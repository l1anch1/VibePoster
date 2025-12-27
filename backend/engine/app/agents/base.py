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
    def get_director_agent(cls):
        """获取 Director Agent"""
        from .director import DirectorAgent
        from ..core.config import DIRECTOR_CONFIG
        return cls._get_or_create_agent("director", DirectorAgent, DIRECTOR_CONFIG)
    
    @classmethod
    def get_prompter_agent(cls):
        """获取 Prompter Agent"""
        from .prompter import PrompterAgent
        from ..core.config import PROMPTER_CONFIG
        return cls._get_or_create_agent("prompter", PrompterAgent, PROMPTER_CONFIG)
    
    @classmethod
    def get_layout_agent(cls):
        """获取 Layout Agent"""
        from .layout import LayoutAgent
        from ..core.config import LAYOUT_CONFIG
        return cls._get_or_create_agent("layout", LayoutAgent, LAYOUT_CONFIG)
    
    @classmethod
    def get_reviewer_agent(cls):
        """获取 Reviewer Agent"""
        from .reviewer import ReviewerAgent
        from ..core.config import REVIEWER_CONFIG
        return cls._get_or_create_agent("reviewer", ReviewerAgent, REVIEWER_CONFIG)
