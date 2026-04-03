"""
Knowledge Graph 模块 v3

五层设计知识本体：
    Industry/Vibe → Emotion → ColorStrategy / TypographyStyle / LayoutPattern / DecorationTheme

模块结构:
    - types.py:           Pydantic 类型定义（节点、边、推理结果）
    - loader.py:          本体数据加载（ontology.json）
    - graph.py:           有向属性图构建与遍历
    - inference.py:       多跳推理引擎（冲突消解 + 链路追踪）
    - knowledge_graph.py: 组合入口（IKnowledgeGraph 实现）
"""

from .knowledge_graph import DesignKnowledgeGraph
from .types import (
    NodeType,
    EdgeType,
    EmotionDefinition,
    IndustryDefinition,
    VibeDefinition,
    ColorStrategyDefinition,
    TypographyStyleDefinition,
    LayoutPatternDefinition,
    DecorationThemeDefinition,
    Relation,
    InferenceResult,
    InferenceTrace,
    GraphStats,
)
from .loader import OntologyLoader, RulesLoader
from .graph import DesignGraph
from .inference import InferenceEngine

__all__ = [
    "DesignKnowledgeGraph",
    "NodeType",
    "EdgeType",
    "EmotionDefinition",
    "IndustryDefinition",
    "VibeDefinition",
    "ColorStrategyDefinition",
    "TypographyStyleDefinition",
    "LayoutPatternDefinition",
    "DecorationThemeDefinition",
    "Relation",
    "InferenceResult",
    "InferenceTrace",
    "GraphStats",
    "OntologyLoader",
    "RulesLoader",
    "DesignGraph",
    "InferenceEngine",
]
