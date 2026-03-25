"""
渲染服务 - 统一入口

职责：
1. 协调 DSL 解析和 Schema 转换
2. 提供完整的渲染流程
"""

from typing import Dict, Any, List, Optional

from ...models.poster import PosterData, Canvas
from ...core.logger import get_logger
from .dsl_parser import DSLParser
from .schema_converter import SchemaConverter

logger = get_logger(__name__)


class RendererService:
    """渲染服务 — DSL 解析 + Schema 转换"""

    def __init__(self):
        self.dsl_parser = DSLParser()
        self.schema_converter = SchemaConverter()

    def parse_dsl_and_build_layout(
        self,
        dsl_instructions: List[Dict[str, Any]],
        canvas_width: int = 1080,
        canvas_height: int = 1920,
        design_brief: Optional[Dict[str, Any]] = None,
        font_style: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """解析 DSL 指令，返回元素字典列表"""
        return self.dsl_parser.parse(
            dsl_instructions=dsl_instructions,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            design_brief=design_brief,
            font_style=font_style,
        )

    def convert_to_pydantic_schema(
        self,
        elements: Optional[List[Dict[str, Any]]] = None,
        design_brief: Optional[Dict[str, Any]] = None,
        canvas_width: int = 1080,
        canvas_height: int = 1920,
    ) -> PosterData:
        """将元素列表转换为 PosterData"""
        if elements is None:
            raise ValueError("elements 不能为空，请先调用 parse_dsl_and_build_layout")
        return self.schema_converter.convert(
            elements, design_brief,
            canvas_width=canvas_width, canvas_height=canvas_height,
        )

    def merge_with_design_brief(
        self,
        poster_data: PosterData,
        design_brief: Dict[str, Any],
        asset_list: Optional[Dict[str, Any]] = None,
    ) -> PosterData:
        """合并设计数据"""
        return self.schema_converter.merge_with_design_brief(
            poster_data, design_brief, asset_list
        )


def create_simple_poster_from_text(
    title: str,
    subtitle: Optional[str] = None,
    image_url: Optional[str] = None,
    canvas_width: int = 1080,
    canvas_height: int = 1920,
) -> PosterData:
    """快速创建简单海报（无需 LLM）"""
    renderer = RendererService()

    instructions = [
        {
            "command": "add_title",
            "content": title,
            "font_size": 48,
            "x": 40, "y": int(canvas_height * 0.35),
            "width": canvas_width - 80, "height": 80,
        }
    ]

    if subtitle:
        instructions.append({
            "command": "add_subtitle",
            "content": subtitle,
            "font_size": 32,
            "x": 40, "y": int(canvas_height * 0.45),
            "width": canvas_width - 80, "height": 60,
        })

    if image_url:
        instructions.insert(0, {
            "command": "add_image",
            "src": image_url,
            "x": 0, "y": 0,
            "width": canvas_width, "height": canvas_height,
            "layer_type": "background",
        })

    elements = renderer.parse_dsl_and_build_layout(
        dsl_instructions=instructions,
        canvas_width=canvas_width,
        canvas_height=canvas_height,
    )

    return renderer.convert_to_pydantic_schema(
        elements, canvas_width=canvas_width, canvas_height=canvas_height,
    )
