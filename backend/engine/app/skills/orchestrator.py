"""
Skill 调度器

组合 4 个 Skill 完成完整的意图理解 → 设计简报生成流程。

执行流程：
1. IntentParseSkill  - 解析用户意图
2. DesignRuleSkill   - 基于意图从 KG 推理设计规则
3. BrandContextSkill - 从 RAG 检索品牌知识（如有品牌）
4. DesignBriefSkill  - 综合所有上下文，LLM 生成设计简报

Author: VibePoster Team
Date: 2025-01
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from .base import SkillResult, SkillStatus
from .types import (
    IntentParseInput,
    IntentParseOutput,
    DesignRuleInput,
    DesignRuleOutput,
    BrandContextInput,
    BrandContextOutput,
    DesignBriefInput,
    DesignBriefOutput,
)
from .intent_parse.run import IntentParseSkill
from .design_rule.run import DesignRuleSkill
from .brand_context.run import BrandContextSkill
from .design_brief.run import DesignBriefSkill
from ..core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PlannerContext:
    """
    Planner 上下文 - 收集所有 Skill 的输出
    
    记录完整的规划流程结果，支持决策追溯。
    """
    user_prompt: str
    intent: Optional[IntentParseOutput] = None
    design_rules: Optional[DesignRuleOutput] = None
    brand_context: Optional[BrandContextOutput] = None
    design_brief: Optional[DesignBriefOutput] = None
    
    # 追溯信息
    skill_results: Dict[str, SkillResult] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_prompt": self.user_prompt,
            "intent": self.intent.to_dict() if self.intent else None,
            "design_rules": self.design_rules.to_dict() if self.design_rules else None,
            "brand_context": self.brand_context.to_dict() if self.brand_context else None,
            "design_brief": self.design_brief.to_dict() if self.design_brief else None,
            "skill_trace": {
                name: {
                    "status": result.status.value,
                    "error": result.error
                }
                for name, result in self.skill_results.items()
            }
        }
    
    def to_design_brief_dict(self) -> Dict[str, Any]:
        """
        转换为设计简报字典
        
        供下游 Agent (Visual, Layout, Critic) 使用。
        """
        if self.design_brief:
            return self.design_brief.to_dict()
        return {}


class SkillOrchestrator:
    """
    Skill 调度器
    
    按顺序执行 4 个 Skills，收集结果，构建完整的规划上下文。
    
    Usage:
        orchestrator = SkillOrchestrator()
        context = orchestrator.run("帮我做一个科技风格的海报")
        
        print(context.intent.industry)          # "Tech"
        print(context.design_rules.emotions)    # ["Trust", "Innovation"]
        print(context.design_brief.title)       # "创新科技 引领未来"
    """
    
    def __init__(
        self,
        intent_skill: Optional[IntentParseSkill] = None,
        rule_skill: Optional[DesignRuleSkill] = None,
        brand_skill: Optional[BrandContextSkill] = None,
        brief_skill: Optional[DesignBriefSkill] = None,
    ):
        """
        初始化调度器
        
        所有 Skill 支持延迟初始化和依赖注入。
        
        Args:
            intent_skill: 意图解析 Skill
            rule_skill: 设计规则 Skill
            brand_skill: 品牌上下文 Skill
            brief_skill: 设计简报 Skill
        """
        self._intent_skill = intent_skill
        self._rule_skill = rule_skill
        self._brand_skill = brand_skill
        self._brief_skill = brief_skill
    
    # ========================================================================
    # Skill 延迟初始化
    # ========================================================================
    
    @property
    def intent_skill(self) -> IntentParseSkill:
        """延迟初始化 IntentParseSkill"""
        if self._intent_skill is None:
            self._intent_skill = IntentParseSkill()
        return self._intent_skill
    
    @property
    def rule_skill(self) -> DesignRuleSkill:
        """延迟初始化 DesignRuleSkill"""
        if self._rule_skill is None:
            self._rule_skill = DesignRuleSkill()
        return self._rule_skill
    
    @property
    def brand_skill(self) -> BrandContextSkill:
        """延迟初始化 BrandContextSkill"""
        if self._brand_skill is None:
            self._brand_skill = BrandContextSkill()
        return self._brand_skill
    
    @property
    def brief_skill(self) -> DesignBriefSkill:
        """延迟初始化 DesignBriefSkill"""
        if self._brief_skill is None:
            self._brief_skill = DesignBriefSkill()
        return self._brief_skill
    
    # ========================================================================
    # 核心编排逻辑
    # ========================================================================
    
    def run(
        self,
        user_prompt: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        brand_name: Optional[str] = None,
    ) -> PlannerContext:
        """
        执行完整的规划流程
        
        流程：IntentParse → DesignRule → BrandContext → DesignBrief
        
        Args:
            user_prompt: 用户输入
            chat_history: 对话历史（可选）
            brand_name: 品牌名称（可选，优先级高于自动识别）
            
        Returns:
            包含所有 Skill 结果的上下文
        """
        logger.info(f"🎯 开始 Skill 编排: {user_prompt[:50]}...")
        
        context = PlannerContext(user_prompt=user_prompt)
        
        # Step 1: 意图解析
        intent_result = self.intent_skill(IntentParseInput(
            user_prompt=user_prompt,
            chat_history=chat_history,
        ))
        context.skill_results["intent_parse"] = intent_result
        
        if intent_result.output:
            context.intent = intent_result.output
            # 外部传入的 brand_name 优先级更高
            if brand_name:
                context.intent.brand_name = brand_name
        else:
            logger.warning(f"意图解析失败: {intent_result.error}")
            # 构建最小意图，确保流程可以继续
            context.intent = IntentParseOutput(poster_type="promotion")
        
        # Step 2: 设计规则推理
        rule_result = self.rule_skill(DesignRuleInput(
            industry=context.intent.industry,
            vibe=context.intent.vibe,
        ))
        context.skill_results["design_rule"] = rule_result
        
        if rule_result.output:
            context.design_rules = rule_result.output
        else:
            context.design_rules = DesignRuleOutput()
        
        # Step 3: 品牌上下文（仅当有品牌名时）
        effective_brand = context.intent.brand_name
        if effective_brand:
            brand_result = self.brand_skill(BrandContextInput(
                brand_name=effective_brand,
            ))
            context.skill_results["brand_context"] = brand_result
            
            if brand_result.output:
                context.brand_context = brand_result.output
        
        # Step 4: 设计简报生成
        brief_result = self.brief_skill(DesignBriefInput(
            user_prompt=user_prompt,
            intent=context.intent,
            design_rules=context.design_rules,
            brand_context=context.brand_context,
        ))
        context.skill_results["design_brief"] = brief_result
        
        if brief_result.output:
            context.design_brief = brief_result.output
        
        # 汇总日志
        skill_statuses = {
            name: result.status.value 
            for name, result in context.skill_results.items()
        }
        logger.info(f"✅ Skill 编排完成: {skill_statuses}")
        
        return context
