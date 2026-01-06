"""
Agent 基类 - 定义 invoke 接口规范
只包含基类和工厂类，不包含具体实现
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Type


class BaseAgent(ABC):
    """Agent 基类 - 定义统一的接口规范"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = self._create_client()

    @abstractmethod
    def _create_client(self):
        """创建客户端"""
        pass

    @abstractmethod
    def invoke(self, *args, **kwargs) -> Dict[str, Any]:
        """调用 Agent（统一接口）"""
        pass


class AgentFactory:
    """Agent 工厂类 - 负责创建和管理 Agent 实例"""

    _agents: Dict[str, BaseAgent] = {}

    @classmethod
    def _get_or_create_agent(cls, cache_key: str, agent_class: Type[BaseAgent], config: Dict[str, Any]) -> BaseAgent:
        """
        获取或创建 Agent 实例（内部方法）

        Args:
            cache_key: 缓存键
            agent_class: Agent 类
            config: Agent 配置

        Returns:
            Agent 实例
        """
        if cache_key not in cls._agents:
            cls._agents[cache_key] = agent_class(config)
        return cls._agents[cache_key]

    @classmethod
    def get_planner_agent(cls):
        """获取 Planner Agent"""
        from .planner import PlannerAgent
        from ..core.config import settings

        # 将 Pydantic Settings 对象转换为字典格式
        config_dict = {
            "provider": settings.planner.PROVIDER,
            "model": settings.planner.MODEL,
            "temperature": settings.planner.TEMPERATURE,
            "api_key": settings.planner.API_KEY,
            "base_url": settings.planner.BASE_URL,
            "response_format": {"type": "json_object"},
            "default_intent": settings.planner.DEFAULT_INTENT,
        }
        return cls._get_or_create_agent("planner", PlannerAgent, config_dict)

    @classmethod
    def get_visual_agent(cls):
        """获取 Visual Agent"""
        from .visual import VisualAgent
        from ..core.config import settings

        config_dict = {
            "provider": settings.visual.PROVIDER,
            "model": settings.visual.MODEL,
            "temperature": settings.visual.TEMPERATURE,
            "api_key": settings.visual.API_KEY,
            "base_url": settings.visual.BASE_URL,
            "response_format": {"type": "json_object"},
            "default_position": settings.visual.DEFAULT_POSITION,
        }
        return cls._get_or_create_agent("visual", VisualAgent, config_dict)

    @classmethod
    def get_layout_agent(cls):
        """获取 Layout Agent"""
        from .layout import LayoutAgent
        from ..core.config import settings

        config_dict = {
            "provider": settings.layout.PROVIDER,
            "model": settings.layout.MODEL,
            "api_key": settings.layout.API_KEY,
            "base_url": settings.layout.BASE_URL,
            "response_mime_type": "application/json",
            "foreground_max_width_ratio": settings.layout.FG_MAX_WIDTH_RATIO,
            "foreground_max_height_ratio": settings.layout.FG_MAX_HEIGHT_RATIO,
            "z_index": {
                "background": settings.layout.Z_INDEX_BG,
                "foreground": settings.layout.Z_INDEX_FG,
                "text": settings.layout.Z_INDEX_TEXT,
            },
        }
        return cls._get_or_create_agent("layout", LayoutAgent, config_dict)

    @classmethod
    def get_critic_agent(cls):
        """获取 Critic Agent"""
        from .critic import CriticAgent
        from ..core.config import settings

        config_dict = {
            "provider": settings.critic.PROVIDER,
            "model": settings.critic.MODEL,
            "temperature": settings.critic.TEMPERATURE,
            "api_key": settings.critic.API_KEY,
            "base_url": settings.critic.BASE_URL,
            "response_format": {"type": "json_object"},
            "system_prompt": "你是一个严格的海报质量审核员。请仔细检查海报数据，输出 JSON 格式的审核结果。",
            "default_status": settings.critic.DEFAULT_STATUS,
            "default_feedback": "审核通过",
            "max_retry_count": settings.critic.MAX_RETRY_COUNT,
        }
        return cls._get_or_create_agent("critic", CriticAgent, config_dict)
