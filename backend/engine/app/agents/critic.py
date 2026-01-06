"""
Critic Agent - 反思与质量审核
基于规则和视觉冲突检测，进行自修正
"""

import json
from typing import Dict, Any
from ..core.config import settings
from ..core.llm import LLMClientFactory
from ..core.logger import get_logger
from ..prompts import get_critic_prompt
from .base import BaseAgent

logger = get_logger(__name__)


class CriticAgent(BaseAgent):
    """Critic Agent 实现类"""

    def _create_client(self):
        return LLMClientFactory.get_client(
            provider=self.config.get("provider", "deepseek"),
            api_key=self.config.get("api_key"),
            base_url=self.config.get("base_url"),
        )

    def invoke(self, messages: list, **kwargs) -> Dict[str, Any]:
        """调用 Critic Agent"""
        response = self.client.chat.completions.create(
            model=self.config["model"],
            messages=messages,
            temperature=self.config["temperature"],
            response_format=self.config.get("response_format"),
            **kwargs,
        )
        return response


def run_critic_agent(poster_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    运行 Critic Agent

    Args:
        poster_data: 海报数据

    Returns:
        审核反馈字典
    """
    logger.info("⚖️ Critic Agent 正在审核海报质量...")

    try:
        # 使用配置化的 prompt
        prompt_content = get_critic_prompt(poster_data)

        # 使用工厂类获取 Agent
        from .base import AgentFactory

        agent = AgentFactory.get_critic_agent()

        # 调用 Agent（使用统一的 invoke 接口）
        response = agent.invoke(
            messages=[
                {"role": "system", "content": agent.config["system_prompt"]},
                {"role": "user", "content": prompt_content},
            ]
        )

        content = response.choices[0].message.content

        # 清理可能存在的 markdown 标记
        if "```json" in content:
            content = content.replace("```json", "").replace("```", "")

        feedback = json.loads(content)

        # 确保包含必要字段
        if "status" not in feedback:
            feedback["status"] = settings.critic.DEFAULT_STATUS
        if "feedback" not in feedback:
            feedback["feedback"] = agent.config["default_feedback"]
        if "issues" not in feedback:
            feedback["issues"] = []

        status_emoji = "✅" if feedback["status"] == "PASS" else "❌"
        logger.info(f"{status_emoji} Critic 审核结果: {feedback['status']} - {feedback['feedback']}")

        # 记录详细的问题列表，方便调试
        if feedback.get("issues"):
            logger.info(f"📋 问题列表: {', '.join(feedback['issues'])}")

        return feedback

    except Exception as e:
        logger.error(f"❌ Critic Agent 出错: {e}")
        return settings.ERROR_FALLBACKS["critic"]


def critic_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Critic Agent 工作流节点

    Args:
        state: 工作流状态

    Returns:
        更新后的状态
    """
    final_poster = state.get("final_poster", {})

    # 先读取当前重试计数（在审核之前）
    current_retry_count = state.get("_retry_count", 0)

    review_feedback = run_critic_agent(final_poster)

    # 如果审核不通过，增加重试计数
    new_retry_count = current_retry_count
    if review_feedback.get("status") == "REJECT":
        new_retry_count = current_retry_count + 1
        max_retry = settings.critic.MAX_RETRY_COUNT
        logger.info(f"📊 当前重试计数: {new_retry_count}/{max_retry} (之前: {current_retry_count})")

    return {"review_feedback": review_feedback, "_retry_count": new_retry_count}


def should_retry_layout(state: Dict[str, Any]) -> str:
    """
    判断是否应该重新进行 Layout（条件边函数）

    注意：在 LangGraph 中，条件边函数只能读取状态，不能修改状态。
    状态更新应该在节点中完成（已在 critic_node 中处理）。

    Args:
        state: 工作流状态

    Returns:
        "retry" 或 "end"
    """
    review_feedback = state.get("review_feedback", {})
    status = review_feedback.get("status", "PASS")
    retry_count = state.get("_retry_count", 0)

    # 如果审核不通过，且重试次数未超过限制，则重试
    if status == "REJECT":
        max_retry = settings.critic.MAX_RETRY_COUNT
        if retry_count <= max_retry:  # 最多重试 max_retry 次
            logger.info(f"🔄 审核不通过，准备重试 Layout (第 {retry_count} 次重试，最多{max_retry}次)...")
            return "retry"
        else:
            logger.warning(f"⚠️ 已达到最大重试次数 ({retry_count}/{max_retry})，结束工作流")
            return "end"

    # 审核通过，结束工作流
    logger.info("✅ 审核通过，结束工作流")
    return "end"
