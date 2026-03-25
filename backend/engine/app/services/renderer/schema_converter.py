"""
Schema 转换器 - 元素字典列表 → Pydantic PosterData

职责：
1. 将解析后的元素列表转换为 Pydantic 图层
2. 创建 PosterData 对象
3. 合并设计数据
"""

from typing import Dict, Any, List, Optional, Union

from ...models.poster import (
    PosterData,
    Canvas,
    TextLayer,
    ImageLayer,
    ShapeLayer,
)
from ...core.logger import get_logger
from .font_registry import resolve_font, DEFAULT_FONT_STYLE

logger = get_logger(__name__)


class SchemaConverter:
    """将 DSLParser 输出的元素字典列表转换为 PosterData"""

    def convert(
        self,
        elements: List[Dict[str, Any]],
        design_brief: Optional[Dict[str, Any]] = None,
        canvas_width: int = 1080,
        canvas_height: int = 1920,
    ) -> PosterData:
        logger.info("🔄 转换为 Pydantic Schema...")

        layers: List[Union[TextLayer, ImageLayer, ShapeLayer]] = []

        for i, elem in enumerate(elements):
            try:
                layer = self._convert_element_to_layer(elem, i)
                if layer:
                    layers.append(layer)
            except Exception as e:
                logger.error(f"转换图层 {i} 失败: {e}")

        bg_color = (design_brief or {}).get("background_color", "#FFFFFF")
        canvas = Canvas(
            width=canvas_width,
            height=canvas_height,
            backgroundColor=bg_color,
        )

        poster_data = PosterData(canvas=canvas, layers=layers)
        logger.info(f"✅ 转换完成，共 {len(layers)} 个图层")
        return poster_data

    def _convert_element_to_layer(
        self, elem: Dict[str, Any], index: int
    ) -> Optional[Union[TextLayer, ImageLayer, ShapeLayer]]:
        elem_type = elem.get("type")
        layer_id = f"{elem_type}_{index}"

        base_attrs = {
            "id": layer_id,
            "name": f"{elem_type.capitalize()} {index}",
            "type": elem_type,
            "x": int(elem.get("x", 0)),
            "y": int(elem.get("y", 0)),
            "width": int(elem.get("width", 0)),
            "height": int(elem.get("height", 0)),
            "rotation": int(elem.get("rotation", 0)),
            "opacity": float(elem.get("opacity", 1.0)),
        }

        if elem_type == "text":
            font_family = elem.get("fontFamily")
            if not font_family:
                font_family = resolve_font(DEFAULT_FONT_STYLE, role="body")["family"]
            return TextLayer(
                **base_attrs,
                content=elem.get("content", ""),
                fontSize=int(elem.get("fontSize", 24)),
                color=elem.get("color", "#000000"),
                fontFamily=font_family,
                textAlign=elem.get("textAlign", "left"),
                fontWeight=elem.get("fontWeight", "normal"),
            )

        if elem_type == "image":
            return ImageLayer(**base_attrs, src=elem.get("src", ""))

        if elem_type == "rect":
            return ShapeLayer(
                **base_attrs,
                backgroundColor=elem.get("backgroundColor", "transparent"),
            )

        logger.warning(f"未知元素类型: {elem_type}")
        return None

    def merge_with_design_brief(
        self,
        poster_data: PosterData,
        design_brief: Dict[str, Any],
        asset_list: Optional[Dict[str, Any]] = None,
    ) -> PosterData:
        logger.info("🔗 合并设计数据...")

        if "background_color" in design_brief:
            poster_data.canvas.backgroundColor = design_brief["background_color"]

        for layer in poster_data.layers:
            if layer.type == "image" and not layer.src and asset_list:
                if "background_layer" in asset_list:
                    layer.src = asset_list["background_layer"].get("src", "")
                elif "subject_layer" in asset_list:
                    layer.src = asset_list["subject_layer"].get("src", "")

        logger.info("✅ 数据合并完成")
        return poster_data
