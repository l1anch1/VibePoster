"""
DSL 解析器 - 解析 Layout Agent 的 DSL 指令（绝对坐标模式）

LLM 直接输出每个元素的 x, y, width, height，
解析器负责类型校验、越界修正、字体映射，然后输出扁平的元素列表。
"""

from typing import Dict, Any, List, Optional

from ...core.logger import get_logger
from .font_registry import resolve_font, resolve_font_style_from_kg, DEFAULT_FONT_STYLE

logger = get_logger(__name__)

# command → layer role（用于字体注册表查询 title / body）
_CMD_ROLE_MAP: Dict[str, str] = {
    "add_title": "title", "add_heading": "title", "add_main_title": "title",
    "add_subtitle": "body",  "add_subheading": "body",
    "add_text": "body", "add_body_text": "body", "add_description": "body",
    "add_cta": "title", "add_button_text": "title",
}


class DSLParser:
    """
    DSL 解析器（绝对坐标模式）

    每条 DSL 指令必须包含 x, y, width, height，
    解析器将其转换为渲染层可直接消费的元素字典列表。
    """

    def __init__(self):
        self.canvas_width: int = 1080
        self.canvas_height: int = 1920

    def parse(
        self,
        dsl_instructions: List[Dict[str, Any]],
        canvas_width: int = 1080,
        canvas_height: int = 1920,
        design_brief: Optional[Dict[str, Any]] = None,
        font_style: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        解析 DSL 指令列表，返回扁平的元素字典列表。

        Args:
            font_style: LLM 输出的字体风格枚举（sans/serif/rounded/handwriting/display），
                        缺省时从 design_brief 中的 KG typography_styles 推断。

        Returns:
            [{"type": "image"|"text", "x": ..., "y": ..., "fontFamily": ..., ...}, ...]
        """
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        main_color = (design_brief or {}).get("main_color", "#000000")

        resolved_font_style = self._resolve_font_style(font_style, design_brief)
        logger.info(
            f"🎨 解析 {len(dsl_instructions)} 条 DSL 指令"
            f"（绝对坐标模式，font_style={resolved_font_style}）"
        )

        elements: List[Dict[str, Any]] = []

        for i, instr in enumerate(dsl_instructions):
            try:
                elem = self._parse_instruction(instr, main_color, resolved_font_style, design_brief)
                if elem:
                    elem = self._clamp_bounds(elem)
                    elements.append(elem)
                    logger.debug(f"  ✅ [{i+1}] {instr.get('command')} → ({elem['x']},{elem['y']}) {elem['width']}×{elem['height']}")
            except Exception as e:
                logger.error(f"  ❌ [{i+1}] 解析失败: {e}")

        logger.info(f"✅ 解析完成，共 {len(elements)} 个元素")
        return elements

    @staticmethod
    def _resolve_font_style(
        font_style: Optional[str],
        design_brief: Optional[Dict[str, Any]],
    ) -> str:
        """确定最终 font_style：LLM 显式指定 > KG 推断 > 默认值"""
        if font_style and font_style.lower().strip() != "":
            return font_style.lower().strip()

        kg_rules = (design_brief or {}).get("kg_rules")
        if kg_rules:
            ts = kg_rules.get("typography_styles", [])
            if ts:
                return resolve_font_style_from_kg(ts)

        return DEFAULT_FONT_STYLE

    # ------------------------------------------------------------------
    # 指令 → 元素字典
    # ------------------------------------------------------------------

    def _parse_instruction(
        self, instr: Dict[str, Any], main_color: str, font_style: str,
        design_brief: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        cmd = instr.get("command", "")

        x = int(instr.get("x", 0))
        y = int(instr.get("y", 0))
        w = int(instr.get("width", 0))
        h = int(instr.get("height", 0))

        if cmd == "add_image":
            return {
                "type": "image",
                "x": x, "y": y, "width": w, "height": h,
                "src": instr.get("src", ""),
                "layer_type": instr.get("layer_type", "background"),
            }

        if cmd in ("add_title", "add_heading", "add_main_title"):
            return self._text_elem(instr, x, y, w, h,
                                   font_style=font_style, role="title",
                                   default_size=48, default_color=main_color,
                                   default_weight="bold", default_align="center")

        if cmd in ("add_subtitle", "add_subheading"):
            return self._text_elem(instr, x, y, w, h,
                                   font_style=font_style, role="body",
                                   default_size=32, default_color="#666666",
                                   default_weight="normal", default_align="center")

        if cmd in ("add_text", "add_body_text", "add_description"):
            return self._text_elem(instr, x, y, w, h,
                                   font_style=font_style, role="body",
                                   default_size=24, default_color="#333333",
                                   default_weight="normal", default_align="left")

        if cmd in ("add_cta", "add_button_text"):
            return self._text_elem(instr, x, y, w, h,
                                   font_style=font_style, role="title",
                                   default_size=28, default_color="#0066FF",
                                   default_weight="bold", default_align="center")

        # ---- 装饰类指令（KG 驱动样式） ----

        if cmd in ("add_divider", "add_line"):
            return self._divider_elem(instr, x, y, w, h, design_brief)

        if cmd in ("add_overlay", "add_gradient"):
            return self._overlay_elem(instr, x, y, w, h, design_brief)

        if cmd in ("add_shape", "add_rect"):
            return self._shape_elem(instr, x, y, w, h, design_brief)

        logger.warning(f"未知指令: {cmd}")
        return None

    # ------------------------------------------------------------------
    # 装饰元素构建（KG 知识感知）
    # ------------------------------------------------------------------

    def _get_decoration_style(
        self, design_brief: Optional[Dict[str, Any]], decoration_type: str
    ) -> Dict[str, Any]:
        """从 KG 装饰推荐中读取指定类型的样式"""
        kg = (design_brief or {}).get("kg_rules", {})
        deco = kg.get("decoration_styles", {})
        return deco.get(decoration_type, {})

    def _resolve_color_from_source(
        self, design_brief: Optional[Dict[str, Any]], source_key: str
    ) -> str:
        """从 KG 调色板中根据 source_key 取色"""
        kg = (design_brief or {}).get("kg_rules", {})
        palettes = kg.get("color_palettes", {})
        colors = palettes.get(source_key, [])
        return colors[0] if colors else "#666666"

    def _divider_elem(
        self, instr: Dict[str, Any],
        x: int, y: int, w: int, h: int,
        design_brief: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        deco = self._get_decoration_style(design_brief, "divider")
        color = self._resolve_color_from_source(
            design_brief, deco.get("color_source", "accent")
        )
        return {
            "type": "rect", "subtype": "divider",
            "x": x, "y": y, "width": w,
            "height": max(h, deco.get("thickness", 2)),
            "backgroundColor": instr.get("color", color),
            "opacity": deco.get("opacity", 0.6),
            "borderRadius": 0,
            "borderColor": "transparent", "borderWidth": 0, "gradient": "",
        }

    def _overlay_elem(
        self, instr: Dict[str, Any],
        x: int, y: int, w: int, h: int,
        design_brief: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        deco = self._get_decoration_style(design_brief, "overlay")
        color = self._resolve_color_from_source(
            design_brief, deco.get("color_source", "primary")
        )
        gradient = ""
        overlay_type = deco.get("type", "linear-gradient")
        if overlay_type.startswith("linear"):
            direction_map = {
                "to-bottom": "180deg", "to-top": "0deg",
                "to-right": "90deg", "diagonal": "135deg",
            }
            deg = direction_map.get(deco.get("direction", "to-bottom"), "180deg")
            gradient = f"linear-gradient({deg}, {color}cc, {color}00)"
        elif overlay_type.startswith("radial"):
            gradient = f"radial-gradient(circle, {color}cc, {color}00)"
        return {
            "type": "rect", "subtype": "overlay",
            "x": x, "y": y, "width": w, "height": h,
            "backgroundColor": color if not gradient else "transparent",
            "gradient": gradient,
            "opacity": deco.get("opacity", 0.5),
            "borderRadius": 0,
            "borderColor": "transparent", "borderWidth": 0,
        }

    def _shape_elem(
        self, instr: Dict[str, Any],
        x: int, y: int, w: int, h: int,
        design_brief: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        deco = self._get_decoration_style(design_brief, "shape")
        fill_color = self._resolve_color_from_source(
            design_brief, deco.get("fill_source", "accent")
        )
        border_w = deco.get("border_width", 0)
        border_color = (
            self._resolve_color_from_source(
                design_brief, deco.get("border_color_source", "primary")
            )
            if border_w > 0 else "transparent"
        )
        return {
            "type": "rect", "subtype": instr.get("subtype", "rect"),
            "x": x, "y": y, "width": w, "height": h,
            "backgroundColor": instr.get("color", fill_color),
            "borderRadius": instr.get("border_radius", deco.get("border_radius", 0)),
            "borderColor": border_color,
            "borderWidth": border_w,
            "opacity": instr.get("opacity", deco.get("opacity", 0.9)),
            "gradient": "",
        }

    @staticmethod
    def _text_elem(
        instr: Dict[str, Any],
        x: int, y: int, w: int, h: int,
        font_style: str,
        role: str,
        default_size: int,
        default_color: str,
        default_weight: str,
        default_align: str,
    ) -> Dict[str, Any]:
        fs = int(instr.get("font_size", default_size))
        font = resolve_font(font_style, role=role)
        return {
            "type": "text",
            "x": x, "y": y, "width": w, "height": max(h, int(fs * 1.4)),
            "content": instr.get("content", ""),
            "fontSize": fs,
            "color": instr.get("color", default_color),
            "fontFamily": font["family"],
            "fontWeight": instr.get("font_weight", default_weight),
            "textAlign": instr.get("text_align", default_align),
        }

    # ------------------------------------------------------------------
    # 越界修正
    # ------------------------------------------------------------------

    def _clamp_bounds(self, elem: Dict[str, Any]) -> Dict[str, Any]:
        """确保元素不超出画布范围（背景图例外）"""
        if elem.get("layer_type") == "background":
            return elem

        margin = 20
        cw, ch = self.canvas_width, self.canvas_height

        x = max(margin, min(elem["x"], cw - margin))
        y = max(margin, min(elem["y"], ch - margin))
        w = min(elem["width"], cw - x - margin)
        h = min(elem["height"], ch - y - margin)

        elem.update({"x": x, "y": y, "width": max(w, 40), "height": max(h, 20)})
        return elem
