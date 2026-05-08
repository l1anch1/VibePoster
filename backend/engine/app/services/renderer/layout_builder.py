"""
布局构建器 — 语义 DSL → OOP 容器布局 → 扁平元素字典列表

核心流程：
    1. LLM 输出语义 DSL（无坐标，只有内容和样式属性）
    2. LayoutBuilder 根据 layout_strategy 创建 OOP 容器树
    3. VerticalContainer.arrange() 动态计算所有坐标
    4. 输出与 SchemaConverter 兼容的扁平元素字典列表

坐标计算权完全归 OOP 引擎，LLM 只负责"放什么"和"什么风格"。
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from ...core.layout import (
    VerticalContainer,
    TextBlock,
    ImageBlock,
    ShapeBlock,
    Style,
    Element,
)
from ...core.logger import get_logger
from .font_registry import resolve_font, resolve_font_style_from_kg, DEFAULT_FONT_STYLE

logger = get_logger(__name__)


# ============================================================================
# WCAG 2.0 对比度计算（用于文字颜色后置校验）
# ============================================================================

def _hex_to_rgb(hex_color: str) -> tuple:
    """#RRGGBB 或 #RGB 转为 (r, g, b)"""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = h[0] * 2 + h[1] * 2 + h[2] * 2
    if len(h) < 6:
        return (0, 0, 0)
    try:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    except ValueError:
        return (0, 0, 0)


def _relative_luminance(r: int, g: int, b: int) -> float:
    """WCAG 2.0 相对亮度"""
    def linearize(c):
        s = c / 255.0
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4
    return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)


def _wcag_contrast(color1: str, color2: str) -> float:
    """计算两个十六进制颜色的 WCAG 对比度（1.0 ~ 21.0）"""
    r1, g1, b1 = _hex_to_rgb(color1)
    r2, g2, b2 = _hex_to_rgb(color2)
    l1 = _relative_luminance(r1, g1, b1)
    l2 = _relative_luminance(r2, g2, b2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


# ============================================================================
# 布局策略配置
# ============================================================================

@dataclass(frozen=True)
class LayoutRegion:
    """布局区域（画布比例坐标 0.0~1.0）"""
    y_start: float
    y_end: float
    align: str = "center"


@dataclass(frozen=True)
class StrategyConfig:
    """单个布局策略的完整参数"""
    content_region: LayoutRegion
    cta_region: Optional[LayoutRegion] = None
    padding: float = 60
    gap: float = 20
    text_align: str = "center"
    title_scale: float = 1.0
    overlay_coverage: str = "content"


STRATEGIES: Dict[str, StrategyConfig] = {
    "top_text": StrategyConfig(
        content_region=LayoutRegion(0.04, 0.50),
        padding=48, gap=20, text_align="left",
        overlay_coverage="full",
    ),
    "centered": StrategyConfig(
        content_region=LayoutRegion(0.28, 0.72),
        padding=100, gap=36, text_align="center",
        overlay_coverage="content",
    ),
    "bottom_heavy": StrategyConfig(
        content_region=LayoutRegion(0.58, 0.96),
        padding=48, gap=16, text_align="left",
        overlay_coverage="bottom_half",
    ),
    "left_aligned": StrategyConfig(
        content_region=LayoutRegion(0.12, 0.88),
        padding=48, gap=12, text_align="left",
        overlay_coverage="full",
    ),
    "diagonal": StrategyConfig(
        content_region=LayoutRegion(0.04, 0.42, align="left"),
        cta_region=LayoutRegion(0.80, 0.96, align="right"),
        padding=48, gap=16, text_align="left",
        overlay_coverage="full",
    ),
    "big_title": StrategyConfig(
        content_region=LayoutRegion(0.15, 0.85),
        padding=32, gap=40, text_align="center",
        title_scale=1.8,
        overlay_coverage="content",
    ),
    "split_vertical": StrategyConfig(
        content_region=LayoutRegion(0.04, 0.45),
        cta_region=LayoutRegion(0.58, 0.96),
        padding=48, gap=12, text_align="center",
        overlay_coverage="full",
    ),
}

VALID_STRATEGIES = list(STRATEGIES.keys())
DEFAULT_STRATEGY = "centered"


# ============================================================================
# 指令 command 分组
# ============================================================================

_TITLE_COMMANDS = frozenset({"add_title", "add_heading", "add_main_title"})
_SUBTITLE_COMMANDS = frozenset({"add_subtitle", "add_subheading"})
_BODY_COMMANDS = frozenset({"add_text", "add_body_text", "add_description"})
_CTA_COMMANDS = frozenset({"add_cta", "add_button_text"})
_TEXT_COMMANDS = _TITLE_COMMANDS | _SUBTITLE_COMMANDS | _BODY_COMMANDS
_DIVIDER_COMMANDS = frozenset({"add_divider", "add_line"})
_SHAPE_COMMANDS = frozenset({"add_shape", "add_rect"})
_OVERLAY_COMMANDS = frozenset({"add_overlay", "add_gradient"})


# ============================================================================
# LayoutBuilder
# ============================================================================

class LayoutBuilder:
    """
    将语义 DSL 指令 + 布局策略 → OOP 容器 → arrange() → 扁平元素列表。

    与旧 DSLParser 的核心区别：坐标由 OOP 引擎计算，而非从 LLM 输出读取。
    """

    def build(
        self,
        dsl_instructions: List[Dict[str, Any]],
        layout_strategy: str = DEFAULT_STRATEGY,
        canvas_width: int = 1080,
        canvas_height: int = 1920,
        design_brief: Optional[Dict[str, Any]] = None,
        font_style: Optional[str] = None,
        subject_size: Optional[tuple] = None,
    ) -> List[Dict[str, Any]]:
        """
        构建布局并返回扁平元素字典列表（与 SchemaConverter 兼容）。
        """
        resolved_font_style = _resolve_font_style(font_style, design_brief)
        strategy = STRATEGIES.get(layout_strategy, STRATEGIES[DEFAULT_STRATEGY])
        main_color = (design_brief or {}).get("main_color", "#000000")

        logger.info(
            f"🏗️ OOP 布局构建: strategy={layout_strategy}, "
            f"font_style={resolved_font_style}, {len(dsl_instructions)} 条指令"
        )

        # ── 1. 分类指令 ──
        bg_instrs, subj_instrs, overlay_instrs, content_instrs, cta_instrs = (
            _classify_instructions(dsl_instructions)
        )

        # ── 2. 背景图（始终全屏铺满，不经过 OOP 引擎） ──
        result: List[Dict[str, Any]] = []
        for bg in bg_instrs:
            result.append({
                "type": "image", "x": 0, "y": 0,
                "width": canvas_width, "height": canvas_height,
                "src": bg.get("src", ""), "layer_type": "background",
            })

        # ── 3. 主内容容器 ──
        avail_w = canvas_width - 2 * strategy.padding
        content_elems = self._create_elements(
            content_instrs, avail_w, resolved_font_style, main_color,
            design_brief, strategy, strategy.text_align,
        )

        content_ctr = self._build_and_arrange_container(
            content_elems, strategy.content_region,
            canvas_width, canvas_height, strategy.padding, strategy.gap,
            text_align=strategy.text_align,
        )

        # ── 4. CTA 区域 ──
        cta_ctr: Optional[VerticalContainer] = None
        if cta_instrs:
            cta_align = strategy.cta_region.align if strategy.cta_region else strategy.text_align
            cta_elems = self._create_elements(
                cta_instrs, avail_w, resolved_font_style, main_color,
                design_brief, strategy, cta_align,
            )
            if strategy.cta_region:
                cta_ctr = self._build_and_arrange_container(
                    cta_elems, strategy.cta_region,
                    canvas_width, canvas_height, strategy.padding, strategy.gap,
                    text_align=cta_align,
                )
            else:
                for e in cta_elems:
                    content_ctr.add(e)
                content_ctr.arrange()
                self._center_in_region(content_ctr, strategy.content_region, canvas_height)

        # ── 5. Overlay（铺设于背景与文字之间） ──
        for ov in overlay_instrs:
            result.append(self._build_overlay(
                ov, content_ctr, cta_ctr, strategy, canvas_width, canvas_height, design_brief,
            ))

        # ── 6. 主体素材（置于 overlay 之后、文字之前，避免遮挡文字） ──
        subj_w = subject_size[0] if subject_size else None
        subj_h = subject_size[1] if subject_size else None
        for subj in subj_instrs:
            result.append(self._build_subject(subj, strategy, canvas_width, canvas_height, subj_w, subj_h))

        # ── 7. 收集内容图层（文字在最上层） ──
        result.extend(content_ctr.get_all_elements())
        if cta_ctr:
            result.extend(cta_ctr.get_all_elements())

        # ── 8. 画布边界保护 ──
        result = [_ensure_canvas_bounds(e, canvas_width, canvas_height) for e in result]

        # ── 9. 文字颜色对比度校验 ──
        bg_color = self._extract_bg_color(result)
        result = [self._ensure_text_contrast(e, bg_color) for e in result]

        # ── 10. rect+text 对齐修正（按钮/高亮色块内的文字居中） ──
        result = _fix_rect_text_alignment(result)

        logger.info(f"✅ OOP 布局完成，共 {len(result)} 个元素")
        return result

    # ------------------------------------------------------------------
    # OOP 元素创建
    # ------------------------------------------------------------------

    def _create_elements(
        self,
        instructions: List[Dict[str, Any]],
        available_width: float,
        font_style: str,
        main_color: str,
        design_brief: Optional[Dict[str, Any]],
        strategy: StrategyConfig,
        text_align: str,
    ) -> List[Element]:
        elements: List[Element] = []
        for instr in instructions:
            cmd = instr.get("command", "")
            elem: Optional[Element] = None

            if cmd in _TITLE_COMMANDS:
                elem = self._make_text(
                    instr, available_width, font_style, role="title",
                    default_size=int(48 * strategy.title_scale),
                    default_color=main_color, default_weight="bold",
                    default_align=text_align,
                )
            elif cmd in _SUBTITLE_COMMANDS:
                elem = self._make_text(
                    instr, available_width, font_style, role="body",
                    default_size=32, default_color="#E0E0E0",
                    default_weight="normal", default_align=text_align,
                )
            elif cmd in _BODY_COMMANDS:
                body_align = text_align if text_align != "center" else "left"
                elem = self._make_text(
                    instr, available_width, font_style, role="body",
                    default_size=24, default_color="#F0F0F0",
                    default_weight="normal", default_align=body_align,
                )
            elif cmd in _CTA_COMMANDS:
                elem = self._make_text(
                    instr, available_width, font_style, role="title",
                    default_size=28, default_color="#8B5CF6",
                    default_weight="bold", default_align="center",
                )
            elif cmd in _DIVIDER_COMMANDS:
                elem = self._make_divider(instr, available_width, design_brief)
            elif cmd in _SHAPE_COMMANDS:
                elem = self._make_shape(instr, available_width, design_brief)

            if elem:
                elements.append(elem)
        return elements

    # ------------------------------------------------------------------
    # 元素工厂
    # ------------------------------------------------------------------

    @staticmethod
    def _make_text(
        instr: Dict[str, Any],
        available_width: float,
        font_style: str,
        role: str,
        default_size: int,
        default_color: str,
        default_weight: str,
        default_align: str,
    ) -> TextBlock:
        fs = int(instr.get("font_size", default_size))
        font = resolve_font(font_style, role=role)
        return TextBlock(
            content=instr.get("content", ""),
            font_size=fs,
            max_width=available_width,
            style=Style(
                font_size=fs,
                font_family=font["family"],
                font_weight=instr.get("font_weight", default_weight),
                color=instr.get("color", default_color),
                text_align=instr.get("text_align", default_align),
            ),
        )

    @staticmethod
    def _make_divider(
        instr: Dict[str, Any],
        available_width: float,
        design_brief: Optional[Dict[str, Any]],
    ) -> ShapeBlock:
        deco = _get_decoration_style(design_brief, "divider")
        color = _resolve_kg_color(design_brief, deco.get("color_source", "accent"))
        ratio = float(instr.get("width_ratio", 0.5))
        return ShapeBlock(
            width=ratio * available_width,
            height=max(int(deco.get("thickness", 2)), 2),
            subtype="divider",
            background_color=instr.get("color", color),
            style=Style(opacity=deco.get("opacity", 0.6)),
        )

    @staticmethod
    def _make_shape(
        instr: Dict[str, Any],
        available_width: float,
        design_brief: Optional[Dict[str, Any]],
    ) -> ShapeBlock:
        deco = _get_decoration_style(design_brief, "shape")
        fill = _resolve_kg_color(design_brief, deco.get("fill_source", "accent"))
        bw = int(deco.get("border_width", 0))
        bc = (
            _resolve_kg_color(design_brief, deco.get("border_color_source", "primary"))
            if bw > 0 else "transparent"
        )
        ratio = float(instr.get("width_ratio", 1.0))
        h = int(instr.get("height", 80))
        return ShapeBlock(
            width=ratio * available_width, height=h,
            subtype=instr.get("subtype", "rect"),
            background_color=instr.get("color", fill),
            border_radius=int(instr.get("border_radius", deco.get("border_radius", 0))),
            border_color=bc, border_width=bw,
            style=Style(opacity=float(instr.get("opacity", deco.get("opacity", 0.9)))),
        )

    # ------------------------------------------------------------------
    # 容器构建 + 区域内居中
    # ------------------------------------------------------------------

    @staticmethod
    def _build_and_arrange_container(
        elements: List[Element],
        region: LayoutRegion,
        canvas_width: int,
        canvas_height: int,
        padding: float,
        gap: float,
        text_align: str = "center",
    ) -> VerticalContainer:
        region_y = int(region.y_start * canvas_height)
        ctr = VerticalContainer(
            x=0, y=region_y,
            width=canvas_width, padding=padding, gap=gap,
            style=Style(text_align=text_align),
        )
        for e in elements:
            ctr.add(e)
        ctr.arrange()

        LayoutBuilder._center_in_region(ctr, region, canvas_height)
        return ctr

    @staticmethod
    def _center_in_region(
        container: VerticalContainer, region: LayoutRegion, canvas_height: int,
    ) -> None:
        """将容器内容在指定区域内垂直居中"""
        region_h = (region.y_end - region.y_start) * canvas_height
        if container.height < region_h:
            offset = (region_h - container.height) / 2
            container.y = int(region.y_start * canvas_height + offset)
            container.arrange()

    # ------------------------------------------------------------------
    # 特殊图层
    # ------------------------------------------------------------------

    @staticmethod
    def _build_overlay(
        instr: Dict[str, Any],
        content_ctr: VerticalContainer,
        cta_ctr: Optional[VerticalContainer],
        strategy: StrategyConfig,
        cw: int, ch: int,
        design_brief: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        deco = _get_decoration_style(design_brief, "overlay")
        color = _resolve_kg_color(design_brief, deco.get("color_source", "primary"))

        cov = strategy.overlay_coverage
        if cov == "content":
            y_top = max(0, int(content_ctr.y) - 40)
            y_bot = min(ch, int(content_ctr.y + content_ctr.height) + 40)
            if cta_ctr:
                y_bot = min(ch, max(y_bot, int(cta_ctr.y + cta_ctr.height) + 40))
        elif cov == "bottom_half":
            y_top, y_bot = ch // 2, ch
        else:
            y_top, y_bot = 0, ch

        gradient = ""
        ov_type = deco.get("type", "linear-gradient")
        if ov_type.startswith("linear"):
            _dir_map = {
                "to-bottom": "180deg", "to-top": "0deg",
                "to-right": "90deg", "diagonal": "135deg",
            }
            deg = _dir_map.get(deco.get("direction", "to-bottom"), "180deg")
            gradient = f"linear-gradient({deg}, {color}cc, {color}00)"
        elif ov_type.startswith("radial"):
            gradient = f"radial-gradient(circle, {color}cc, {color}00)"

        return {
            "type": "rect", "subtype": "overlay",
            "x": 0, "y": y_top, "width": cw, "height": y_bot - y_top,
            "backgroundColor": color if not gradient else "transparent",
            "gradient": gradient,
            "opacity": deco.get("opacity", 0.5),
            "borderRadius": 0, "borderColor": "transparent", "borderWidth": 0,
        }

    @staticmethod
    def _build_subject(
        instr: Dict[str, Any],
        strategy: StrategyConfig,
        cw: int, ch: int,
        subject_width: Optional[int] = None,
        subject_height: Optional[int] = None,
    ) -> Dict[str, Any]:
        """主体素材定位：基于内容区域互补 + 宽高比等比缩放"""
        mid = (strategy.content_region.y_start + strategy.content_region.y_end) / 2
        if mid < 0.5:
            region_y_start = strategy.content_region.y_end + 0.02
            region_y_end = 0.96
        else:
            region_y_start = 0.04
            region_y_end = strategy.content_region.y_start - 0.02

        region_h = int(ch * (region_y_end - region_y_start))
        region_y = int(ch * region_y_start)

        if subject_width and subject_height and subject_width > 0 and subject_height > 0:
            aspect = subject_width / subject_height
            max_w = int(cw * 0.85)
            max_h = region_h

            if aspect >= 1:
                w = min(max_w, int(max_h * aspect))
                h = int(w / aspect)
            else:
                h = min(max_h, int(max_w / aspect))
                w = int(h * aspect)

            x = (cw - w) // 2
            y = region_y + (region_h - h) // 2
        else:
            x = 0
            y = region_y
            w = cw
            h = region_h

        return {
            "type": "image",
            "x": x, "y": y, "width": w, "height": h,
            "src": instr.get("src", ""), "layer_type": "subject",
        }

    # ------------------------------------------------------------------
    # 颜色对比度校验
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_bg_color(layers: List[Dict[str, Any]]) -> str:
        """
        从已构建的图层列表中提取文字实际所在的有效背景色。

        优先级：
        1. 如果存在不透明度 >= 0.5 的 overlay（含 gradient），以其主色为准
        2. 否则用第一个 image 图层的颜色
        3. 回退到 #333333
        """
        import re
        image_color = "#333333"
        overlay_color = None

        for layer in layers:
            # 提取背景图颜色
            if layer.get("type") == "image" and image_color == "#333333":
                src = layer.get("src", "")
                m = re.search(r"placehold\.co/\d+x\d+/([0-9A-Fa-f]{6})", src)
                if m:
                    image_color = f"#{m.group(1).upper()}"

            # 检测 overlay（含 gradient）
            if (layer.get("type") == "rect"
                    and layer.get("subtype") == "overlay"
                    and layer.get("opacity", 1.0) >= 0.5):
                bg = layer.get("backgroundColor", "")
                if bg and bg != "transparent":
                    overlay_color = bg
                elif layer.get("gradient"):
                    # 从 gradient 字符串中提取第一个 hex 色值
                    gm = re.search(r"#([0-9A-Fa-f]{6})", layer["gradient"])
                    if gm:
                        overlay_color = f"#{gm.group(1).upper()}"

        if overlay_color:
            return overlay_color

        return image_color

    @staticmethod
    def _ensure_text_contrast(
        elem: Dict[str, Any], bg_color: str,
    ) -> Dict[str, Any]:
        """如果文字与背景对比度不足 3.0，替换为黑或白中对比度更高的"""
        if elem.get("type") != "text":
            return elem
        text_color = elem.get("color", "#FFFFFF")
        if not text_color or text_color == "transparent":
            return elem

        ratio = _wcag_contrast(text_color, bg_color)
        if ratio >= 3.0:
            return elem

        white_ratio = _wcag_contrast("#FFFFFF", bg_color)
        black_ratio = _wcag_contrast("#000000", bg_color)
        elem["color"] = "#FFFFFF" if white_ratio >= black_ratio else "#000000"
        return elem


# ============================================================================
# 模块级辅助函数
# ============================================================================

def _resolve_font_style(
    font_style: Optional[str], design_brief: Optional[Dict[str, Any]],
) -> str:
    if font_style and font_style.lower().strip():
        return font_style.lower().strip()
    kg = (design_brief or {}).get("kg_rules")
    if kg:
        ts = kg.get("typography_styles", [])
        if ts:
            return resolve_font_style_from_kg(ts)
    return DEFAULT_FONT_STYLE


def _classify_instructions(
    instructions: List[Dict[str, Any]],
) -> Tuple[
    List[Dict[str, Any]],  # background
    List[Dict[str, Any]],  # subject
    List[Dict[str, Any]],  # overlay
    List[Dict[str, Any]],  # content
    List[Dict[str, Any]],  # cta
]:
    bg: List[Dict[str, Any]] = []
    subj: List[Dict[str, Any]] = []
    overlay: List[Dict[str, Any]] = []
    content: List[Dict[str, Any]] = []
    cta: List[Dict[str, Any]] = []

    for instr in instructions:
        cmd = instr.get("command", "")
        if cmd == "add_image":
            lt = instr.get("layer_type", "background")
            (bg if lt == "background" else subj).append(instr)
        elif cmd in _OVERLAY_COMMANDS:
            overlay.append(instr)
        elif cmd in _CTA_COMMANDS:
            cta.append(instr)
        elif cmd in _TEXT_COMMANDS or cmd in _DIVIDER_COMMANDS or cmd in _SHAPE_COMMANDS:
            content.append(instr)
        else:
            logger.warning(f"未知 DSL 指令: {cmd}")

    return bg, subj, overlay, content, cta


def _get_decoration_style(
    design_brief: Optional[Dict[str, Any]], decoration_type: str,
) -> Dict[str, Any]:
    kg = (design_brief or {}).get("kg_rules") or {}
    return (kg.get("decoration_styles") or {}).get(decoration_type, {})


def _resolve_kg_color(
    design_brief: Optional[Dict[str, Any]], source_key: str,
) -> str:
    kg = (design_brief or {}).get("kg_rules") or {}
    colors = (kg.get("color_palettes") or {}).get(source_key, [])
    return colors[0] if colors else "#A78BFA"


def _fix_rect_text_alignment(layers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    修正 rect + text 对的 y 坐标对齐。

    LLM 生成 add_shape（色块/按钮背景）+ add_cta（按钮文字）时，VerticalContainer
    将它们作为独立元素按间距排列，导致 text 不在 rect 内部。
    此函数检测相邻的 rect-text 对，将 text 的 y 居中到 rect 内部。
    """
    for i in range(len(layers) - 1):
        curr = layers[i]
        nxt = layers[i + 1]

        # 检测 rect + text 对（rect 的 subtype 是 label/highlight/shape/rect 等）
        if (curr.get("type") == "rect"
                and curr.get("subtype") in ("label", "highlight", "shape", "rect")
                and nxt.get("type") == "text"):

            rect_y = curr.get("y", 0)
            rect_h = curr.get("height", 0)
            text_h = nxt.get("height", 0)

            if rect_h > 0 and text_h > 0:
                # 将 text 垂直居中在 rect 内
                centered_y = rect_y + (rect_h - text_h) // 2
                nxt["y"] = max(rect_y, centered_y)
                # text 宽度不超过 rect（留 padding）
                rect_w = curr.get("width", 0)
                rect_x = curr.get("x", 0)
                if rect_w > 0:
                    padding = min(20, rect_w * 0.1)
                    nxt["x"] = int(rect_x + padding)
                    nxt["width"] = int(rect_w - 2 * padding)

    return layers


def _ensure_canvas_bounds(
    elem: Dict[str, Any], cw: int, ch: int,
) -> Dict[str, Any]:
    if elem.get("layer_type") == "background":
        return elem
    if elem.get("subtype") == "overlay":
        return elem

    margin = 20
    min_h = 1 if elem.get("subtype") == "divider" else 20
    x = max(margin, min(int(elem["x"]), cw - margin))
    y = max(margin, min(int(elem["y"]), ch - margin))
    w = max(40, min(int(elem["width"]), cw - x - margin))
    h = max(min_h, min(int(elem["height"]), ch - y - margin))
    elem.update({"x": x, "y": y, "width": w, "height": h})
    return elem
