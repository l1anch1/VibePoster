"""
Models 模块 - 领域数据模型

包含：
- poster.py: 海报相关数据模型（PosterData, Canvas, Layer 等）
- response.py: 统一 API 响应模型（APIResponse, ErrorResponse 等）
- design_brief.py: 设计简报与素材列表模型
"""

from .poster import (
    BaseLayer,
    TextLayer,
    ImageLayer,
    ShapeLayer,
    Canvas,
    PosterData,
)
from .response import (
    APIResponse,
    ErrorResponse,
    HealthCheckResponse,
    KGInferResult,
    BrandSearchResult,
    BrandUploadResult,
    StatsResult,
)
from .design_brief import (
    DesignBrief,
    AssetLayer,
    AssetList,
)

__all__ = [
    # Poster models
    "BaseLayer",
    "TextLayer",
    "ImageLayer",
    "ShapeLayer",
    "Canvas",
    "PosterData",
    # Response models
    "APIResponse",
    "ErrorResponse",
    "HealthCheckResponse",
    "KGInferResult",
    "BrandSearchResult",
    "BrandUploadResult",
    "StatsResult",
    # Design brief models
    "DesignBrief",
    "AssetLayer",
    "AssetList",
]

