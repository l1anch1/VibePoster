"""
布局引擎 - 元素定义

包含：
- Element: 抽象基类
- TextBlock: 文本块组件
- ImageBlock: 图片块组件

Author: VibePoster Team
Date: 2025-01
"""

from typing import Dict, Any, Optional, TYPE_CHECKING
from abc import ABC, abstractmethod
import math

from .styles import Style

if TYPE_CHECKING:
    from .containers import Container


class Element(ABC):
    """
    抽象基类 - 所有布局元素的基类
    
    属性：
        x, y: 元素的绝对位置
        width, height: 元素的尺寸
        z_index: 层级
        style: 样式配置
    """
    
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        width: float = 100,
        height: float = 100,
        z_index: int = 0,
        style: Optional[Style] = None
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.z_index = z_index
        self.style = style or Style()
        self._parent: Optional['Container'] = None
    
    @abstractmethod
    def render(self) -> Dict[str, Any]:
        """
        渲染元素为字典（用于生成 PSD/JSON）
        
        Returns:
            元素的字典表示
        """
        pass
    
    def set_position(self, x: float, y: float):
        """设置元素位置"""
        self.x = x
        self.y = y
    
    def get_bounds(self) -> Dict[str, float]:
        """获取元素的边界框"""
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "right": self.x + self.width,
            "bottom": self.y + self.height
        }
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(x={self.x}, y={self.y}, w={self.width}, h={self.height})"


class TextBlock(Element):
    """
    文本块组件
    
    自动根据文本内容、字体大小、最大宽度计算高度
    """
    
    def __init__(
        self,
        content: str,
        font_size: int = 16,
        max_width: float = 400,
        line_height: float = 1.5,
        x: float = 0,
        y: float = 0,
        z_index: int = 0,
        style: Optional[Style] = None
    ):
        """
        初始化文本块
        
        Args:
            content: 文本内容
            font_size: 字体大小（px）
            max_width: 最大宽度
            line_height: 行高倍数
            x, y: 初始位置
            z_index: 层级
            style: 样式配置
        """
        self.content = content
        self.font_size = font_size
        self.max_width = max_width
        self.line_height = line_height
        
        # 自动计算高度
        calculated_height = self.calculate_height()
        
        # 初始化基类
        super().__init__(
            x=x,
            y=y,
            width=max_width,
            height=calculated_height,
            z_index=z_index,
            style=style or Style(font_size=font_size)
        )
    
    def calculate_height(self) -> float:
        """
        根据文本内容和字体大小自动计算高度
        
        算法：
        1. 估算每个字符的平均宽度（约为 font_size * 0.6）
        2. 计算总宽度
        3. 除以 max_width 得到行数
        4. 乘以 line_height 和 font_size 得到总高度
        
        Returns:
            计算后的高度
        """
        if not self.content:
            return self.font_size * self.line_height
        
        # 估算字符宽度（中文约等于字体大小，英文约为字体大小的 0.6）
        # 简化处理：统一使用 0.7 作为平均值
        avg_char_width = self.font_size * 0.7
        
        # 计算总宽度
        total_width = len(self.content) * avg_char_width
        
        # 计算行数（向上取整）
        line_count = math.ceil(total_width / self.max_width)
        
        # 计算总高度
        total_height = line_count * self.font_size * self.line_height
        
        return total_height
    
    def render(self) -> Dict[str, Any]:
        """渲染为字典"""
        return {
            "type": "text",
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "content": self.content,
            "fontSize": self.style.font_size,
            "fontFamily": self.style.font_family,
            "fontWeight": self.style.font_weight,
            "color": self.style.color,
            "textAlign": self.style.text_align,
            "opacity": self.style.opacity,
            "rotation": self.style.rotation,
            "z_index": self.z_index
        }
    
    def update_content(self, new_content: str):
        """
        更新文本内容并重新计算高度
        
        这是动态布局的关键：内容变化时自动调整高度
        """
        self.content = new_content
        self.height = self.calculate_height()
        
        # 通知父容器重新排列
        if self._parent:
            self._parent.arrange()


class ImageBlock(Element):
    """
    图片块组件
    """
    
    def __init__(
        self,
        src: str,
        width: float,
        height: float,
        x: float = 0,
        y: float = 0,
        z_index: int = 0,
        maintain_aspect_ratio: bool = True,
        style: Optional[Style] = None
    ):
        """
        初始化图片块
        
        Args:
            src: 图片源（URL 或 Base64）
            width: 宽度
            height: 高度
            x, y: 初始位置
            z_index: 层级
            maintain_aspect_ratio: 是否保持宽高比
            style: 样式配置
        """
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            z_index=z_index,
            style=style or Style()
        )
        self.src = src
        self.maintain_aspect_ratio = maintain_aspect_ratio
    
    def render(self) -> Dict[str, Any]:
        """渲染为字典"""
        return {
            "type": "image",
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "src": self.src,
            "opacity": self.style.opacity,
            "rotation": self.style.rotation,
            "z_index": self.z_index
        }
    
    def resize(self, width: float, height: Optional[float] = None):
        """
        调整图片大小
        
        Args:
            width: 新宽度
            height: 新高度（如果为 None 且 maintain_aspect_ratio=True，则自动计算）
        """
        if height is None and self.maintain_aspect_ratio:
            aspect_ratio = self.height / self.width
            height = width * aspect_ratio
        
        self.width = width
        self.height = height or self.height
        
        # 通知父容器重新排列
        if self._parent:
            self._parent.arrange()

