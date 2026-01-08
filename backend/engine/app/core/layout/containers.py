"""
布局引擎 - 容器定义

包含：
- Container: 容器基类
- VerticalContainer: 垂直布局容器
- HorizontalContainer: 水平布局容器

Author: VibePoster Team
Date: 2025-01
"""

from typing import List, Dict, Any, Optional
from abc import abstractmethod

from .styles import Style
from .elements import Element


class Container(Element):
    """
    容器基类
    
    可以包含多个子元素，并负责排列它们的位置
    """
    
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        width: float = 400,
        height: float = 600,
        padding: float = 0,
        gap: float = 0,
        z_index: int = 0,
        style: Optional[Style] = None
    ):
        """
        初始化容器
        
        Args:
            x, y: 容器位置
            width, height: 容器尺寸
            padding: 内边距
            gap: 子元素间距
            z_index: 层级
            style: 样式配置
        """
        super().__init__(x, y, width, height, z_index, style)
        self.elements: List[Element] = []
        self.padding = padding
        self.gap = gap
    
    def add(self, element: Element) -> 'Container':
        """
        添加子元素
        
        Args:
            element: 要添加的元素
        
        Returns:
            self（支持链式调用）
        """
        element._parent = self
        self.elements.append(element)
        return self
    
    def remove(self, element: Element):
        """移除子元素"""
        if element in self.elements:
            element._parent = None
            self.elements.remove(element)
    
    def clear(self):
        """清空所有子元素"""
        for element in self.elements:
            element._parent = None
        self.elements.clear()
    
    @abstractmethod
    def arrange(self):
        """
        排列子元素（抽象方法，由子类实现）
        
        这是动态布局的核心：根据容器类型自动计算子元素位置
        """
        pass
    
    def render(self) -> Dict[str, Any]:
        """渲染容器及其所有子元素"""
        return {
            "type": "container",
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "padding": self.padding,
            "gap": self.gap,
            "elements": [element.render() for element in self.elements]
        }
    
    def get_all_elements(self) -> List[Dict[str, Any]]:
        """获取所有子元素的扁平列表（用于导出）"""
        result = []
        for element in self.elements:
            if isinstance(element, Container):
                result.extend(element.get_all_elements())
            else:
                result.append(element.render())
        return result


class VerticalContainer(Container):
    """
    垂直布局容器
    
    子元素从上到下依次排列，自动计算每个元素的 y 坐标
    """
    
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        width: float = 400,
        padding: float = 20,
        gap: float = 10,
        z_index: int = 0,
        style: Optional[Style] = None
    ):
        """
        初始化垂直容器
        
        Args:
            x, y: 容器位置
            width: 容器宽度
            padding: 内边距
            gap: 子元素垂直间距
            z_index: 层级
            style: 样式配置
        """
        # 初始高度为 0，将在 arrange() 中自动计算
        super().__init__(x, y, width, 0, padding, gap, z_index, style)
    
    def arrange(self):
        """
        垂直排列所有子元素
        
        算法：
        1. 从 padding 开始
        2. 遍历每个子元素
        3. 设置子元素的 x = container.x + padding
        4. 设置子元素的 y = current_y
        5. current_y += element.height + gap
        6. 更新容器总高度
        """
        if not self.elements:
            self.height = 2 * self.padding
            return
        
        current_y = self.y + self.padding
        max_width = 0
        
        for i, element in enumerate(self.elements):
            # 设置子元素的 x（居中或左对齐）
            element_x = self.x + self.padding
            
            # 如果子元素宽度小于容器宽度，可以选择居中
            available_width = self.width - 2 * self.padding
            if element.width < available_width:
                # 居中对齐
                element_x = self.x + self.padding + (available_width - element.width) / 2
            
            # 设置子元素的 y
            element.set_position(element_x, current_y)
            
            # 更新 current_y
            current_y += element.height
            
            # 添加间距（最后一个元素不加）
            if i < len(self.elements) - 1:
                current_y += self.gap
            
            # 追踪最大宽度
            max_width = max(max_width, element.width)
        
        # 更新容器的总高度
        self.height = current_y - self.y + self.padding


class HorizontalContainer(Container):
    """
    水平布局容器
    
    子元素从左到右依次排列
    """
    
    def arrange(self):
        """水平排列所有子元素"""
        if not self.elements:
            self.width = 2 * self.padding
            return
        
        current_x = self.x + self.padding
        max_height = 0
        
        for i, element in enumerate(self.elements):
            # 设置子元素的位置
            element.set_position(current_x, self.y + self.padding)
            
            # 更新 current_x
            current_x += element.width
            
            # 添加间距（最后一个元素不加）
            if i < len(self.elements) - 1:
                current_x += self.gap
            
            # 追踪最大高度
            max_height = max(max_height, element.height)
        
        # 更新容器的总宽度和高度
        self.width = current_x - self.x + self.padding
        self.height = max_height + 2 * self.padding

