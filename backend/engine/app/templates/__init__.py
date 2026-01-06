"""
海报风格模板模块

提供预定义的海报风格模板，包括：
- Business（商务）
- Campus（校园）
- Event（活动）
- Product（产品推广）
- Festival（节日）
"""

from .models import (
    StyleTemplate,
    ColorScheme,
    FontRecommendation,
    LayoutRule,
    StylePreference,
)
from .manager import TemplateManager
from .templates import STYLE_TEMPLATES

__all__ = [
    "StyleTemplate",
    "ColorScheme",
    "FontRecommendation",
    "LayoutRule",
    "StylePreference",
    "TemplateManager",
    "STYLE_TEMPLATES",
]

