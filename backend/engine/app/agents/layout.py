"""
Layout Agent - 空间计算与排版

使用 DSL 模式：
- LLM 输出 DSL 指令
- RendererService 解析 DSL，使用 OOP 布局引擎生成布局
- 动态计算元素位置，支持文本高度自适应

Author: VibePoster Team
Date: 2025-01
"""

import json
from typing import Dict, Any, Optional
from ..core.config import settings, ERROR_FALLBACKS
from ..core.llm import LLMClientFactory
from ..core.logger import get_logger
from ..prompts import layout as layout_prompt
from ..services.renderer import RendererService
from .base import BaseAgent

logger = get_logger(__name__)


class LayoutAgent(BaseAgent):
    """Layout Agent 实现类"""

    def _create_client(self):
        return LLMClientFactory.get_client(
            provider=self.config.get("provider", "gemini"),
            api_key=self.config.get("api_key"),
            base_url=self.config.get("base_url"),
        )

    def invoke(self, contents: str, **kwargs) -> Dict[str, Any]:
        """调用 Layout Agent"""
        provider = self.config.get("provider", "gemini").lower()

        if provider == "gemini":
            # Gemini 客户端调用
            from google.genai import types

            if not hasattr(self.client, "models"):
                raise ValueError(f"Gemini Client {type(self.client)} does not have 'models' attribute")

            models = self.client.models
            if not hasattr(models, "generate_content"):
                raise ValueError(f"Gemini Models object {type(models)} does not have 'generate_content' method")

            response = models.generate_content(
                model=self.config["model"],
                contents=contents,
                config=types.GenerateContentConfig(response_mime_type=self.config["response_mime_type"]),
                **kwargs,
            )
            return response
        else:
            # OpenAI 兼容接口调用
            from openai import OpenAI

            if not isinstance(self.client, OpenAI):
                raise ValueError(f"Expected OpenAI client, got {type(self.client)}")

            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=[{"role": "user", "content": contents}],
                temperature=self.config.get("temperature", 0.1),
                response_format=(
                    {"type": "json_object"} if self.config.get("response_mime_type") == "application/json" else None
                ),
                **kwargs,
            )
            return response


def run_layout_agent(
    design_brief: Dict[str, Any],
    asset_list: Dict[str, Any],
    canvas_width: int,
    canvas_height: int,
    review_feedback: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    运行 Layout Agent（DSL 模式）
    
    流程：
    1. LLM 输出 DSL 指令列表
    2. RendererService 解析 DSL
    3. OOP 布局引擎计算布局
    4. 转换为 Pydantic Schema
    
    Args:
        design_brief: 设计简报
        asset_list: 资产列表
        canvas_width: 画布宽度
        canvas_height: 画布高度
        review_feedback: 审核反馈（可选）
    
    Returns:
        海报 JSON 数据
    """
    logger.info("📐 Layout Agent 正在规划布局...")
    
    if review_feedback and review_feedback.get("status") == "REJECT":
        logger.info(f"📝 收到审核反馈: {review_feedback.get('feedback', '')}")
    
    try:
        # 1. 生成 DSL Prompt
        prompts = layout_prompt.get_prompt(
            design_brief=design_brief,
            asset_list=asset_list,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            review_feedback=review_feedback
        )
        
        # 2. 调用 LLM 获取 DSL 指令
        from .base import AgentFactory
        agent = AgentFactory.get_layout_agent()
        
        logger.debug(f"📤 发送 DSL Prompt 到 LLM...")
        response = agent.invoke(contents=f"{prompts['system']}\n\n{prompts['user']}")
        
        # 3. 解析 LLM 响应
        if hasattr(response, "text"):
            content = response.text
        elif hasattr(response, "choices") and len(response.choices) > 0:
            content = response.choices[0].message.content
        else:
            raise ValueError(f"Unknown response format: {type(response)}")
        
        # 清理 markdown 标记
        if "```json" in content:
            content = content.replace("```json", "").replace("```", "")
        content = content.strip()
        
        # 解析 JSON
        dsl_response = json.loads(content)
        dsl_instructions = dsl_response.get("dsl_instructions", [])
        
        logger.info(f"📋 收到 {len(dsl_instructions)} 条 DSL 指令")
        for i, instr in enumerate(dsl_instructions[:5]):  # 只打印前 5 条
            logger.debug(f"  [{i+1}] {instr.get('command')}: {str(instr)[:50]}...")
        
        # 4. 替换图片 src 占位符
        for instr in dsl_instructions:
            if instr.get("command") == "add_image":
                src = instr.get("src", "")
                layer_type = instr.get("layer_type", "background")
                
                if "ASSET_BG" in src or layer_type == "background":
                    if asset_list.get("background_layer"):
                        instr["src"] = asset_list["background_layer"].get("src", "")
                elif "ASSET_FG" in src or layer_type == "foreground":
                    if asset_list.get("foreground_layer"):
                        instr["src"] = asset_list["foreground_layer"].get("src", "")
        
        # 5. 使用 RendererService 构建布局
        renderer = RendererService()
        
        container = renderer.parse_dsl_and_build_layout(
            dsl_instructions=dsl_instructions,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            design_brief=design_brief
        )
        
        # 6. 转换为 Pydantic Schema
        poster_data = renderer.convert_to_pydantic_schema(
            container=container,
            design_brief=design_brief
        )
        
        # 7. 合并素材数据
        poster_data = renderer.merge_with_design_brief(
            poster_data=poster_data,
            design_brief=design_brief,
            asset_list=asset_list
        )
        
        # 8. 转换为字典格式返回
        poster_json = poster_data.model_dump()
        
        logger.info(f"✅ Layout 完成，生成了 {len(poster_json.get('layers', []))} 个图层")
        return poster_json
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ DSL JSON 解析失败: {e}")
        return ERROR_FALLBACKS["layout"]
    except Exception as e:
        logger.error(f"❌ Layout Error: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"   堆栈:\n{traceback.format_exc()}")
        return ERROR_FALLBACKS["layout"]


def layout_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Layout Agent 工作流节点

    Args:
        state: 工作流状态

    Returns:
        更新后的状态
    """
    design_brief = state.get("design_brief", {})
    asset_list = state.get("asset_list", {})
    review_feedback = state.get("review_feedback")

    canvas_width = state.get("canvas_width", settings.canvas.WIDTH)
    canvas_height = state.get("canvas_height", settings.canvas.HEIGHT)

    final_poster = run_layout_agent(
        design_brief=design_brief,
        asset_list=asset_list,
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        review_feedback=review_feedback,
    )

    return {"final_poster": final_poster}
