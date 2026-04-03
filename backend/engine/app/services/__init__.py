"""
Services 模块 - 业务逻辑层

服务类：
- PosterService: 海报一次性生成服务（MCP Server 调用）
- RendererService: OOP 布局渲染服务

知识服务已迁移至 Skills 模块。
"""

from .renderer import RendererService, create_simple_poster_from_text


def get_poster_service_class():
    """延迟导入 PosterService，避免循环引用"""
    from .poster_service import PosterService
    return PosterService


def get_asset_service():
    """延迟导入 AssetService，避免加载 tools 层的重量级依赖"""
    from .asset_service import AssetService, AssetResult
    return AssetService, AssetResult


__all__ = [
    "get_poster_service_class",
    "get_asset_service",
    "RendererService",
    "create_simple_poster_from_text",
]
