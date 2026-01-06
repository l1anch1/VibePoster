"""
依赖注入模块
提供统一的依赖注入管理，支持单例模式和生命周期管理
"""
from typing import Optional
from functools import lru_cache

from ..services import PosterService
from ..workflow import app_workflow
from .config import settings
from .logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# 服务实例管理（单例模式）
# ============================================================================

# 应用级别的服务实例（单例）
_poster_service_instance: Optional[PosterService] = None


def get_poster_service() -> PosterService:
    """
    获取海报服务实例（单例模式）
    
    使用单例模式确保整个应用只有一个服务实例，避免重复创建。
    这对于需要共享状态或资源的服务特别有用。
    
    Returns:
        PosterService: 海报服务实例
    """
    global _poster_service_instance
    
    if _poster_service_instance is None:
        logger.debug("创建 PosterService 实例（单例）")
        _poster_service_instance = PosterService()
    
    return _poster_service_instance


def reset_poster_service():
    """
    重置服务实例（主要用于测试）
    
    在测试中，可能需要重置服务实例以确保测试隔离。
    """
    global _poster_service_instance
    _poster_service_instance = None
    logger.debug("重置 PosterService 实例")


# ============================================================================
# 工作流依赖
# ============================================================================

def get_workflow():
    """
    获取工作流实例
    
    Returns:
        工作流实例
    """
    return app_workflow


# ============================================================================
# 配置依赖
# ============================================================================

@lru_cache(maxsize=1)
def get_settings():
    """
    获取配置实例（使用缓存确保单例）
    
    Returns:
        GlobalSettings: 全局配置实例
    """
    return settings

