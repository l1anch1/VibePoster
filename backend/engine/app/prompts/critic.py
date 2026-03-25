"""
Critic Agent Prompt - 海报质量审核（双路审核）

Path 1: JSON 结构审核 - 基于数据检查布局结构问题
Path 2: 视觉审核 - 基于渲染图片检查视觉质量问题
"""
import json
from typing import Dict, Any, Optional


# =============================================================================
# Path 1: JSON 结构审核
# =============================================================================

SYSTEM_PROMPT = """
你是一个海报质量审核员。检查生成的海报数据是否存在问题。

【图层叠放规则 — 非常重要！】
layers 数组中：
  - index 0 = 最底层（最先绘制，会被上面的图层遮挡）
  - index 越大 = 越靠上（越后绘制，会遮挡下面的图层）
因此：如果背景图在 index 0，而文字在 index 1、2、3，文字就在图片上方，不会被遮挡——这是正确的结构。
只有当文字的 index 小于图片的 index 时，文字才会被图片遮挡。

【REJECT 标准】
仅当存在明确的严重问题时才 REJECT（宁可放过，不可误杀）：
- 文字 index < 图片 index，导致文字被图片完全遮挡
- 文字严重溢出画布（x + width > canvas.width + 100 或 y + height > canvas.height + 100）
- 图层尺寸无效（width <= 0 或 height <= 0）

【不应 REJECT 的情况】
- 背景图在 index 0 + 文字在更高 index → 正常，不是遮挡
- 配色偏好（颜色搭配是主观判断）
- 文字略微超出画布边缘（容差 100px 以内）

【输出格式】
请输出 JSON：
{{
    "status": "PASS" | "REJECT",
    "feedback": "审核意见",
    "issues": []
}}
"""

USER_PROMPT_TEMPLATE = """
【输入】
海报数据（layers[0] = 最底层，index 越大越靠上；文字 index > 图片 index 则文字可见，不算遮挡）:
{poster_data}
{intent_section}
请审核，输出 JSON 结果。
"""


# =============================================================================
# Path 2: 视觉审核（基于渲染后的图片）
# =============================================================================

VISUAL_SYSTEM_PROMPT = """
你是一位专业的平面设计审核员。你将看到一张由系统自动生成的海报图片，请从视觉角度判断它是否存在问题。

【审核原则】
- 只关注视觉缺陷，不追求完美。
- 存在视觉缺陷时 REJECT，否则 PASS。

【检查项】
1. 文字可读性：文字是否因颜色与背景颜色过于接近而几乎无法辨认？
2. 视觉遮挡：核心文字内容是否被图片或其他元素严重遮挡？
3. 排版合理性：是否存在文字大面积溢出画布、严重重叠等排版错误？
4. 整体完整性：海报是否看起来残缺或渲染异常（如大片空白、图片加载失败的占位符等）？

【不需要检查的内容】
- 配色是否"好看" —— 风格偏好因人而异
- 字体选择 —— 不在审核范围内
- 创意水平 —— 不在审核范围内

【输出格式】
请输出 JSON：
{{
    "status": "PASS" | "REJECT",
    "feedback": "视觉审核意见",
    "issues": []
}}
"""

VISUAL_USER_PROMPT = "请审核这张海报图片，按照检查项判断是否存在视觉问题，输出 JSON 结果。"


# =============================================================================
# Prompt 构造函数
# =============================================================================

def _summarize_intent(design_brief: Optional[Dict[str, Any]]) -> str:
    """从 design_brief 提取设计意图摘要，供 Critic 参考"""
    if not design_brief:
        return ""
    parts = []
    title = design_brief.get("title")
    intent = design_brief.get("intent")
    style_kw = design_brief.get("style_keywords", [])
    main_color = design_brief.get("main_color")
    if title:
        parts.append(f"- 预期标题: {title}")
    if intent:
        parts.append(f"- 海报意图: {intent}")
    if style_kw:
        parts.append(f"- 风格关键词: {', '.join(style_kw[:5])}")
    if main_color:
        parts.append(f"- 主色调: {main_color}")
    if not parts:
        return ""
    return "\n【设计意图（参考）】\n" + "\n".join(parts) + "\n"


def get_prompt(
    poster_data: Dict[str, Any],
    design_brief: Optional[Dict[str, Any]] = None,
) -> Dict[str, str]:
    """
    获取 Path 1（JSON 结构审核）的 prompt。

    Args:
        poster_data: 海报数据
        design_brief: 设计简报（可选，用于语义对照）

    Returns:
        包含 system 和 user prompt 的字典
    """
    return {
        "system": SYSTEM_PROMPT,
        "user": USER_PROMPT_TEMPLATE.format(
            poster_data=json.dumps(poster_data, ensure_ascii=False, indent=2),
            intent_section=_summarize_intent(design_brief),
        ),
    }


def get_visual_prompt() -> Dict[str, str]:
    """
    获取 Path 2（视觉审核）的 prompt。

    Returns:
        包含 system 和 user prompt 的字典
    """
    return {
        "system": VISUAL_SYSTEM_PROMPT,
        "user": VISUAL_USER_PROMPT,
    }

