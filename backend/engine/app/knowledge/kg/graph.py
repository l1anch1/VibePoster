"""
五层设计知识本体图 v3

构建完整的有向属性图：
    Layer 0  Industry / Vibe
    Layer 1  Emotion
    Layer 2  ColorStrategy / TypographyStyle / LayoutPattern / DecorationTheme

边类型：EMBODIES · EVOKES · AVOIDS · CONFLICTS_WITH
"""

from typing import Dict, Any, List, Optional, Set
from collections import defaultdict

import networkx as nx

from .types import (
    EdgeType,
    GraphStats,
    NodeType,
    Relation,
)
from .loader import OntologyLoader
from ...core.logger import get_logger

logger = get_logger(__name__)

# 节点分类名 → NodeType 映射（与 ontology.json 的 nodes 键对齐）
_SECTION_NODE_TYPE: Dict[str, NodeType] = {
    "emotions": NodeType.EMOTION,
    "industries": NodeType.INDUSTRY,
    "vibes": NodeType.VIBE,
    "color_strategies": NodeType.COLOR_STRATEGY,
    "typography_styles": NodeType.TYPOGRAPHY_STYLE,
    "layout_patterns": NodeType.LAYOUT_PATTERN,
    "decoration_themes": NodeType.DECORATION_THEME,
}


class DesignGraph:
    """五层设计知识本体图"""

    def __init__(self, loader: Optional[OntologyLoader] = None):
        self.graph = nx.DiGraph()
        self.loader = loader or OntologyLoader()
        self._build()

    # ------------------------------------------------------------------
    # 图构建
    # ------------------------------------------------------------------

    def _build(self) -> None:
        """从 ontology.json 构建完整的有向属性图"""
        raw = self.loader.load()
        nodes_section = raw.get("nodes", {})

        for section_key, node_type in _SECTION_NODE_TYPE.items():
            items = nodes_section.get(section_key, {})
            for name, props in items.items():
                self.graph.add_node(
                    name,
                    node_type=node_type.value,
                    data=props,
                )

        relations = self.loader.get_relations()
        for rel in relations:
            if not (self.graph.has_node(rel.source) and self.graph.has_node(rel.target)):
                logger.warning(
                    f"关系引用了不存在的节点: {rel.source} → {rel.target} ({rel.type})"
                )
                continue
            self.graph.add_edge(
                rel.source,
                rel.target,
                relation=rel.type.lower(),
                weight=rel.weight,
                context=rel.context,
            )

        type_counts = defaultdict(int)
        for _, d in self.graph.nodes(data=True):
            type_counts[d.get("node_type", "?")] += 1
        edge_counts = defaultdict(int)
        for _, _, d in self.graph.edges(data=True):
            edge_counts[d.get("relation", "?")] += 1

        logger.info(
            f"本体图 v3 构建完成: {self.node_count} 节点 / {self.edge_count} 边 | "
            f"节点: {dict(type_counts)} | 边: {dict(edge_counts)}"
        )

    # ------------------------------------------------------------------
    # 基础查询
    # ------------------------------------------------------------------

    @property
    def node_count(self) -> int:
        return self.graph.number_of_nodes()

    @property
    def edge_count(self) -> int:
        return self.graph.number_of_edges()

    def has_node(self, name: str) -> bool:
        return name in self.graph

    def get_node_type(self, name: str) -> Optional[str]:
        if not self.has_node(name):
            return None
        return self.graph.nodes[name].get("node_type")

    def get_node_data(self, name: str) -> Optional[Dict[str, Any]]:
        if not self.has_node(name):
            return None
        return self.graph.nodes[name].get("data")

    # ------------------------------------------------------------------
    # 语义遍历
    # ------------------------------------------------------------------

    def get_neighbors(
        self, source: str, relation: str
    ) -> List[Dict[str, Any]]:
        """获取指定关系类型的所有邻居（含边属性）"""
        if not self.has_node(source):
            return []
        result: List[Dict[str, Any]] = []
        for _, target, edge_data in self.graph.out_edges(source, data=True):
            if edge_data.get("relation") == relation:
                result.append({
                    "target": target,
                    "weight": edge_data.get("weight", 1.0),
                    "context": edge_data.get("context", {}),
                })
        return result

    def get_embodied_emotions(self, keyword: str) -> List[Dict[str, Any]]:
        """获取入口节点体现的情绪（含权重），Emotion 节点返回自身"""
        node_type = self.get_node_type(keyword)
        if node_type == NodeType.EMOTION.value:
            return [{"target": keyword, "weight": 1.0, "context": {}}]
        return self.get_neighbors(keyword, EdgeType.EMBODIES.value)

    def get_evoked_strategies(
        self, emotion: str, target_type: Optional[NodeType] = None
    ) -> List[Dict[str, Any]]:
        """获取情绪唤起的视觉策略（可按节点类型过滤）"""
        neighbors = self.get_neighbors(emotion, EdgeType.EVOKES.value)
        if target_type is None:
            return neighbors
        return [
            n for n in neighbors
            if self.get_node_type(n["target"]) == target_type.value
        ]

    def get_avoided_targets(self, entry: str) -> Set[str]:
        """获取入口节点的所有 AVOIDS 目标"""
        neighbors = self.get_neighbors(entry, EdgeType.AVOIDS.value)
        return {n["target"] for n in neighbors}

    def get_conflicts(self, strategy: str) -> Set[str]:
        """获取与某策略互斥的其他策略"""
        neighbors = self.get_neighbors(strategy, EdgeType.CONFLICTS_WITH.value)
        return {n["target"] for n in neighbors}

    # ------------------------------------------------------------------
    # 推理链可视化
    # ------------------------------------------------------------------

    def visualize_inference_chain(self, keyword: str) -> Dict[str, Any]:
        """可视化完整推理链"""
        if not self.has_node(keyword):
            return {"error": f"关键词 '{keyword}' 不在图谱中"}

        node_type = self.get_node_type(keyword)
        emotion_hits = self.get_embodied_emotions(keyword)
        emotions = [e["target"] for e in emotion_hits]

        chain: Dict[str, Any] = {
            "keyword": keyword,
            "node_type": node_type,
            "emotions": emotions,
            "visual_elements": {},
        }

        for emo in emotions:
            strategies: Dict[str, List[str]] = {}
            for target_type in (
                NodeType.COLOR_STRATEGY,
                NodeType.TYPOGRAPHY_STYLE,
                NodeType.LAYOUT_PATTERN,
                NodeType.DECORATION_THEME,
            ):
                hits = self.get_evoked_strategies(emo, target_type)
                strategies[target_type.value] = [
                    f"{h['target']}(w={h['weight']})" for h in hits
                ]
            chain["visual_elements"][emo] = strategies

        return chain

    # ------------------------------------------------------------------
    # 统计
    # ------------------------------------------------------------------

    def get_stats(self) -> GraphStats:
        keywords = self.loader.get_supported_keywords()

        type_counts: Dict[str, int] = defaultdict(int)
        for _, d in self.graph.nodes(data=True):
            type_counts[d.get("node_type", "?")] += 1
        edge_counts: Dict[str, int] = defaultdict(int)
        for _, _, d in self.graph.edges(data=True):
            edge_counts[d.get("relation", "?")] += 1

        return GraphStats(
            node_count=self.node_count,
            edge_count=self.edge_count,
            rules_file=str(self.loader.ontology_file),
            version=self.loader.get_version(),
            industries=keywords.get("industries", []),
            vibes=keywords.get("vibes", []),
            emotions=keywords.get("emotions", []),
            node_type_counts=dict(type_counts),
            edge_type_counts=dict(edge_counts),
        )

    def rebuild(self) -> None:
        self.graph.clear()
        self.loader.clear_cache()
        self._build()
