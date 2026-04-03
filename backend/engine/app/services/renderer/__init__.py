"""
渲染服务模块

包含：
- LayoutBuilder: OOP 布局引擎桥接器（核心）
- DSLParser: 兼容性入口（委托 LayoutBuilder）
- SchemaConverter: 元素字典 → Pydantic Schema 转换器
- RendererService: 统一渲染服务入口
"""

from .layout_builder import LayoutBuilder, STRATEGIES, VALID_STRATEGIES
from .dsl_parser import DSLParser
from .schema_converter import SchemaConverter
from .service import RendererService, create_simple_poster_from_text

__all__ = [
    "LayoutBuilder",
    "STRATEGIES",
    "VALID_STRATEGIES",
    "DSLParser",
    "SchemaConverter",
    "RendererService",
    "create_simple_poster_from_text",
]
