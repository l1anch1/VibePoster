"""
海报数据模型定义

用于 API 接口响应和 LLM 结构化输出校验。

Author: VibePoster Team
Date: 2025-01
"""

from typing import List, Literal, Union
from pydantic import BaseModel


class BaseLayer(BaseModel):
    """基础图层公用属性"""

    id: str
    name: str = "Layer"
    type: Literal["text", "image", "rect"]
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    rotation: int = 0
    opacity: float = 1.0
    z_index: int = 0


class TextLayer(BaseLayer):
    """文本图层"""

    type: Literal["text"]
    content: str
    fontSize: int = 24
    color: str = "#000000"
    fontFamily: str = "Yuanti TC"
    textAlign: str = "left"
    fontWeight: str = "normal"


class ImageLayer(BaseLayer):
    """图片图层"""

    type: Literal["image"]
    src: str = ""


class ShapeLayer(BaseLayer):
    """形状图层"""

    type: Literal["rect"]
    backgroundColor: str = "transparent"


class Canvas(BaseModel):
    """画布配置"""

    width: int = 1080
    height: int = 1920
    backgroundColor: str = "#FFFFFF"


class PosterData(BaseModel):
    """最终海报数据结构"""

    canvas: Canvas
    layers: List[Union[TextLayer, ImageLayer, ShapeLayer]]

