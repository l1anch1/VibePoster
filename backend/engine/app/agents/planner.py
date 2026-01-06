"""
Planner Agent - 规划与意图理解
纯粹的"大脑" (只写 Prompt 和调用 LLM)
"""

import json
from typing import Dict, Any, Optional, List
from ..core.config import settings
from ..core.llm import LLMClientFactory
from ..core.logger import get_logger
from ..prompts import get_planner_prompt
from ..templates.manager import template_manager
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
    style_template_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    运行 Planner Agent（独立函数版本）

    Args:
        user_prompt: 用户输入的提示词
        chat_history: 对话历史（可选）
        style_template_id: 风格模板 ID（可选）

    Returns:
        设计简报字典
    """
    logger.info(f"🕵️ Planner Agent 正在思考: {user_prompt}...")

    try:
        # 1. 选择风格模板（手动指定或智能匹配）
        if style_template_id:
            # 用户手动指定风格
            template = template_manager.get_template(style_template_id)
            if not template:
                logger.warning(f"指定的风格模板 '{style_template_id}' 不存在，使用默认模板")
                template = template_manager.get_default_template()
            else:
                logger.info(f"📋 使用指定的风格模板: {template.display_name}")
        else:
            # 智能匹配风格模板
            template = template_manager.smart_match_template(user_prompt)
            logger.info(f"🎯 智能匹配到风格模板: {template.display_name}")

        # 2. 将风格模板上下文注入到 Prompt 中
        template_context = template.to_prompt_context()
        
        # 使用配置化的 prompt（支持对话历史和风格模板）
        prompts = get_planner_prompt(user_prompt, chat_history, template_context)

        # 使用工厂类获取 Agent
        from .base import AgentFactory

        agent = AgentFactory.get_planner_agent()

        # 调用 Agent（使用统一的 invoke 接口）
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

        # 3. 将风格模板信息添加到设计简报中
        brief["style_template"] = {
            "id": template.id,
            "name": template.display_name,
            "color_scheme": template.get_default_color_scheme().dict(),
        }

        logger.info(f"✅ Planner 思考完毕: {brief.get('title', 'Untitled')} ({template.display_name})")
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
    logger.info("🕵️ Planner (DeepSeek) 正在规划海报内容...")

    user_prompt = state.get("user_prompt", "")
    chat_history = state.get("chat_history")
    style_template_id = state.get("style_template")  # 获取风格模板 ID

    # 关键：先获取已存在的 brief（包含画布尺寸）
    existing_brief = state.get("design_brief", {})

    # 运行 Planner Agent（传递风格模板 ID）
    brief_from_llm = run_planner_agent(user_prompt, chat_history, style_template_id)

    # 合并，这样 LLM 的输出会覆盖默认值，但我们保留了画布尺寸等额外信息
    final_brief = {**existing_brief, **brief_from_llm}

    logger.info(f"✅ Planner 最终合并后的设计简报: {final_brief}")

    return {"design_brief": final_brief}
