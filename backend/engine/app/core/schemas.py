"""
数据结构定义 - Pydantic Schema
用于 API 接口响应和 LLM 结构化输出校验
"""

from typing import List, Literal, Union, Optional
from pydantic import BaseModel, Field


class BaseLayer(BaseModel):
    """基础图层公用属性"""

    id: str
    name: str = "Layer"
    # 允许 text, image, rect (形状)
    type: Literal["text", "image", "rect"]
    x: int = 0
    y: int = 0
    # ⚠️ 关键修改：设置默认值为 0，防止 LLM 没返回时报错
    width: int = 0
    height: int = 0
    rotation: int = 0
    opacity: float = 1.0
    z_index: int = 0  # 图层顺序（背景=0, 前景=1, 文字=2）


class TextLayer(BaseLayer):
    """文本图层"""

    type: Literal["text"]
    content: str
    fontSize: int = 24  # 给默认值
    color: str = "#000000"
    fontFamily: str = "Yuanti TC"
    textAlign: str = "left"
    fontWeight: str = "normal"


class ImageLayer(BaseLayer):
    """图片图层"""

    type: Literal["image"]
    src: str = ""  # 给默认值


class ShapeLayer(BaseLayer):
    """
    [新增] 形状图层
    用于兼容 LLM 生成的遮罩(overlay)或线条(rect)
    """

    type: Literal["rect"]
    backgroundColor: str = "transparent"  # 形状填充色


class Canvas(BaseModel):
    """画布配置"""

    width: int = 1080
    height: int = 1920
    backgroundColor: str = "#FFFFFF"


class PosterData(BaseModel):
    """最终海报数据结构"""

    canvas: Canvas
    # 加入 ShapeLayer 支持
    layers: List[Union[TextLayer, ImageLayer, ShapeLayer]]


# 注意：工作流内部使用的数据结构（如 asset_list, review_feedback 等）
# 目前使用 Dict[str, Any] 传递，未定义专门的 Pydantic Schema
# 如果未来需要类型验证或 API 文档，可以在此处添加相应的 Schema
