"""
Knowledge Graph 模块 v2

支持语义化推理链：Industry/Vibe → Emotion → Visual Elements

模块结构:
    - types.py: Pydantic 类型定义
    - loader.py: 规则数据加载
    - graph.py: 图结构管理
    - inference.py: 推理引擎
    - knowledge_graph.py: 组合入口
"""

from .knowledge_graph import DesignKnowledgeGraph
from .types import (
    # 枚举
    NodeType,
    EdgeType,
    # 设计元素模型
    ColorPalette,
    Typography,
    LayoutStyle,
    EmotionDefinition,
    IndustryDefinition,
    VibeDefinition,
    # 结果模型
    InferenceResult,
    GraphStats,
)
from .loader import RulesLoader
from .graph import DesignGraph
from .inference import InferenceEngine

__all__ = [
    # 主入口
    "DesignKnowledgeGraph",
    
    # 枚举
    "NodeType",
    "EdgeType",
    
    # 设计元素模型
    "ColorPalette",
    "Typography",
    "LayoutStyle",
    "EmotionDefinition",
    "IndustryDefinition",
    "VibeDefinition",
    
    # 结果模型
    "InferenceResult",
    "GraphStats",
    
    # 组件
    "RulesLoader",
    "DesignGraph",
    "InferenceEngine",
]
