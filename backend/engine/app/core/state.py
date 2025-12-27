"""
状态定义 - AgentState 和 PosterSchema
防止循环引用
"""
from typing import TypedDict, Optional, List, Literal, Union, Dict, Any
from pydantic import BaseModel


# === LangGraph 状态定义 ===

class AgentState(TypedDict, total=False):
    """工作流状态定义"""
    user_prompt: str
    chat_history: Optional[List[Dict[str, str]]]  # 多轮对话历史
    user_images: Optional[List[Dict[str, Any]]]  # 用户上传的图片列表 [{"type": "person"|"background", "data": bytes}]
    design_brief: Dict[str, Any]  # 设计简报
    asset_list: Optional[Dict[str, Any]]  # 资产列表（背景图、前景图等）
    selected_asset: Optional[str]  # 兼容旧字段
    final_poster: Dict[str, Any]  # 最终海报数据
    review_feedback: Optional[Dict[str, Any]]  # 审核反馈
    _retry_count: int  # 重试计数器


# === Pydantic Schema 定义 ===

class BaseLayer(BaseModel):
    """基础图层"""
    id: str
    name: str
    type: Literal["text", "image"]
    x: int
    y: int
    width: int
    height: int
    rotation: int = 0
    opacity: float = 1.0
    z_index: int = 0  # 图层顺序


class TextLayer(BaseLayer):
    """文本图层"""
    type: Literal["text"]
    content: str
    fontSize: int
    color: str
    fontFamily: str = "Yuanti TC"
    textAlign: str = "left"
    fontWeight: str = "normal"


class ImageLayer(BaseLayer):
    """图片图层"""
    type: Literal["image"]
    src: str


class Canvas(BaseModel):
    """画布配置"""
    width: int = 1080
    height: int = 1920
    backgroundColor: str = "#FFFFFF"


class PosterData(BaseModel):
    """海报数据"""
    canvas: Canvas
    layers: List[Union[TextLayer, ImageLayer]]


# === 图像分析结果 Schema ===

class ImageAnalysisResult(BaseModel):
    """图像分析结果"""
    processed_image_path: Optional[str] = None  # 处理后的图片路径（本地）
    processed_image_base64: Optional[str] = None  # 处理后的图片 Base64
    width: int
    height: int
    main_color: str  # Hex 颜色
    subject_bbox: Optional[List[int]] = None  # [x1, y1, x2, y2] 主体边界框


# === Asset List Schema ===

class AssetLayer(BaseModel):
    """资产图层"""
    type: Literal["image"]
    src: str
    source_type: Literal["user_upload", "stock", "generated"]
    width: Optional[int] = None
    height: Optional[int] = None
    suggested_position: Optional[str] = None  # 建议位置


class AssetList(BaseModel):
    """资产列表"""
    background_layer: AssetLayer
    foreground_layer: Optional[AssetLayer] = None


# === Review Feedback Schema ===

class ReviewFeedback(BaseModel):
    """审核反馈"""
    status: Literal["PASS", "REJECT"]
    feedback: str
    issues: Optional[List[str]] = None  # 问题列表
