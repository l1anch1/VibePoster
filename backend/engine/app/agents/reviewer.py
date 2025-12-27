"""
Reviewer Agent - 质量审核
基于规则和视觉冲突检测，进行自修正
"""
import json
from typing import Dict, Any
from ..core.config import ERROR_FALLBACKS, DEEPSEEK_CONFIG
from ..core.llm import LLMClientFactory
from ..prompts import get_reviewer_prompt
from .base import BaseAgent


class ReviewerAgent(BaseAgent):
    """Reviewer Agent 实现类"""
    
    def _create_client(self):
        return LLMClientFactory.get_deepseek_client()
    
    def invoke(self, messages: list, **kwargs) -> Dict[str, Any]:
        """调用 Reviewer Agent"""
        response = self.client.chat.completions.create(
            model=DEEPSEEK_CONFIG["model"],
            messages=messages,
            temperature=DEEPSEEK_CONFIG.get("temperature", 0.3),  # 审核需要更低的温度
            response_format=DEEPSEEK_CONFIG.get("response_format"),
            **kwargs,
        )
        return response


def run_reviewer_agent(poster_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    运行 Reviewer Agent
    
    检查项：
    1. 文字是否遮挡了前景图层（特别是人物）的面部区域？
    2. 文字是否超出画布范围？
    3. 文字对比度是否合格？
    4. 图层顺序是否正确？
    5. 所有图层是否都有有效的 width 和 height？
    
    Args:
        poster_data: 海报数据
        
    Returns:
        审核反馈字典
    """
    print("⚖️ Reviewer Agent 正在审核海报质量...")

    try:
        # 使用配置化的 prompt
        prompt_content = get_reviewer_prompt(poster_data)
        
        # 使用工厂类获取 Agent
        from .base import AgentFactory
        agent = AgentFactory.get_reviewer_agent()
        
        # 调用 Agent（使用统一的 invoke 接口）
        response = agent.invoke(
            messages=[
                {"role": "system", "content": "你是一个严格的海报质量审核员。请仔细检查海报数据，输出 JSON 格式的审核结果。"},
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
            feedback["status"] = "PASS"
        if "feedback" not in feedback:
            feedback["feedback"] = "审核通过"
        if "issues" not in feedback:
            feedback["issues"] = []
        
        status_emoji = "✅" if feedback["status"] == "PASS" else "❌"
        print(f"{status_emoji} Reviewer 审核结果: {feedback['status']} - {feedback['feedback']}")
        
        # 打印详细的问题列表，方便调试
        if feedback.get("issues"):
            print(f"📋 问题列表: {', '.join(feedback['issues'])}")
        
        return feedback

    except Exception as e:
        print(f"❌ Reviewer Agent 出错: {e}")
        return ERROR_FALLBACKS["reviewer"]


def reviewer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reviewer Agent 工作流节点
    
    Args:
        state: 工作流状态
        
    Returns:
        更新后的状态
    """
    final_poster = state.get("final_poster", {})
    
    # 先读取当前重试计数（在审核之前）
    current_retry_count = state.get("_retry_count", 0)
    
    review_feedback = run_reviewer_agent(final_poster)
    
    # 如果审核不通过，增加重试计数
    new_retry_count = current_retry_count
    if review_feedback.get("status") == "REJECT":
        new_retry_count = current_retry_count + 1
        print(f"📊 当前重试计数: {new_retry_count}/2 (之前: {current_retry_count})")
    
    return {
        "review_feedback": review_feedback,
        "_retry_count": new_retry_count
    }


def should_retry_layout(state: Dict[str, Any]) -> str:
    """
    判断是否应该重新进行 Layout（条件边函数）
    
    注意：在 LangGraph 中，条件边函数只能读取状态，不能修改状态。
    状态更新应该在节点中完成（已在 reviewer_node 中处理）。
    
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
        # 注意：这里的 retry_count 是审核后的新计数（已经在 reviewer_node 中增加了）
        # retry_count = 1 表示第1次重试，retry_count = 2 表示第2次重试，retry_count = 3 表示超过限制
        if retry_count <= 2:  # 最多重试2次（retry_count <= 2 表示还可以重试）
            print(f"🔄 审核不通过，准备重试 Layout (第 {retry_count} 次重试，最多2次)...")
            return "retry"
        else:
            print(f"⚠️ 已达到最大重试次数 ({retry_count}/2)，结束工作流")
            return "end"
    
    # 审核通过，结束工作流
    print("✅ 审核通过，结束工作流")
    return "end"
