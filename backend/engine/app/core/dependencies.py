"""
依赖注入模块 - 统一管理所有服务实例

职责：
1. 单例模式管理所有服务实例
2. 延迟初始化，避免启动时加载全部依赖
3. 支持测试时重置和 Mock

Author: VibePoster Team
Date: 2025-01
"""

from typing import Optional
from functools import lru_cache

from .config import settings
from .logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# 服务实例存储（单例）
# ============================================================================

class ServiceContainer:
    """服务容器 - 统一管理所有服务实例"""
    
    _poster_service = None
    _knowledge_service = None
    _knowledge_graph = None
    _knowledge_base = None
    _renderer_service = None
    
    @classmethod
    def reset_all(cls):
        """重置所有服务实例（用于测试）"""
        cls._poster_service = None
        cls._knowledge_service = None
        cls._knowledge_graph = None
        cls._knowledge_base = None
        cls._renderer_service = None
        logger.debug("已重置所有服务实例")


# ============================================================================
# 知识模块依赖
# ============================================================================

def get_knowledge_graph():
    """
    获取知识图谱实例（单例）
    
    Returns:
        DesignKnowledgeGraph 实例
    """
    if ServiceContainer._knowledge_graph is None:
        from ..knowledge import DesignKnowledgeGraph
        logger.debug("创建 DesignKnowledgeGraph 实例（单例）")
        ServiceContainer._knowledge_graph = DesignKnowledgeGraph()
    return ServiceContainer._knowledge_graph


def get_knowledge_base():
    """
    获取品牌知识库实例（单例）
    
    Returns:
        BrandKnowledgeBase 实例
    """
    if ServiceContainer._knowledge_base is None:
        from ..knowledge import BrandKnowledgeBase
        logger.debug("创建 BrandKnowledgeBase 实例（单例）")
        ServiceContainer._knowledge_base = BrandKnowledgeBase()
    return ServiceContainer._knowledge_base


def get_knowledge_service():
    """
    获取知识服务实例（单例）
    
    KnowledgeService 统一管理 KG 和 RAG。
    
    Returns:
        KnowledgeService 实例
    """
    if ServiceContainer._knowledge_service is None:
        from ..services.knowledge_service import KnowledgeService
        logger.debug("创建 KnowledgeService 实例（单例）")
        ServiceContainer._knowledge_service = KnowledgeService(
            knowledge_graph=get_knowledge_graph(),
            knowledge_base=get_knowledge_base()
        )
    return ServiceContainer._knowledge_service


# ============================================================================
# 渲染服务依赖
# ============================================================================

def get_renderer_service():
    """
    获取渲染服务实例（单例）
    
    Returns:
        RendererService 实例
    """
    if ServiceContainer._renderer_service is None:
        from ..services.renderer import RendererService
        logger.debug("创建 RendererService 实例（单例）")
        ServiceContainer._renderer_service = RendererService()
    return ServiceContainer._renderer_service


# ============================================================================
# 海报服务依赖
# ============================================================================

def get_poster_service():
    """
    获取海报服务实例（单例）
    
    Returns:
        PosterService 实例
    """
    if ServiceContainer._poster_service is None:
        from ..services import PosterService
        logger.debug("创建 PosterService 实例（单例）")
        ServiceContainer._poster_service = PosterService()
    return ServiceContainer._poster_service


def reset_poster_service():
    """重置海报服务实例（用于测试）"""
    ServiceContainer._poster_service = None
    logger.debug("重置 PosterService 实例")


# ============================================================================
# 工作流依赖
# ============================================================================

def get_workflow():
    """
    获取工作流实例
    
    Returns:
        编译后的 LangGraph 工作流
    """
    from ..workflow import app_workflow
    return app_workflow


# ============================================================================
# 配置依赖
# ============================================================================

@lru_cache(maxsize=1)
def get_settings():
    """
    获取配置实例（使用缓存确保单例）
    
    Returns:
        GlobalSettings 实例
    """
    return settings


# ============================================================================
# 测试辅助
# ============================================================================

def reset_all_services():
    """
    重置所有服务实例（用于测试）
    
    在测试中调用此函数可确保测试隔离。
    """
    ServiceContainer.reset_all()
    get_settings.cache_clear()
    logger.info("已重置所有服务和配置缓存")
