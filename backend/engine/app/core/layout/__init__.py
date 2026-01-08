"""
布局引擎模块 - OOP 动态布局

提供"容器+组件"的流式布局逻辑（类似简易的 CSS Flexbox）。

核心思想：
    元素的位置不是写死的，而是由容器自动计算的。
    当文字变长时，下方的图片应该自动被推下去。

使用示例：
    from app.core.layout import VerticalContainer, TextBlock, ImageBlock, Style
    
    container = VerticalContainer(width=1080, padding=40, gap=20)
    container.add(TextBlock(content="标题", font_size=48))
    container.add(ImageBlock(src="...", width=800, height=600))
    container.arrange()
    
    # 导出
    elements = container.get_all_elements()

Author: VibePoster Team
Date: 2025-01
"""

from .styles import Style
from .elements import Element, TextBlock, ImageBlock
from .containers import Container, VerticalContainer, HorizontalContainer

__all__ = [
    "Style",
    "Element",
    "TextBlock",
    "ImageBlock",
    "Container",
    "VerticalContainer",
    "HorizontalContainer",
]

