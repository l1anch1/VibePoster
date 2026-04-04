"""
Planner Agent - 规划与意图理解

通过 SkillOrchestrator 调度 4 个 Skill 完成规划流程：
  IntentParseSkill  → 意图解析
  DesignRuleSkill   → KG 设计规则推理
  BrandContextSkill → RAG 品牌知识检索
  DesignBriefSkill  → LLM 设计简报生成

Author: VibePoster Team
Date: 2025-01
"""

from typing import Dict, Any, Optional, List

from ..core.config import ERROR_FALLBACKS
from ..core.llm import LLMClientFactory
from ..core.logger import get_logger
from .base import BaseAgent

logger = get_logger(__name__)


class PlannerAgent(BaseAgent):
    """Planner Agent 实现类（LLM 调用层，供 DesignBriefSkill 使用）"""

    def _create_client(self):
        return LLMClientFactory.get_client(
            provider=self.config.get("provider", "deepseek"),
            api_key=self.config.get("api_key"),
            base_url=self.config.get("base_url"),
        )

    def invoke(self, messages: list, **kwargs) -> Dict[str, Any]:
        """调用 LLM"""
        response = self.client.chat.completions.create(
            model=self.config["model"],
            messages=messages,
            temperature=self.config["temperature"],
            response_format=self.config.get("response_format"),
            **kwargs,
        )
        return response


def run_planner_agent(
    user_prompt: str,
    chat_history: Optional[List[Dict[str, str]]] = None,
    brand_name: Optional[str] = None,
    image_analyses: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    运行 Planner Agent（通过 SkillOrchestrator 调度）

    执行流程：
    1. IntentParseSkill  - 解析用户意图
    2. DesignRuleSkill   - KG 推理设计规则
    3. BrandContextSkill - RAG 检索品牌知识
    4. DesignBriefSkill  - LLM 生成设计简报

    Args:
        user_prompt: 用户输入的提示词
        chat_history: 对话历史（可选）
        brand_name: 企业品牌名称（可选，用于 RAG 检索）

    Returns:
        设计简报字典
    """
    logger.info(f"🕵️ Planner Agent（Skills 模式）正在思考: {user_prompt}...")

    try:
        orchestrator = _get_orchestrator()
        context = orchestrator.run(
            user_prompt=user_prompt,
            chat_history=chat_history,
            brand_name=brand_name,
            image_analyses=image_analyses,
        )

        if context.design_brief:
            brief = context.design_brief.to_dict()
            logger.info(f"✅ Planner 思考完毕: {brief.get('title', 'Untitled')}")
            return brief

        logger.warning("DesignBriefSkill 未返回结果，使用 fallback")
        return ERROR_FALLBACKS["planner"]

    except Exception as e:
        logger.error(f"❌ Planner 出错: {e}")
        return ERROR_FALLBACKS["planner"]


def planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Planner Agent 工作流节点

    Args:
        state: 工作流状态

    Returns:
        更新后的状态
    """
    logger.info("🕵️ Planner (Skills: Intent→KG→RAG→Brief) 正在规划海报内容...")

    user_prompt = state.get("user_prompt", "")
    chat_history = state.get("chat_history")
    brand_name = state.get("brand_name")
    existing_brief = state.get("design_brief", {})

    brief_from_llm = run_planner_agent(
        user_prompt,
        chat_history,
        brand_name=brand_name
    )

    final_brief = {**existing_brief, **brief_from_llm}

    logger.info(f"✅ Planner 最终设计简报: {final_brief.get('title', 'Untitled')}")

    return {"design_brief": final_brief}


# ============================================================================
# 模块级单例
# ============================================================================

_orchestrator = None


def _get_orchestrator():
    """获取 SkillOrchestrator 单例"""
    global _orchestrator
    if _orchestrator is None:
        from ..skills import SkillOrchestrator
        from ..core.dependencies import (
            get_intent_parse_skill,
            get_design_rule_skill,
            get_brand_context_skill,
            get_design_brief_skill,
        )
        _orchestrator = SkillOrchestrator(
            intent_skill=get_intent_parse_skill(),
            rule_skill=get_design_rule_skill(),
            brand_skill=get_brand_context_skill(),
            brief_skill=get_design_brief_skill(),
        )
    return _orchestrator
