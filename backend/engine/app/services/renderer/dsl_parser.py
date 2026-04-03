"""
DSL 解析器 — 委托 OOP 布局引擎计算坐标

保留 DSLParser 类名以兼容已有导入路径，内部完全委托 LayoutBuilder。
坐标不再从 LLM 输出中读取，而是由 OOP 容器 arrange() 动态计算。
"""

from typing import Dict, Any, List, Optional

from ...core.logger import get_logger
from .layout_builder import LayoutBuilder

logger = get_logger(__name__)


class DSLParser:
    """DSL 解析器（OOP 布局模式）— 委托 LayoutBuilder"""

    def __init__(self) -> None:
        self._builder = LayoutBuilder()

    def parse(
        self,
        dsl_instructions: List[Dict[str, Any]],
        layout_strategy: str = "centered",
        canvas_width: int = 1080,
        canvas_height: int = 1920,
        design_brief: Optional[Dict[str, Any]] = None,
        font_style: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """解析 DSL 指令并通过 OOP 布局引擎计算坐标。"""
        return self._builder.build(
            dsl_instructions=dsl_instructions,
            layout_strategy=layout_strategy,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            design_brief=design_brief,
            font_style=font_style,
        )
