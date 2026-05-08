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


BASELINE_SYSTEM_PROMPT = """你是一位顶级海报版式设计师。你需要根据设计简报和素材，直接输出带像素坐标的海报图层 JSON。

⚠️ 重要：你必须为每个元素指定精确的 x, y, width, height 像素值。

━━━━━━━━━━━━━━━━━━━━━━━━━━
一、输出格式
━━━━━━━━━━━━━━━━━━━━━━━━━━
输出 JSON，包含 layers 数组，每个元素带有精确的像素坐标：

{
  "layers": [
    {"type": "image", "x": 0, "y": 0, "width": 1080, "height": 1920, "src": "{ASSET_BG}"},
    {"type": "text", "x": 72, "y": 800, "width": 936, "height": 80, "content": "标题文本", "fontSize": 64, "color": "#FFFFFF", "fontFamily": "PingFang SC", "fontWeight": "bold", "textAlign": "center"},
    {"type": "text", "x": 72, "y": 900, "width": 936, "height": 50, "content": "副标题", "fontSize": 28, "color": "#EEEEEE", "fontFamily": "PingFang SC", "fontWeight": "normal", "textAlign": "center"},
    {"type": "text", "x": 72, "y": 980, "width": 936, "height": 44, "content": "了解更多", "fontSize": 24, "color": "#FFFFFF", "fontFamily": "PingFang SC", "fontWeight": "bold", "textAlign": "center"}
  ]
}

━━━━━━━━━━━━━━━━━━━━━━━━━━
二、布局策略参考
━━━━━━━━━━━━━━━━━━━━━━━━━━
你可以从以下布局思路中选择最适合的一种，并据此确定元素坐标：

- "top_text"       — 上文下图：标题在画布上方（y: 5%~50%），下方留给背景
- "centered"       — 极简居中：大留白，文字垂直居中（y: 25%~75%）
- "bottom_heavy"   — 底部聚集：内容紧凑在底部（y: 55%~95%），上方全给背景
- "left_aligned"   — 杂志通栏：左对齐紧凑排版（x: 5%~60%）
- "diagonal"       — 对角线冲击：标题左上 + CTA右下，视觉张力
- "big_title"      — 大字报：超大标题占据视觉中心
- "split_vertical" — 上下分割：信息分两区

━━━━━━━━━━━━━━━━━━━━━━━━━━
三、设计规则
━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 标题 font_size 建议 48-96，副标题 28-42，正文 18-28，CTA 24-36
2. 【文字颜色】
   - 标题鼓励使用知识图谱推荐的强调色（accent color），前提是与背景有足够对比
   - 副标题可使用主色调的浅色变体或 #FFFFFF
   - 正文和 CTA 优先使用 #FFFFFF 或 #000000 保证可读性
   - 禁止使用与背景同色系的文字（如蓝色背景上用蓝色字）
   - 禁止使用中间灰度（如 #888888）作为标题颜色
3. 所有坐标和尺寸必须是具体的像素值，元素不能溢出画布
4. 画布外边距至少保留 40px
5. 文字图层之间应保持合理的垂直间距（40-80px）
6. 所有文字建议对齐到同一条竖直基准线（左对齐或居中对齐）"""


def run_layout_agent(
    design_brief: Dict[str, Any],
    asset_list: Dict[str, Any],
    canvas_width: int,
    canvas_height: int,
    review_feedback: Optional[Dict[str, Any]] = None,
    style_hint: Optional[str] = None,
    use_dsl: bool = True,
) -> Dict[str, Any]:
    """
    运行 Layout Agent

    Args:
        use_dsl: True=语义DSL+布局引擎（默认），False=LLM直接输出坐标（Baseline消融实验用）
    """
    logger.info(f"📐 Layout Agent 正在规划布局... (use_dsl={use_dsl})")

    if review_feedback and review_feedback.get("status") == "REJECT":
        logger.info(f"📝 收到审核反馈: {review_feedback.get('feedback', '')}")

    try:
        # Baseline 模式：LLM 直接输出坐标，跳过 DSL 和布局引擎
        if not use_dsl:
            return _run_baseline_layout(design_brief, asset_list, canvas_width, canvas_height)

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

        subject_layer = asset_list.get("subject_layer", {})
        subject_size = None
        if subject_layer.get("width") and subject_layer.get("height"):
            subject_size = (subject_layer["width"], subject_layer["height"])

        elements = renderer.parse_dsl_and_build_layout(
            dsl_instructions=dsl_instructions,
            layout_strategy=layout_strategy,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            design_brief=design_brief,
            font_style=font_style,
            subject_size=subject_size,
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


def _run_baseline_layout(
    design_brief: Dict[str, Any],
    asset_list: Dict[str, Any],
    canvas_width: int,
    canvas_height: int,
) -> Dict[str, Any]:
    """
    Baseline 模式：LLM 直接输出带像素坐标的图层 JSON，不经过 DSL 和布局引擎。

    与 DSL 模式共享相同的 user_prompt（包含知识上下文、布局推荐等），
    仅替换 system_prompt 为直接坐标输出格式，确保消融实验的公平性。
    """
    logger.info("📐 [Baseline] LLM 直接输出坐标模式（公平 prompt）")

    # 复用 DSL 模式的 user_prompt 构建（获得相同的知识上下文）
    prompts = layout_prompt.get_prompt(
        design_brief=design_brief,
        asset_list=asset_list,
        canvas_width=canvas_width,
        canvas_height=canvas_height,
    )

    # 替换输出格式要求：DSL 指令 → 直接坐标 JSON
    user_prompt = prompts["user"].replace(
        "请输出完整的 JSON（包含 layout_strategy、font_style、dsl_instructions）。\n"
        "结合上述知识推荐，从 7 种 layout_strategy 中选择最合适的一种。\n"
        "仅输出 JSON，不要包含其他文本。",
        "请直接输出带像素坐标的 layers JSON（不要使用 DSL 指令）。\n"
        "结合上述知识推荐，选择合适的布局思路，为每个元素计算精确的 x, y, width, height。\n"
        "仅输出 JSON，不要包含其他文本。",
    )

    from .base import AgentFactory
    agent = AgentFactory.get_layout_agent()
    response = agent.invoke(contents=f"{BASELINE_SYSTEM_PROMPT}\n\n{user_prompt}")

    if hasattr(response, "text"):
        content = response.text
    elif hasattr(response, "choices") and len(response.choices) > 0:
        content = response.choices[0].message.content
    else:
        raise ValueError(f"Unknown response format: {type(response)}")

    if "```json" in content:
        content = content.replace("```json", "").replace("```", "")
    content = content.strip()

    result = json.loads(content)
    layers = result.get("layers", [])

    # 替换图片占位符
    for layer in layers:
        src = layer.get("src", "")
        if "ASSET_BG" in str(src) and asset_list.get("background_layer"):
            layer["src"] = asset_list["background_layer"].get("src", "")
        elif "ASSET_FG" in str(src) and asset_list.get("subject_layer"):
            layer["src"] = asset_list["subject_layer"].get("src", "")

    # 与 DSL 模式相同的文字颜色后处理（公平消融：后处理不应成为组间差异来源）
    from ..services.renderer.layout_builder import LayoutBuilder
    bg_color = LayoutBuilder._extract_bg_color(layers)
    layers = [LayoutBuilder._ensure_text_contrast(l, bg_color) for l in layers]

    poster_json = {
        "canvas": {
            "width": canvas_width,
            "height": canvas_height,
            "backgroundColor": design_brief.get("background_color", "#FFFFFF"),
        },
        "layers": layers,
        "layout_strategy": "baseline_direct",
    }
    logger.info(f"✅ [Baseline] 生成了 {len(layers)} 个图层")
    return poster_json


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
