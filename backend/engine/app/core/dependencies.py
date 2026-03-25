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
    _knowledge_graph = None
    _knowledge_base = None
    @classmethod
    def reset_all(cls):
        """重置所有服务实例（用于测试）"""
        cls._poster_service = None
        cls._knowledge_graph = None
        cls._knowledge_base = None
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
        from ..services.poster_service import PosterService
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
# Skills 依赖
# ============================================================================

class SkillContainer:
    """Skill 容器 - 统一管理所有 Skill 实例"""
    
    _intent_parse_skill = None
    _design_rule_skill = None
    _brand_context_skill = None
    _design_brief_skill = None
    
    @classmethod
    def reset_all(cls):
        """重置所有 Skill 实例"""
        cls._intent_parse_skill = None
        cls._design_rule_skill = None
        cls._brand_context_skill = None
        cls._design_brief_skill = None
        logger.debug("已重置所有 Skill 实例")


def get_intent_parse_skill():
    """
    获取意图解析 Skill 实例（单例）
    
    Returns:
        IntentParseSkill 实例
    """
    if SkillContainer._intent_parse_skill is None:
        from ..skills import IntentParseSkill
        logger.debug("创建 IntentParseSkill 实例（单例）")
        SkillContainer._intent_parse_skill = IntentParseSkill()
    return SkillContainer._intent_parse_skill


def get_design_rule_skill():
    """
    获取设计规则 Skill 实例（单例）
    
    Returns:
        DesignRuleSkill 实例
    """
    if SkillContainer._design_rule_skill is None:
        from ..skills import DesignRuleSkill
        logger.debug("创建 DesignRuleSkill 实例（单例）")
        SkillContainer._design_rule_skill = DesignRuleSkill(
            knowledge_graph=get_knowledge_graph()
        )
    return SkillContainer._design_rule_skill


def get_brand_context_skill():
    """
    获取品牌上下文 Skill 实例（单例）
    
    Returns:
        BrandContextSkill 实例
    """
    if SkillContainer._brand_context_skill is None:
        from ..skills import BrandContextSkill
        logger.debug("创建 BrandContextSkill 实例（单例）")
        SkillContainer._brand_context_skill = BrandContextSkill(
            knowledge_base=get_knowledge_base()
        )
    return SkillContainer._brand_context_skill


def get_design_brief_skill():
    """
    获取设计简报 Skill 实例（单例）
    
    Returns:
        DesignBriefSkill 实例
    """
    if SkillContainer._design_brief_skill is None:
        from ..skills import DesignBriefSkill
        logger.debug("创建 DesignBriefSkill 实例（单例）")
        SkillContainer._design_brief_skill = DesignBriefSkill()
    return SkillContainer._design_brief_skill


# ============================================================================
# 测试辅助
# ============================================================================

def reset_all_services():
    """
    重置所有服务实例（用于测试）
    
    在测试中调用此函数可确保测试隔离。
    """
    ServiceContainer.reset_all()
    SkillContainer.reset_all()
    get_settings.cache_clear()
    logger.info("已重置所有服务、Skill 和配置缓存")
