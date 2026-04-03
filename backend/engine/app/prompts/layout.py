"""
Layout Agent Prompt — 语义 DSL 版式生成

LLM 输出语义 DSL 指令（无坐标），OOP 布局引擎根据 layout_strategy 自动计算坐标。
"""
import json
from typing import Dict, Any, Optional


SYSTEM_PROMPT = """你是一位顶级海报版式设计师。你需要根据设计简报和素材，输出**语义化的 DSL 指令**。

⚠️ 重要：你不需要指定任何坐标（x, y, width, height）。系统的 OOP 布局引擎会根据你选择的 layout_strategy 自动计算所有元素的精确位置。

━━━━━━━━━━━━━━━━━━━━━━━━━━
一、输出格式
━━━━━━━━━━━━━━━━━━━━━━━━━━
输出 JSON，包含 layout_strategy、font_style 和 dsl_instructions：

{
  "layout_strategy": "bottom_heavy",
  "font_style": "sans",
  "dsl_instructions": [
    {"command": "add_image", "src": "{ASSET_BG}", "layer_type": "background"},
    {"command": "add_overlay"},
    {"command": "add_title", "content": "标题文本", "font_size": 64, "color": "#FFFFFF"},
    {"command": "add_subtitle", "content": "副标题", "font_size": 28, "color": "#EEEEEE"},
    {"command": "add_divider"},
    {"command": "add_cta", "content": "了解更多", "font_size": 24, "color": "#FFFFFF"}
  ]
}

━━━━━━━━━━━━━━━━━━━━━━━━━━
二、布局策略（layout_strategy）—— 必选
━━━━━━━━━━━━━━━━━━━━━━━━━━
从以下 7 种策略中选择最适合的一种。布局引擎会自动将元素放置到对应区域：

- "top_text"       — 上文下图型：标题+副标题放在画布上方，下方留给背景视觉
- "centered"       — 居中对称型：所有文字垂直居中于画布，上下留白，适合极简风格
- "bottom_heavy"   — 底部聚集型：标题和 CTA 堆叠在画布底部，上方留给背景视觉
- "left_aligned"   — 左对齐通栏型：所有文字左对齐，从上到下铺开，像杂志封面
- "diagonal"       — 对角线型：标题放在左上区域，CTA 放在右下区域，形成视觉对角线
- "big_title"      — 大标题铺满型：标题字号放大 1.5x，居中展示，副标题和 CTA 紧跟
- "split_vertical" — 上下分割型：画布上半部分放标题和副标题，下半部分放 CTA

每次生成请选择不同的策略，保持多样性。

━━━━━━━━━━━━━━━━━━━━━━━━━━
三、字体风格（font_style）
━━━━━━━━━━━━━━━━━━━━━━━━━━
在 JSON 顶层指定 font_style，系统会自动映射到具体字体。可选值：

- "sans"        — 无衬线体（现代、科技、商务）
- "serif"       — 衬线体（优雅、正式、文艺）
- "rounded"     — 圆体（友好、温暖、亲切）
- "handwriting" — 手写体（文艺、个性、轻松）
- "display"     — 展示体（标题醒目、有冲击力）

根据海报风格和情绪基调选择最匹配的 font_style。

━━━━━━━━━━━━━━━━━━━━━━━━━━
四、可用指令（无需坐标）
━━━━━━━━━━━━━━━━━━━━━━━━━━
1. add_image  — 图片图层
   必填: src, layer_type("background"|"subject")
   背景图始终铺满画布，主体素材由布局引擎自动定位

2. add_title  — 主标题
   必填: content, font_size, color
   可选: text_align(left|center|right), font_weight(normal|bold)

3. add_subtitle — 副标题
   必填: content, font_size, color
   可选: text_align, font_weight

4. add_text   — 正文
   必填: content, font_size, color
   可选: text_align, font_weight

5. add_cta    — 行动号召
   必填: content, font_size, color
   可选: text_align, font_weight

6. add_divider — 分隔线（装饰性水平线条）
   可选: width_ratio(0.0~1.0, 默认 0.5), color
   注意: 粗细和样式由系统根据风格自动决定

7. add_overlay — 渐变遮罩（提升文字可读性）
   无需任何参数，系统根据布局策略自动确定覆盖区域和方向

8. add_shape  — 装饰形状（色块、标签背景等）
   可选: width_ratio(0.0~1.0), height(px), color, border_radius, opacity, subtype
   注意: 默认填充色和圆角由系统根据风格自动决定

━━━━━━━━━━━━━━━━━━━━━━━━━━
五、设计规则
━━━━━━━━━━━━━━━━━━━━━━━━━━
1. dsl_instructions 中元素的顺序决定了视觉从上到下的排列顺序
2. 标题 font_size 建议 48-96，副标题 28-42，正文 18-28，CTA 24-36
3. 【文字颜色 — 极其重要！】
   - 绝大多数情况下使用 **#FFFFFF（纯白）** 或 **#000000（纯黑）**
   - 如果背景整体偏暗 → 文字用 #FFFFFF
   - 如果背景整体偏亮 → 文字用 #000000 或 #1A1A1A
   - 禁止使用中间灰度（如 #888888）作为标题颜色
   - 如果不确定，一律用 #FFFFFF
4. 善用 add_overlay 提升文字在背景图上的可读性
5. 每次生成请选择不同的 layout_strategy，保持多样性
"""


USER_PROMPT_TEMPLATE = """【输入】
- 画布尺寸: {canvas_width} × {canvas_height}
- 设计简报:
{design_brief}
- 素材:
{asset_summary}
{knowledge_section}{reference_section}{style_hint_section}{review_feedback_section}
请输出完整的 JSON（包含 layout_strategy、font_style、dsl_instructions）。
结合上述知识推荐，从 7 种 layout_strategy 中选择最合适的一种。
仅输出 JSON，不要包含其他文本。"""


# ============================================================================
# Prompt 辅助：从 design_brief 中提取结构化知识
# ============================================================================

def _summarize_assets(asset_list: Dict[str, Any]) -> str:
    """将 asset_list 压缩为 prompt 友好的摘要"""
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

    analyses = asset_list.get("image_analyses", [])
    for item in analyses:
        img_type = item.get("type", "unknown")
        analysis = item.get("analysis", {})
        understanding = analysis.get("understanding", {})
        if not understanding:
            continue

        desc = understanding.get("description")
        theme = understanding.get("theme")
        mood = understanding.get("mood")
        elements = understanding.get("elements", [])
        layout_hints = understanding.get("layout_hints", {})

        tag = "背景图" if img_type == "background" else "主体素材"
        detail_parts = []
        if desc:
            detail_parts.append(f"内容: {desc}")
        if theme and theme != "其他":
            detail_parts.append(f"主题: {theme}")
        if mood and mood != "其他":
            detail_parts.append(f"情绪: {mood}")
        if elements:
            detail_parts.append(f"元素: {', '.join(elements[:5])}")
        if layout_hints.get("text_position"):
            detail_parts.append(f"建议文字区域: {layout_hints['text_position']}")
        if layout_hints.get("text_color_suggestion"):
            detail_parts.append(f"建议文字颜色: {layout_hints['text_color_suggestion']}")

        if detail_parts:
            parts.append(f'  [{tag}图像分析] {"; ".join(detail_parts)}')

    return "\n".join(parts)


def _summarize_knowledge(design_brief: Dict[str, Any]) -> str:
    """从 design_brief 提取 KG 推理结果，格式化为 LLM 可直接消费的布局指导"""
    kg = design_brief.get("kg_rules")
    if not kg:
        return ""

    parts = ["【知识图谱布局推荐 — 请优先参考】"]

    _fields = [
        ("emotions", "情绪基调"),
        ("color_strategies", "配色策略"),
        ("layout_strategies", "推荐布局策略"),
        ("layout_patterns", "推荐布局模式"),
        ("layout_intents", "布局意图"),
        ("typography_styles", "字体风格"),
        ("typography_weights", "字重"),
        ("typography_characteristics", "排版特征"),
        ("design_principles", "设计原则"),
        ("avoid", "应避免"),
    ]

    for field_key, label in _fields:
        values = kg.get(field_key, [])
        if values:
            parts.append(f"- {label}: {', '.join(values)}")

    palettes = kg.get("color_palettes", {})
    if palettes.get("primary"):
        parts.append(f"- 推荐主色: {', '.join(palettes['primary'][:4])}")
    if palettes.get("accent"):
        parts.append(f"- 推荐强调色: {', '.join(palettes['accent'][:3])}")

    decorations = kg.get("decoration_styles", {})
    if decorations:
        types_available = [k for k in ("divider", "overlay", "shape") if k in decorations]
        if types_available:
            parts.append(f"- 可用装饰类型: {', '.join(types_available)}")

    if len(parts) == 1:
        return ""

    parts.append("")
    return "\n".join(parts) + "\n"


def _summarize_reference(design_brief: Dict[str, Any]) -> str:
    """从 design_brief 提取风格参考图分析结果"""
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
        style_hint: 多样性引导（如 "请尝试 diagonal 风格"），用于并行生成时避免雷同
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

你可以且应该同时调整：layout_strategy、font_style、文字颜色(color)、字号(font_size)、文字内容、元素顺序。
特别注意：如果反馈提到「文字可读性」或「颜色接近」，直接将所有文字颜色改为 #FFFFFF（白色）或 #000000（黑色）。"""

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
