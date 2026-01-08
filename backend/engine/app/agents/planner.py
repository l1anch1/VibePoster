"""
Planner Agent - 规划与意图理解

职责：
1. 解析用户意图
2. 生成设计简报

知识模块通过 KnowledgeService 注入，实现解耦。

Author: VibePoster Team
Date: 2025-01
"""

import json
from typing import Dict, Any, Optional, List

from ..core.config import settings
from ..core.llm import LLMClientFactory
from ..core.logger import get_logger
from ..core.dependencies import get_knowledge_service
from ..prompts import get_planner_prompt
from .base import BaseAgent

logger = get_logger(__name__)


class PlannerAgent(BaseAgent):
    """Planner Agent 实现类"""

    def _create_client(self):
        return LLMClientFactory.get_client(
            provider=self.config.get("provider", "deepseek"),
            api_key=self.config.get("api_key"),
            base_url=self.config.get("base_url"),
        )

    def invoke(self, messages: list, **kwargs) -> Dict[str, Any]:
        """调用 Planner Agent"""
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
    knowledge_service=None
) -> Dict[str, Any]:
    """
    运行 Planner Agent

    Args:
        user_prompt: 用户输入的提示词
        chat_history: 对话历史（可选）
        brand_name: 企业品牌名称（可选，用于 RAG 检索）
        knowledge_service: 知识服务实例（可选，用于依赖注入）

    Returns:
        设计简报字典
    """
    logger.info(f"🕵️ Planner Agent 正在思考: {user_prompt}...")

    try:
        # 获取知识服务（支持依赖注入）
        ks = knowledge_service or get_knowledge_service()
        
        # 使用 KnowledgeService 获取设计上下文
        design_context = ks.get_design_context(user_prompt, brand_name)
        
        kg_keywords = design_context["kg_keywords"]
        kg_rules = design_context["kg_rules"]
        brand_knowledge = design_context["brand_knowledge"]
        
        if kg_keywords:
            logger.info(f"🔮 KG 检测到关键词: {kg_keywords}")
        
        # 构建 Prompt 上下文
        template_context = ks.build_prompt_context(kg_rules, brand_knowledge)
        
        # 获取 Prompt
        prompts = get_planner_prompt(user_prompt, chat_history, template_context)

        # 调用 Agent
        from .base import AgentFactory
        agent = AgentFactory.get_planner_agent()

        response = agent.invoke(
            messages=[
                {"role": "system", "content": prompts["system"]},
                {"role": "user", "content": prompts["user"]},
            ]
        )

        content = response.choices[0].message.content
        brief = json.loads(content)

        # 确保包含 intent 字段
        if "intent" not in brief:
            brief["intent"] = settings.planner.DEFAULT_INTENT

        # 添加知识模块结果
        if kg_rules:
            brief["kg_rules"] = kg_rules
            if not brief.get("main_color") and kg_rules.get("recommended_colors"):
                brief["main_color"] = kg_rules["recommended_colors"][0]
                logger.info(f"🔮 使用 KG 推荐的主色调: {brief['main_color']}")
        
        if brand_knowledge:
            brief["brand_knowledge"] = [
                {"text": doc["text"], "category": doc.get("metadata", {}).get("category", "")}
                for doc in brand_knowledge
            ]
        
        # 添加来源标记
        brief["design_source"] = {
            "kg_keywords": kg_keywords,
            "kg_active": bool(kg_rules),
            "rag_active": bool(brand_knowledge),
            "brand_name": brand_name
        }

        logger.info(f"✅ Planner 思考完毕: {brief.get('title', 'Untitled')}")
        return brief

    except Exception as e:
        logger.error(f"❌ Planner 出错: {e}")
        return settings.ERROR_FALLBACKS["planner"]


def planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Planner Agent 工作流节点

    Args:
        state: 工作流状态

    Returns:
        更新后的状态
    """
    logger.info("🕵️ Planner (KG + RAG) 正在规划海报内容...")

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
