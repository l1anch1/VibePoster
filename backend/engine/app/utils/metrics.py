"""
海报质量自动化评估指标

用于消融实验和系统测试，提供六个可量化的评估维度：
1. 文字可读性（WCAG 对比度）
2. 布局合理性（溢出/无效尺寸检测）
3. 风格一致性（主色调与 KG 推荐的匹配度）
4. 文字重叠率（文字图层间的矩形交叉面积占比）
5. 间距均匀性（相邻文字图层垂直间距的变异系数）
6. 对齐一致性（文字图层落在对齐线上的集中程度）
"""

import math
import re
import statistics
from typing import Any, Dict, List, Optional


def _hex_to_rgb(hex_color: str) -> tuple:
    """#RRGGBB 或 #RGB 转为 (r, g, b)"""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = h[0]*2 + h[1]*2 + h[2]*2
    if len(h) < 6:
        return (0, 0, 0)
    try:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    except ValueError:
        return (0, 0, 0)


def _relative_luminance(r: int, g: int, b: int) -> float:
    """WCAG 2.0 相对亮度计算"""
    def linearize(c):
        s = c / 255.0
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4
    return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)


def _contrast_ratio(color1: str, color2: str) -> float:
    """计算两个十六进制颜色的 WCAG 对比度（1:1 到 21:1）"""
    r1, g1, b1 = _hex_to_rgb(color1)
    r2, g2, b2 = _hex_to_rgb(color2)
    l1 = _relative_luminance(r1, g1, b1)
    l2 = _relative_luminance(r2, g2, b2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def _color_distance(c1: str, c2: str) -> float:
    """简单的欧氏 RGB 色差（0~441.67）"""
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    return math.sqrt((r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2)


def _extract_placeholder_color(url: str) -> Optional[str]:
    """从 placehold.co URL 中提取背景色（格式: .../WxH/RRGGBB/...）"""
    m = re.search(r"placehold\.co/\d+x\d+/([0-9A-Fa-f]{6})", url)
    if m:
        return f"#{m.group(1).upper()}"
    return None


def _get_bg_color(poster_data: Dict[str, Any]) -> str:
    """
    获取海报中文字实际所在的有效背景色（overlay 感知）。

    优先级：
    1. 不透明度 >= 0.5 的 overlay 层（含 gradient）→ 取其主色
    2. 背景图 placeholder URL 中提取的颜色
    3. canvas.backgroundColor
    4. 回退 #333333
    """
    layers = poster_data.get("layers", [])
    image_color = None
    overlay_color = None

    for layer in layers:
        # 提取背景图颜色
        if layer.get("type") == "image" and image_color is None:
            src = layer.get("src", "")
            extracted = _extract_placeholder_color(src)
            if extracted:
                image_color = extracted

        # 检测 overlay（含 gradient），与 layout_builder._extract_bg_color 逻辑一致
        if (layer.get("type") == "rect"
                and layer.get("subtype") == "overlay"
                and layer.get("opacity", 1.0) >= 0.5):
            bg = layer.get("backgroundColor", "")
            if bg and bg != "transparent":
                overlay_color = bg
            elif layer.get("gradient"):
                gm = re.search(r"#([0-9A-Fa-f]{6})", layer["gradient"])
                if gm:
                    overlay_color = f"#{gm.group(1).upper()}"

    # 优先返回 overlay 色（文字实际叠在 overlay 之上）
    if overlay_color:
        return overlay_color
    if image_color:
        return image_color

    canvas = poster_data.get("canvas", {})
    bg = canvas.get("backgroundColor", "")
    if bg and bg.upper() not in ("#FFFFFF", "#FFF"):
        return bg
    return "#333333"


# ============================================================================
# 指标 1：文字可读性
# ============================================================================

def calc_text_readability(poster_data: Dict[str, Any]) -> float:
    """
    计算海报中所有文字图层与背景色的 WCAG 对比度，返回最小值。

    WCAG AA 标准：普通文字 >= 4.5，大号文字 >= 3.0。
    返回值范围 1.0 ~ 21.0，越高越好。无文字图层时返回 0.0。
    """
    layers = poster_data.get("layers", [])
    bg_color = _get_bg_color(poster_data)

    text_layers = [l for l in layers if l.get("type") == "text"]
    if not text_layers:
        return 0.0

    min_contrast = 21.0
    for layer in text_layers:
        text_color = layer.get("color", "#000000")
        if not text_color or text_color == "transparent":
            text_color = "#000000"
        ratio = _contrast_ratio(text_color, bg_color)
        min_contrast = min(min_contrast, ratio)

    return round(min_contrast, 2)


# ============================================================================
# 指标 2：布局合理性
# ============================================================================

def calc_layout_validity(poster_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    检查布局结构问题，返回各项统计和综合得分。

    返回:
        {
            "overflow_count": 溢出画布的文字图层数,
            "invalid_size_count": 尺寸无效的图层数,
            "has_text": 是否包含文字图层,
            "total_layers": 总图层数,
            "score": 0.0~1.0 综合得分（1.0 为完美）
        }
    """
    canvas = poster_data.get("canvas", {})
    cw = canvas.get("width", 1080)
    ch = canvas.get("height", 1920)
    layers = poster_data.get("layers", [])

    overflow_count = 0
    invalid_size_count = 0
    has_text = False

    for layer in layers:
        w = layer.get("width", 0)
        h = layer.get("height", 0)

        if w <= 0 or h <= 0:
            invalid_size_count += 1

        if layer.get("type") == "text":
            has_text = True
            x = layer.get("x", 0)
            y = layer.get("y", 0)
            # 溢出容差 80px（与 _quick_validate_layout 一致）
            if x + w > cw + 80 or y + h > ch + 80:
                overflow_count += 1
            if x < -40 or y < -40:
                overflow_count += 1

    penalty = (overflow_count + invalid_size_count) * 0.2
    score = max(0.0, min(1.0, 1.0 - penalty))
    if not has_text:
        score = 0.0

    return {
        "overflow_count": overflow_count,
        "invalid_size_count": invalid_size_count,
        "has_text": has_text,
        "total_layers": len(layers),
        "score": round(score, 2),
    }


# ============================================================================
# 指标 3：风格一致性
# ============================================================================

def calc_style_consistency(
    poster_data: Dict[str, Any],
    design_brief: Optional[Dict[str, Any]] = None,
) -> float:
    """
    检查海报主色调与 KG 推荐的 primary 色的匹配度。

    返回 0.0~1.0，完全匹配为 1.0。无 KG 推荐时返回 -1.0（不适用）。
    """
    if not design_brief:
        return -1.0

    kg_rules = design_brief.get("kg_rules") or {}
    palettes = kg_rules.get("color_palettes") or {}
    primary_colors = palettes.get("primary", [])

    if not primary_colors:
        return -1.0

    kg_primary = primary_colors[0]

    # 从海报中提取实际使用的主色调
    poster_main_color = design_brief.get("main_color", "")
    if not poster_main_color:
        # 回退：从文字图层中找最常用的颜色
        layers = poster_data.get("layers", [])
        colors = [l.get("color", "") for l in layers if l.get("type") == "text" and l.get("color")]
        if colors:
            poster_main_color = colors[0]

    if not poster_main_color:
        return 0.0

    distance = _color_distance(kg_primary, poster_main_color)
    # 最大 RGB 距离约 441.67，归一化后反转
    score = max(0.0, 1.0 - distance / 441.67)
    return round(score, 2)


# ============================================================================
# 指标 4：文字重叠率
# ============================================================================

def _rect_overlap_area(r1: Dict, r2: Dict) -> float:
    """计算两个矩形的交叉面积"""
    x_overlap = max(0, min(r1["x"] + r1["w"], r2["x"] + r2["w"]) - max(r1["x"], r2["x"]))
    y_overlap = max(0, min(r1["y"] + r1["h"], r2["y"] + r2["h"]) - max(r1["y"], r2["y"]))
    return x_overlap * y_overlap


def calc_text_overlap_ratio(poster_data: Dict[str, Any]) -> float:
    """
    计算文字图层间的重叠面积占文字总面积的比例。

    返回 0.0 表示无重叠，值越大重叠越严重。文字图层不足 2 个时返回 0.0。
    """
    layers = poster_data.get("layers", [])
    text_rects = []
    for l in layers:
        if l.get("type") != "text":
            continue
        w = l.get("width", 0)
        h = l.get("height", 0)
        if w <= 0 or h <= 0:
            continue
        text_rects.append({
            "x": l.get("x", 0), "y": l.get("y", 0), "w": w, "h": h,
        })

    if len(text_rects) < 2:
        return 0.0

    total_area = sum(r["w"] * r["h"] for r in text_rects)
    if total_area == 0:
        return 0.0

    overlap_area = 0.0
    for i in range(len(text_rects)):
        for j in range(i + 1, len(text_rects)):
            overlap_area += _rect_overlap_area(text_rects[i], text_rects[j])

    return round(overlap_area / total_area, 4)


# ============================================================================
# 指标 5：间距均匀性
# ============================================================================

def calc_gap_uniformity(poster_data: Dict[str, Any]) -> float:
    """
    计算相邻文字图层垂直间距的变异系数（std / mean）。

    返回 0.0 表示间距完全均匀，值越大越不均匀。
    文字图层不足 2 个时返回 0.0。
    """
    layers = poster_data.get("layers", [])
    text_layers = []
    for l in layers:
        if l.get("type") != "text":
            continue
        h = l.get("height", 0)
        if h <= 0:
            continue
        text_layers.append({"y": l.get("y", 0), "h": h})

    if len(text_layers) < 2:
        return 0.0

    text_layers.sort(key=lambda t: t["y"])

    gaps = []
    for i in range(len(text_layers) - 1):
        gap = text_layers[i + 1]["y"] - text_layers[i]["y"] - text_layers[i]["h"]
        gaps.append(gap)

    if not gaps:
        return 0.0

    mean = statistics.mean(gaps)
    if mean == 0:
        return 0.0

    std = statistics.stdev(gaps) if len(gaps) > 1 else 0.0
    return round(abs(std / mean), 4)


# ============================================================================
# 指标 6：对齐一致性
# ============================================================================

def calc_alignment_lines(poster_data: Dict[str, Any]) -> int:
    """
    计算文字图层的水平对齐线数量。

    将文字图层的左边缘 x 和中心 center_x 分别聚类（容差 5px），
    取两者中较少的作为对齐线数。值为 1 表示所有文字完美对齐在同一条
    基准线上，值越大表示文字分布越分散。
    文字图层不足 2 个时返回 0。
    """
    layers = poster_data.get("layers", [])
    text_layers = [l for l in layers if l.get("type") == "text"
                   and l.get("width", 0) > 0]

    if len(text_layers) < 2:
        return 0

    def count_clusters(values: List[float], tolerance: float = 5.0) -> int:
        if not values:
            return 0
        sorted_vals = sorted(values)
        clusters = 1
        for i in range(1, len(sorted_vals)):
            if sorted_vals[i] - sorted_vals[i - 1] > tolerance:
                clusters += 1
        return clusters

    x_coords = [l.get("x", 0) for l in text_layers]
    center_coords = [l.get("x", 0) + l.get("width", 0) / 2 for l in text_layers]

    return min(count_clusters(x_coords), count_clusters(center_coords))


# ============================================================================
# 指标 7：品牌色彩匹配度
# ============================================================================

def calc_brand_color_adherence(
    poster_data: Dict[str, Any],
    design_brief: Optional[Dict[str, Any]] = None,
) -> float:
    """
    检查海报实际使用的颜色与 RAG 品牌知识中色值的匹配度。

    从 design_brief["brand_knowledge"] 文本中提取 hex 色值作为品牌参考色，
    然后与海报中 main_color 和文字图层颜色逐一比对。

    返回 0.0~1.0（匹配颜色占比），无品牌知识时返回 -1.0（不适用）。
    """
    if not design_brief:
        return -1.0

    brand_knowledge = design_brief.get("brand_knowledge") or []
    if not brand_knowledge:
        return -1.0

    # 从品牌知识文本中提取所有 hex 色值
    brand_colors = set()
    hex_pattern = re.compile(r"#[0-9A-Fa-f]{6}")
    for item in brand_knowledge:
        text = item.get("text", "") if isinstance(item, dict) else str(item)
        for match in hex_pattern.findall(text):
            brand_colors.add(match.upper())

    if not brand_colors:
        return -1.0

    # 收集海报实际使用的颜色
    poster_colors = []
    main_color = design_brief.get("main_color", "")
    if main_color:
        poster_colors.append(main_color)

    for layer in poster_data.get("layers", []):
        if layer.get("type") == "text":
            c = layer.get("color", "")
            if c and c != "transparent":
                poster_colors.append(c)

    if not poster_colors:
        return 0.0

    # 计算匹配度：距离 < 80 视为匹配
    match_count = 0
    threshold = 80.0
    for pc in poster_colors:
        min_dist = min(_color_distance(pc, bc) for bc in brand_colors)
        if min_dist < threshold:
            match_count += 1

    return round(match_count / len(poster_colors), 2)


# ============================================================================
# 指标 8：装饰层丰富度
# ============================================================================

def calc_decoration_layers(poster_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    统计海报中 rect 装饰层的数量和类别。

    DSL + 布局引擎会自动注入 overlay、divider、装饰形状等视觉层次元素，
    而 LLM 直接输出坐标的模式通常只产出 image + text。
    """
    layers = poster_data.get("layers", [])
    rect_layers = [l for l in layers if l.get("type") == "rect"]
    has_overlay = any(l.get("subtype") == "overlay" for l in rect_layers)
    has_divider = any(l.get("subtype") == "divider" for l in rect_layers)

    return {
        "count": len(rect_layers),
        "has_overlay": has_overlay,
        "has_divider": has_divider,
    }


# ============================================================================
# 指标 9：间距异常率
# ============================================================================

def calc_gap_defects(poster_data: Dict[str, Any]) -> int:
    """
    统计相邻文字图层间距 <= 0 的对数。

    间距为零或负说明文字在垂直方向上发生了重叠或贴靠，
    属于坐标计算的结构性缺陷。布局引擎的容器排列在算法上
    保证相邻元素间距不低于最小值，因此 DSL 组该值恒为 0。
    """
    layers = poster_data.get("layers", [])
    text_layers = sorted(
        [l for l in layers if l.get("type") == "text" and l.get("height", 0) > 0],
        key=lambda l: l.get("y", 0),
    )

    defects = 0
    for i in range(len(text_layers) - 1):
        gap = text_layers[i + 1].get("y", 0) - text_layers[i].get("y", 0) - text_layers[i].get("height", 0)
        if gap <= 0:
            defects += 1
    return defects


# ============================================================================
# 指标 10：字号层次比
# ============================================================================

def calc_font_size_ratio(poster_data: Dict[str, Any]) -> float:
    """
    计算最大字号与最小字号的比值。

    合理的海报排版中标题字号是正文的 2-4 倍。比值过大（>8）说明
    LLM 输出了极端字号组合（如 fontSize=2 和 fontSize=96 共存），
    比值接近 1 说明缺乏层次感。
    """
    layers = poster_data.get("layers", [])
    sizes = [l.get("fontSize", 0) for l in layers
             if l.get("type") == "text" and l.get("fontSize", 0) > 0]
    if len(sizes) < 2:
        return 0.0
    return round(max(sizes) / min(sizes), 2)


# ============================================================================
# 汇总
# ============================================================================

def evaluate_poster(
    poster_data: Dict[str, Any],
    design_brief: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """一次性计算所有指标"""
    readability = calc_text_readability(poster_data)
    validity = calc_layout_validity(poster_data)
    consistency = calc_style_consistency(poster_data, design_brief)

    overlap = calc_text_overlap_ratio(poster_data)
    gap_cv = calc_gap_uniformity(poster_data)
    align_lines = calc_alignment_lines(poster_data)
    brand_adherence = calc_brand_color_adherence(poster_data, design_brief)

    decoration = calc_decoration_layers(poster_data)
    gap_defects = calc_gap_defects(poster_data)
    font_ratio = calc_font_size_ratio(poster_data)

    return {
        "text_readability": readability,
        "readability_pass": readability >= 3.0,
        "layout_validity": validity,
        "style_consistency": consistency,
        "text_overlap_ratio": overlap,
        "gap_uniformity_cv": gap_cv,
        "alignment_lines": align_lines,
        "brand_color_adherence": brand_adherence,
        "decoration_layers": decoration,
        "gap_defects": gap_defects,
        "font_size_ratio": font_ratio,
    }
