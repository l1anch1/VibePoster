"""
统一 API 响应模型

所有 API 都使用统一的响应格式，便于前端处理。

职责：
1. 定义通用 API 响应格式
2. 定义所有响应数据模型
3. 定义错误响应模型

Author: VibePoster Team
Date: 2025-01
"""

from typing import TypeVar, Generic, Optional, Any, List, Dict
from pydantic import BaseModel, Field

from .poster import PosterData

T = TypeVar('T')


# ============================================================================
# 通用响应模型
# ============================================================================

class APIResponse(BaseModel, Generic[T]):
    """
    统一 API 响应模型
    
    格式：
    {
        "success": true,
        "data": { ... },
        "message": "操作成功"
    }
    """
    success: bool = Field(default=True, description="操作是否成功")
    data: Optional[T] = Field(default=None, description="响应数据")
    message: str = Field(default="操作成功", description="响应消息")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = Field(default=False, description="请求是否成功")
    error: str = Field(..., description="错误类型")
    message: str = Field(default="", description="错误消息")
    detail: Optional[Dict[str, Any]] = Field(default=None, description="详细错误信息")


# ============================================================================
# 海报相关响应模型
# ============================================================================

class PosterGenerateResponse(BaseModel):
    """海报生成成功响应"""
    
    success: bool = Field(default=True, description="请求是否成功")
    data: PosterData = Field(..., description="生成的海报数据")
    message: str = Field(default="海报生成成功", description="响应消息")


class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    
    status: str = Field(default="healthy", description="服务状态")
    version: str = Field(default="1.0.0", description="API 版本")


# ============================================================================
# 知识模块响应数据模型
# ============================================================================

class KGInferResult(BaseModel):
    """KG 推理结果"""
    keywords: List[str] = Field(..., description="输入的关键词")
    rules: dict = Field(..., description="推理出的规则")


class BrandSearchResult(BaseModel):
    """品牌知识检索结果"""
    query: str = Field(..., description="查询文本")
    results: List[dict] = Field(..., description="检索结果列表")
    count: int = Field(..., description="结果数量")


class BrandUploadResult(BaseModel):
    """品牌文档上传结果"""
    doc_id: str = Field(..., description="文档 ID")
    brand_name: str = Field(..., description="品牌名称")
    category: str = Field(..., description="文档类别")
    text_length: int = Field(..., description="文档长度")


class StatsResult(BaseModel):
    """统计信息结果"""
    total_documents: Optional[int] = None
    backend: Optional[str] = None
    model_available: Optional[bool] = None
    chromadb_available: Optional[bool] = None
    node_count: Optional[int] = None
    edge_count: Optional[int] = None
