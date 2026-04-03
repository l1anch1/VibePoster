"""
Layout Agent - 语义 DSL 生成 + OOP 布局引擎

流程：
    1. LLM 输出语义 DSL 指令（无坐标）+ layout_strategy
    2. OOP 布局引擎根据 strategy 动态计算所有元素坐标
    3. 转换为 Pydantic Schema
"""

import json
from typing import Dict, Any, Optional
from ..core.config import settings, ERROR_FALLBACKS
from ..core.llm import LLMClientFactory
from ..core.logger import get_logger
from ..prompts import layout as layout_prompt
from ..services.renderer import RendererService, VALID_STRATEGIES
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
    style_hint: Optional[str] = None,
) -> Dict[str, Any]:
    """
    运行 Layout Agent（语义 DSL + OOP 布局引擎）

    流程：
    1. LLM 输出语义 DSL 指令（无坐标）+ layout_strategy
    2. 替换图片占位符
    3. OOP 布局引擎根据 strategy 计算所有坐标
    4. 转换为 Pydantic Schema
    """
    logger.info("📐 Layout Agent 正在规划布局...")

    if review_feedback and review_feedback.get("status") == "REJECT":
        logger.info(f"📝 收到审核反馈: {review_feedback.get('feedback', '')}")

    try:
        # 1. 生成 Prompt
        prompts = layout_prompt.get_prompt(
            design_brief=design_brief,
            asset_list=asset_list,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            review_feedback=review_feedback,
            style_hint=style_hint,
        )

        # 2. 调用 LLM
        from .base import AgentFactory
        agent = AgentFactory.get_layout_agent()

        logger.debug("📤 发送语义 DSL Prompt 到 LLM...")
        response = agent.invoke(contents=f"{prompts['system']}\n\n{prompts['user']}")

        # 3. 解析 LLM 响应
        if hasattr(response, "text"):
            content = response.text
        elif hasattr(response, "choices") and len(response.choices) > 0:
            content = response.choices[0].message.content
        else:
            raise ValueError(f"Unknown response format: {type(response)}")

        if "```json" in content:
            content = content.replace("```json", "").replace("```", "")
        content = content.strip()

        dsl_response = json.loads(content)
        dsl_instructions = dsl_response.get("dsl_instructions", [])

        # 4. 提取 layout_strategy 和 font_style
        layout_strategy = dsl_response.get("layout_strategy", "centered")
        if layout_strategy not in VALID_STRATEGIES:
            logger.warning(
                f"⚠️ LLM 返回了无效的 layout_strategy: '{layout_strategy}'，回退到 centered"
            )
            layout_strategy = "centered"

        font_style = dsl_response.get("font_style")

        logger.info(
            f"📋 收到 {len(dsl_instructions)} 条语义 DSL 指令, "
            f"strategy={layout_strategy}, font_style={font_style}"
        )

        # 5. 替换图片 src 占位符
        for instr in dsl_instructions:
            if instr.get("command") == "add_image":
                src = instr.get("src", "")
                layer_type = instr.get("layer_type", "background")

                if "ASSET_BG" in src or layer_type == "background":
                    if asset_list.get("background_layer"):
                        instr["src"] = asset_list["background_layer"].get("src", "")
                elif "ASSET_FG" in src or layer_type == "subject":
                    if asset_list.get("subject_layer"):
                        instr["src"] = asset_list["subject_layer"].get("src", "")

        # 6. OOP 布局引擎计算坐标
        renderer = RendererService()

        elements = renderer.parse_dsl_and_build_layout(
            dsl_instructions=dsl_instructions,
            layout_strategy=layout_strategy,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            design_brief=design_brief,
            font_style=font_style,
        )

        # 7. 转换为 Pydantic Schema
        poster_data = renderer.convert_to_pydantic_schema(
            elements=elements,
            design_brief=design_brief,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
        )

        # 8. 合并素材数据
        poster_data = renderer.merge_with_design_brief(
            poster_data=poster_data,
            design_brief=design_brief,
            asset_list=asset_list,
        )

        # 9. 输出
        poster_json = poster_data.model_dump()
        poster_json["layout_strategy"] = layout_strategy

        layout_style = dsl_response.get("layout_style")
        if layout_style:
            poster_json["layout_style"] = layout_style

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
    """Layout Agent 工作流节点"""
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
