"""
Director Agent - 策划与意图理解
纯粹的"大脑" (只写 Prompt 和调用 LLM)
"""
import json
from typing import Dict, Any, Optional, List
from ..core.config import ERROR_FALLBACKS, DEEPSEEK_CONFIG
from ..core.llm import LLMClientFactory
from ..prompts import get_director_prompt
from .base import BaseAgent


class DirectorAgent(BaseAgent):
    """Director Agent 实现类"""
    
    def _create_client(self):
        return LLMClientFactory.get_deepseek_client()
    
    def invoke(self, messages: list, **kwargs) -> Dict[str, Any]:
        """调用 Director Agent"""
        response = self.client.chat.completions.create(
            model=DEEPSEEK_CONFIG["model"],
            messages=messages,
            temperature=DEEPSEEK_CONFIG.get("temperature", 0.7),
            response_format=DEEPSEEK_CONFIG.get("response_format"),
            **kwargs,
        )
        return response


def run_director_agent(
    user_prompt: str,
    chat_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    运行 Director Agent（独立函数版本）
    
    Args:
        user_prompt: 用户输入的提示词
        chat_history: 对话历史（可选）
        
    Returns:
        设计简报字典
    """
    print(f"🕵️ Director Agent 正在思考: {user_prompt}...")

    try:
        # 使用配置化的 prompt（支持对话历史）
        prompts = get_director_prompt(user_prompt, chat_history)
        
        # 使用工厂类获取 Agent
        from .base import AgentFactory
        agent = AgentFactory.get_director_agent()
        
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
            brief["intent"] = "other"
        
        print(f"✅ Director 思考完毕: {brief}")
        return brief

    except Exception as e:
        print(f"❌ Director 出错: {e}")
        return ERROR_FALLBACKS["director"]


def director_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Director Agent 工作流节点
    
    Args:
        state: 工作流状态
        
    Returns:
        更新后的状态
    """
    print("🕵️ Director (DeepSeek) 正在策划海报内容...")
    
    user_prompt = state.get("user_prompt", "")
    chat_history = state.get("chat_history")
    
    brief = run_director_agent(user_prompt, chat_history)
    
    return {"design_brief": brief}
