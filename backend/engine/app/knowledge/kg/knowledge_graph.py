"""
Design Knowledge Graph v3 — 组合入口

五层设计知识本体：
    Industry / Vibe → Emotion → ColorStrategy / TypographyStyle / LayoutPattern / DecorationTheme

使用示例::

    kg = DesignKnowledgeGraph()
    result = kg.infer_rules(["Tech", "Minimalist"])

    print(result["emotions"])
    print(result["color_strategies"])
    print(result["color_palettes"])
    print(result["layout_patterns"])
    print(result["decoration_styles"])
"""

from typing import List, Dict, Any, Optional, Set

from .types import InferenceResult, InferenceTrace, GraphStats
from .loader import OntologyLoader
from .graph import DesignGraph
from .inference import InferenceEngine
from ...core.interfaces import IKnowledgeGraph
from ...core.logger import get_logger

logger = get_logger(__name__)


class DesignKnowledgeGraph(IKnowledgeGraph):
    """设计知识图谱 v3 — 五层本体 + 多跳推理"""

    def __init__(self, rules_file: Optional[str] = None):
        logger.info("初始化设计知识本体 v3 ...")
        self._loader = OntologyLoader(rules_file)
        self._graph = DesignGraph(self._loader)
        self._engine = InferenceEngine(self._graph)

        stats = self._graph.get_stats()
        logger.info(
            f"本体 v{stats.version} 就绪: "
            f"{stats.node_count} 节点 / {stats.edge_count} 边 | "
            f"Emotions={len(stats.emotions)}, "
            f"Industries={len(stats.industries)}, "
            f"Vibes={len(stats.vibes)}"
        )

    # ==================================================================
    # IKnowledgeGraph 接口
    # ==================================================================

    def infer_rules(
        self, keywords: List[str], extra_avoids: Optional[Set[str]] = None,
    ) -> Dict[str, Any]:
        result = self._engine.infer(keywords, extra_avoids=extra_avoids)
        d = result.to_dict()
        d["inference_traces"] = [t.model_dump() for t in result.inference_traces]
        return d

    def get_graph_stats(self) -> Dict[str, Any]:
        return self._graph.get_stats().to_dict()

    # ==================================================================
    # 扩展接口
    # ==================================================================

    def infer_with_traces(self, keywords: List[str]) -> InferenceResult:
        """推理并返回完整的推理链追踪（不丢弃 traces）"""
        return self._engine.infer(keywords)

    def get_emotions_for_keyword(self, keyword: str) -> List[str]:
        hits = self._graph.get_embodied_emotions(keyword)
        return [h["target"] for h in hits]

    def get_emotion_visual_rules(self, emotion: str) -> Optional[Dict[str, Any]]:
        return self._graph.get_node_data(emotion)

    def visualize_inference_chain(self, keyword: str) -> Dict[str, Any]:
        return self._graph.visualize_inference_chain(keyword)

    def get_supported_keywords(self) -> Dict[str, List[str]]:
        return self._loader.get_supported_keywords()

    def rebuild(self) -> None:
        logger.info("重建知识本体 ...")
        self._graph.rebuild()
        stats = self._graph.get_stats()
        logger.info(f"重建完成: {stats.node_count} 节点 / {stats.edge_count} 边")

    # ==================================================================
    # 属性
    # ==================================================================

    @property
    def loader(self) -> OntologyLoader:
        return self._loader

    @property
    def graph(self) -> DesignGraph:
        return self._graph

    @property
    def engine(self) -> InferenceEngine:
        return self._engine

    @property
    def version(self) -> str:
        return self._loader.get_version()
