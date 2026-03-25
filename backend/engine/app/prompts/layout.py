"""
Layout Agent Prompt - 绝对坐标版式生成

LLM 直接输出每个图层的 x, y, width, height，不依赖自动排版引擎。
"""
import json
from typing import Dict, Any, Optional


SYSTEM_PROMPT = """你是一位顶级海报版式设计师。你需要根据设计简报和素材，为每个图层输出 **精确的像素坐标**。

━━━━━━━━━━━━━━━━━━━━━━━━━━
一、输出格式
━━━━━━━━━━━━━━━━━━━━━━━━━━
输出 JSON，每条指令必须包含 x, y, width, height：

{{
  "layout_style": "版式名称(自由发挥)",
  "font_style": "sans",
  "dsl_instructions": [
    {{
      "command": "add_image",
      "src": "{{ASSET_BG}}",
      "x": 0, "y": 0,
      "width": 1080, "height": 1920,
      "layer_type": "background"
    }},
    {{
      "command": "add_title",
      "content": "标题文本",
      "x": 80, "y": 400,
      "width": 920, "height": 120,
      "font_size": 72,
      "color": "#FFFFFF",
      "text_align": "left"
    }}
  ]
}}

━━━━━━━━━━━━━━━━━━━━━━━━━━
二、字体风格（font_style）
━━━━━━━━━━━━━━━━━━━━━━━━━━
在 JSON 顶层指定 font_style，系统会自动映射到具体字体。可选值：

- "sans"        — 无衬线体（现代、科技、商务）→ 苹方
- "serif"       — 衬线体（优雅、正式、文艺）→ 宋体
- "rounded"     — 圆体（友好、温暖、亲切）→ 圆体
- "handwriting" — 手写体（文艺、个性、轻松）→ 楷体
- "display"     — 展示体（标题醒目、有冲击力）→ 报隶（标题） + 苹方（正文）

根据海报风格和情绪基调选择最匹配的 font_style。

━━━━━━━━━━━━━━━━━━━━━━━━━━
三、可用指令
━━━━━━━━━━━━━━━━━━━━━━━━━━
1. add_image  — 图片图层
   必填: src, x, y, width, height, layer_type("background"|"subject")
   背景图通常 x=0, y=0, width=画布宽, height=画布高（铺满）

2. add_title  — 主标题
   必填: content, x, y, width, height, font_size, color
   可选: text_align(left|center|right)

3. add_subtitle — 副标题
   必填: content, x, y, width, height, font_size, color
   可选: text_align

4. add_text   — 正文
   必填: content, x, y, width, height, font_size, color
   可选: text_align

5. add_cta    — 行动号召
   必填: content, x, y, width, height, font_size, color
   可选: text_align

━━━━━━━━━━━━━━━━━━━━━━━━━━
四、版式灵感（必须多样化）
━━━━━━━━━━━━━━━━━━━━━━━━━━
以下是几种常见版式思路，你应该根据内容和风格 **自由选择或创造**，禁止每次都用同一种：

A. 上文下图型
   标题 + 副标题放在画布上方 1/3，主图（如有）放在下方 2/3

B. 居中对称型
   所有文字垂直居中于画布，上下留白，适合极简风格

C. 底部聚集型
   标题和 CTA 堆叠在画布底部 1/3，上方留给背景视觉

D. 左对齐通栏型
   所有文字左对齐，标题在上、副标题紧跟、CTA 在底，像杂志封面

E. 对角线型
   标题放在左上区域，CTA 放在右下区域，形成视觉对角线

F. 大标题铺满型
   标题字号极大，几乎铺满画布宽度，副标题和 CTA 在角落

G. 上下分割型
   画布上半部分放标题和副标题，下半部分放主体素材和 CTA

━━━━━━━━━━━━━━━━━━━━━━━━━━
五、设计规则
━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 背景图始终铺满画布（x=0, y=0, width=画布宽, height=画布高）
2. 文字不能超出画布边界，必须留至少 40px 安全边距
3. 标题 font_size 建议 48-96，副标题 28-42，正文 18-28，CTA 24-36
4. 确保文字在背景上可读（深色背景 → 浅色字，浅色背景 → 深色字）
5. 如果有主体素材（subject），合理安排其位置和尺寸，不要遮挡主标题
6. height 估算：height ≈ font_size × 行数 × 1.4
7. 每次生成请选择不同的版式思路，保持多样性
8. layout_style 字段必须填写你所选择的版式名称（自由发挥，如"对角线冲击"、"极简居中"等）
"""


USER_PROMPT_TEMPLATE = """【输入】
- 画布尺寸: {canvas_width} × {canvas_height}
- 设计简报:
{design_brief}
- 素材:
{asset_summary}
{knowledge_section}{reference_section}{style_hint_section}{review_feedback_section}
请输出完整的 JSON，包含所有图层的精确坐标。
结合上述知识推荐和灵感库（A-G）自由选择或创造版式，layout_style 填写你选用的版式名称。
仅输出 JSON，不要包含其他文本。"""


# ============================================================================
# Prompt 辅助：从 design_brief 中提取结构化知识
# ============================================================================

def _summarize_assets(asset_list: Dict[str, Any]) -> str:
    """将 asset_list 压缩为 prompt 友好的摘要，避免把巨大 base64 塞进上下文"""
    parts = []
    if asset_list.get("background_layer"):
        bg = asset_list["background_layer"]
        parts.append(f'  背景图: 有 (source: {bg.get("source_type", "unknown")}), 占位符 {{ASSET_BG}}')
    else:
        parts.append("  背景图: 无（将使用纯色背景）")

    if asset_list.get("subject_layer"):
        sl = asset_list["subject_layer"]
        w = sl.get("width", "?")
        h = sl.get("height", "?")
        parts.append(f'  主体素材: 有 ({w}x{h}), 占位符 {{ASSET_FG}}')
    else:
        parts.append("  主体素材: 无")

    if asset_list.get("color_suggestions"):
        cs = asset_list["color_suggestions"]
        parts.append(f'  配色建议: primary={cs.get("primary")}, text={cs.get("text_color")}')

    return "\n".join(parts)


def _summarize_knowledge(design_brief: Dict[str, Any]) -> str:
    """从 design_brief 提取 KG 推理结果，格式化为 LLM 可直接消费的布局指导"""
    kg = design_brief.get("kg_rules")
    if not kg:
        return ""

    parts = ["【知识图谱布局推荐 — 请优先参考】"]

    layout_patterns = kg.get("layout_patterns", [])
    layout_strategies = kg.get("layout_strategies", [])
    layout_intents = kg.get("layout_intents", [])
    emotions = kg.get("emotions", [])
    avoid = kg.get("avoid", [])
    typography_styles = kg.get("typography_styles", [])
    typography_weights = kg.get("typography_weights", [])

    if emotions:
        parts.append(f"- 情绪基调: {', '.join(emotions)}")
    if layout_strategies:
        parts.append(f"- 推荐布局策略: {', '.join(layout_strategies)}")
    if layout_patterns:
        parts.append(f"- 推荐布局模式: {', '.join(layout_patterns)}")
    if layout_intents:
        parts.append(f"- 布局意图: {', '.join(layout_intents)}")
    if typography_styles:
        parts.append(f"- 字体风格: {', '.join(typography_styles)}")
    if typography_weights:
        parts.append(f"- 字重: {', '.join(typography_weights)}")
    if avoid:
        parts.append(f"- 应避免: {', '.join(avoid)}")

    if len(parts) == 1:
        return ""

    parts.append("")
    return "\n".join(parts) + "\n"


def _summarize_reference(design_brief: Dict[str, Any]) -> str:
    """从 design_brief 提取风格参考图分析结果，格式化为布局指导"""
    has_ref = any(
        design_brief.get(k)
        for k in ("reference_mood", "reference_theme", "reference_description",
                   "reference_layout_hints", "reference_palette", "reference_color_scheme")
    )
    if not has_ref:
        return ""

    parts = ["【风格参考图分析 — 请参考以下风格进行设计】"]

    mood = design_brief.get("reference_mood")
    theme = design_brief.get("reference_theme")
    desc = design_brief.get("reference_description")
    layout_hints = design_brief.get("reference_layout_hints", {})
    palette = design_brief.get("reference_palette", [])
    color_scheme = design_brief.get("reference_color_scheme")

    if desc:
        parts.append(f"- 参考图描述: {desc}")
    if mood:
        parts.append(f"- 情感基调: {mood}")
    if theme:
        parts.append(f"- 主题: {theme}")
    if palette:
        parts.append(f"- 参考配色: {', '.join(palette[:6])}")
    if color_scheme:
        parts.append(f"- 配色方案建议: {color_scheme}")
    if layout_hints:
        text_pos = layout_hints.get("text_position")
        text_color = layout_hints.get("text_color_suggestion")
        if text_pos:
            parts.append(f"- 建议文字位置: {text_pos}")
        if text_color:
            parts.append(f"- 建议文字颜色: {text_color}")

    if len(parts) == 1:
        return ""

    parts.append("")
    return "\n".join(parts) + "\n"


# ============================================================================
# Prompt 构建入口
# ============================================================================

def get_prompt(
    design_brief: Dict[str, Any],
    asset_list: Dict[str, Any],
    canvas_width: int,
    canvas_height: int,
    review_feedback: Optional[Dict[str, Any]] = None,
    style_hint: Optional[str] = None,
) -> Dict[str, str]:
    """
    构建 Layout Agent 的 prompt

    Args:
        style_hint: 多样性引导（如 "请尝试 E. 对角线型 风格"），用于并行生成时避免雷同

    Returns:
        {"system": ..., "user": ...}
    """
    review_feedback_section = ""
    if review_feedback and review_feedback.get("status") == "REJECT":
        issues = review_feedback.get("issues", [])
        issues_text = "\n".join([f"  - {issue}" for issue in issues]) if issues else ""
        review_feedback_section = f"""
【⚠️ 审核反馈 — 必须修正以下问题】
审核意见: {review_feedback.get('feedback', '')}
具体问题:
{issues_text}

你可以且应该同时调整：坐标/尺寸、文字颜色(color)、字号(font_size)、文字内容。
特别注意：如果反馈提到「文字可读性」或「颜色接近」，你必须更换文字颜色使其与背景形成强对比（深色背景用白色/浅色字，浅色背景用黑色/深色字）。"""

    style_hint_section = ""
    if style_hint:
        style_hint_section = f"【版式偏好】\n{style_hint}\n\n"

    brief_for_prompt = {
        k: v
        for k, v in design_brief.items()
        if k not in ("kg_rules", "brand_knowledge", "decision_trace", "design_source")
        and not (isinstance(v, str) and len(v) > 500)
    }

    user_prompt = USER_PROMPT_TEMPLATE.format(
        design_brief=json.dumps(brief_for_prompt, ensure_ascii=False, indent=2),
        asset_summary=_summarize_assets(asset_list or {}),
        knowledge_section=_summarize_knowledge(design_brief),
        reference_section=_summarize_reference(design_brief),
        style_hint_section=style_hint_section,
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        review_feedback_section=review_feedback_section,
    )

    return {
        "system": SYSTEM_PROMPT,
        "user": user_prompt,
    }
