"""
依赖注入模块 - 统一管理所有服务实例

职责：
1. 单例模式管理所有服务实例
2. 延迟初始化，避免启动时加载全部依赖
3. 支持测试时重置和 Mock
"""

from typing import Any, Callable, TypeVar
from functools import lru_cache

from .config import settings
from .logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")

# ============================================================================
# 通用单例缓存
# ============================================================================

_cache: dict[str, Any] = {}


def _get_or_create(key: str, factory: Callable[[], T]) -> T:
    """获取或创建单例实例"""
    if key not in _cache:
        logger.debug(f"创建 {key} 实例（单例）")
        _cache[key] = factory()
    return _cache[key]


# ============================================================================
# 知识模块依赖
# ============================================================================

def get_knowledge_graph():
    """获取知识图谱实例（单例）"""
    def _factory():
        from ..knowledge import DesignKnowledgeGraph
        return DesignKnowledgeGraph()
    return _get_or_create("knowledge_graph", _factory)


def get_knowledge_base():
    """获取品牌知识库实例（单例）"""
    def _factory():
        from ..knowledge import BrandKnowledgeBase
        return BrandKnowledgeBase()
    return _get_or_create("knowledge_base", _factory)


# ============================================================================
# 海报服务依赖
# ============================================================================

def get_poster_service():
    """获取海报服务实例（单例）"""
    def _factory():
        from ..services.poster_service import PosterService
        return PosterService()
    return _get_or_create("poster_service", _factory)


def reset_poster_service():
    """重置海报服务实例（用于测试）"""
    _cache.pop("poster_service", None)
    logger.debug("重置 PosterService 实例")


# ============================================================================
# 工作流依赖
# ============================================================================

def get_workflow():
    """获取工作流实例"""
    from ..workflow import app_workflow
    return app_workflow


# ============================================================================
# 配置依赖
# ============================================================================

@lru_cache(maxsize=1)
def get_settings():
    """获取配置实例（使用缓存确保单例）"""
    return settings


# ============================================================================
# Skills 依赖
# ============================================================================

def get_intent_parse_skill():
    """获取意图解析 Skill 实例（单例）"""
    def _factory():
        from ..skills import IntentParseSkill
        return IntentParseSkill()
    return _get_or_create("intent_parse_skill", _factory)


def get_design_rule_skill():
    """获取设计规则 Skill 实例（单例）"""
    def _factory():
        from ..skills import DesignRuleSkill
        return DesignRuleSkill(knowledge_graph=get_knowledge_graph())
    return _get_or_create("design_rule_skill", _factory)


def get_brand_context_skill():
    """获取品牌上下文 Skill 实例（单例）"""
    def _factory():
        from ..skills import BrandContextSkill
        return BrandContextSkill(knowledge_base=get_knowledge_base())
    return _get_or_create("brand_context_skill", _factory)


def get_design_brief_skill():
    """获取设计简报 Skill 实例（单例）"""
    def _factory():
        from ..skills import DesignBriefSkill
        return DesignBriefSkill()
    return _get_or_create("design_brief_skill", _factory)


# ============================================================================
# 测试辅助
# ============================================================================

def reset_skill_cache():
    """重置所有 Skill 实例（用于测试）"""
    for key in ["intent_parse_skill", "design_rule_skill", "brand_context_skill", "design_brief_skill"]:
        _cache.pop(key, None)
    logger.debug("已重置所有 Skill 实例")


def reset_all_services():
    """
    重置所有服务实例（用于测试）

    在测试中调用此函数可确保测试隔离。
    """
    _cache.clear()
    get_settings.cache_clear()
    logger.info("已重置所有服务、Skill 和配置缓存")
