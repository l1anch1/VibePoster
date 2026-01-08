"""
布局引擎 - 样式定义

Author: VibePoster Team
Date: 2025-01
"""

from typing import Optional, Literal
from dataclasses import dataclass


@dataclass
class Style:
    """样式配置"""
    font_size: int = 16
    font_family: str = "Arial"
    font_weight: Literal["normal", "bold"] = "normal"
    color: str = "#000000"
    text_align: Literal["left", "center", "right"] = "left"
    background_color: Optional[str] = None
    opacity: float = 1.0
    rotation: float = 0.0

