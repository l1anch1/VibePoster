"""
本体推理引擎 v3

多跳图遍历推理：
    Phase 1  Entry → Emotion        收集情绪集合 + 入口约束
    Phase 2  Emotion → Strategy     按类型收集视觉策略（带权重）
    Phase 3  冲突消解               CONFLICTS_WITH 互斥对中保留高权重方
    Phase 4  AVOIDS 过滤            移除入口禁忌策略
    Phase 5  聚合具象参数           色值、字重、布局模式等
    Phase 6  构建推理链追踪         每条路径 (entry → emotion → strategy) 记录
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from collections import defaultdict

from .types import InferenceResult, InferenceTrace, NodeType
from .graph import DesignGraph
from ...core.logger import get_logger

logger = get_logger(__name__)


class _StrategyHit:
    """中间结构：一条 Emotion→Strategy 的命中记录"""
    __slots__ = ("name", "node_type", "weight", "context", "source_emotions")

    def __init__(
        self, name: str, node_type: str, weight: float,
        context: Dict[str, Any], source_emotion: str,
    ):
        self.name = name
        self.node_type = node_type
        self.weight = weight
        self.context = context
        self.source_emotions: Set[str] = {source_emotion}

    def merge_weight(self, weight: float, emotion: str) -> None:
        """同名策略从不同情绪到达时，取最大权重并记录来源"""
        self.weight = max(self.weight, weight)
        self.source_emotions.add(emotion)


class InferenceEngine:
    """本体推理引擎 v3 — 多跳图遍历 + 冲突消解"""

    def __init__(self, graph: DesignGraph):
        self.graph = graph

    # ==================================================================
    # 公共接口
    # ==================================================================

    def infer(
        self, keywords: List[str], extra_avoids: Optional[Set[str]] = None,
    ) -> InferenceResult:
        if not keywords:
            return InferenceResult()

        # Phase 1: 收集情绪 + 入口约束
        emotions_weighted, entry_avoids, design_principles, avoid_texts = (
            self._phase1_collect_emotions(keywords)
        )

        if not emotions_weighted:
            logger.debug(f"关键词 {keywords} 未命中任何情绪节点")
            return InferenceResult()

        emotion_names = list(emotions_weighted.keys())

        # Phase 2: 多跳遍历 Emotion → Strategy
        strategy_map = self._phase2_traverse_strategies(emotions_weighted)

        # Phase 3: 冲突消解
        self._phase3_resolve_conflicts(strategy_map)

        # Phase 4: AVOIDS 过滤（合并本体 AVOIDS + 动态否定约束）
        all_avoids = entry_avoids | (extra_avoids or set())
        self._phase4_apply_avoids(strategy_map, all_avoids)

        # Phase 5: 聚合结果
        result = self._phase5_aggregate(
            emotion_names, strategy_map, design_principles, avoid_texts
        )

        # Phase 6: 构建推理链
        result.inference_traces = self._phase6_build_traces(
            keywords, emotions_weighted, strategy_map
        )

        logger.info(
            f"本体推理完成: Keywords={keywords} → "
            f"Emotions={emotion_names} → "
            f"ColorStrategies={result.color_strategies}, "
            f"LayoutPatterns={len(result.layout_patterns)}, "
            f"Traces={len(result.inference_traces)}"
        )
        return result

    def infer_single(self, keyword: str) -> InferenceResult:
        return self.infer([keyword])

    # ==================================================================
    # Phase 1: 收集情绪
    # ==================================================================

    def _phase1_collect_emotions(
        self, keywords: List[str]
    ) -> Tuple[
        Dict[str, float],       # emotion → max_weight
        Set[str],               # avoids (node IDs)
        List[str],              # design_principles
        List[str],              # avoid texts
    ]:
        emotions: Dict[str, float] = {}
        avoids: Set[str] = set()
        principles: List[str] = []
        avoid_texts: List[str] = []

        for kw in keywords:
            if not self.graph.has_node(kw):
                logger.debug(f"关键词 '{kw}' 不在本体中")
                continue

            emotion_hits = self.graph.get_embodied_emotions(kw)
            for hit in emotion_hits:
                emo_name = hit["target"]
                emo_weight = hit["weight"]
                emotions[emo_name] = max(emotions.get(emo_name, 0.0), emo_weight)

            avoids.update(self.graph.get_avoided_targets(kw))

            node_data = self.graph.get_node_data(kw) or {}
            principles.extend(node_data.get("design_principles", []))
            avoid_texts.extend(node_data.get("avoid", []))

        return emotions, avoids, list(set(principles)), list(set(avoid_texts))

    # ==================================================================
    # Phase 2: 多跳遍历
    # ==================================================================

    def _phase2_traverse_strategies(
        self, emotions: Dict[str, float]
    ) -> Dict[str, _StrategyHit]:
        """Emotion → Strategy 遍历，按策略名聚合"""
        hits: Dict[str, _StrategyHit] = {}

        for emotion_name, emo_weight in emotions.items():
            neighbors = self.graph.get_neighbors(emotion_name, "evokes")
            for nb in neighbors:
                target = nb["target"]
                edge_weight = nb["weight"]
                combined_weight = emo_weight * edge_weight
                node_type = self.graph.get_node_type(target) or ""

                if target in hits:
                    hits[target].merge_weight(combined_weight, emotion_name)
                    if nb["context"]:
                        if not hits[target].context:
                            hits[target].context = nb["context"]
                        else:
                            self._merge_context(hits[target].context, nb["context"])
                else:
                    hits[target] = _StrategyHit(
                        name=target,
                        node_type=node_type,
                        weight=combined_weight,
                        context=dict(nb.get("context", {})),
                        source_emotion=emotion_name,
                    )
        return hits

    @staticmethod
    def _merge_context(existing: Dict[str, Any], incoming: Dict[str, Any]) -> None:
        """合并同名策略的多条 EVOKES 边上下文"""
        for key, val in incoming.items():
            if key == "characteristics" and isinstance(val, list):
                prev = existing.get("characteristics", [])
                existing["characteristics"] = list(set(prev + val))
            elif key not in existing:
                existing[key] = val

    # ==================================================================
    # Phase 3: 冲突消解
    # ==================================================================

    def _phase3_resolve_conflicts(self, hits: Dict[str, _StrategyHit]) -> None:
        """CONFLICTS_WITH 互斥对中移除低权重方"""
        to_remove: Set[str] = set()
        checked: Set[frozenset] = set()

        for name in list(hits.keys()):
            conflicts = self.graph.get_conflicts(name)
            for rival in conflicts:
                pair = frozenset((name, rival))
                if pair in checked or rival not in hits:
                    continue
                checked.add(pair)

                if hits[name].weight >= hits[rival].weight:
                    to_remove.add(rival)
                    logger.debug(
                        f"冲突消解: 保留 {name}(w={hits[name].weight:.2f}), "
                        f"移除 {rival}(w={hits[rival].weight:.2f})"
                    )
                else:
                    to_remove.add(name)
                    logger.debug(
                        f"冲突消解: 保留 {rival}(w={hits[rival].weight:.2f}), "
                        f"移除 {name}(w={hits[name].weight:.2f})"
                    )

        for name in to_remove:
            hits.pop(name, None)

    # ==================================================================
    # Phase 4: AVOIDS 过滤
    # ==================================================================

    @staticmethod
    def _phase4_apply_avoids(
        hits: Dict[str, _StrategyHit], avoids: Set[str]
    ) -> None:
        for name in list(hits.keys()):
            if name in avoids:
                logger.debug(f"AVOIDS 过滤: 移除 {name}")
                del hits[name]

    # ==================================================================
    # Phase 5: 聚合结果
    # ==================================================================

    def _phase5_aggregate(
        self,
        emotion_names: List[str],
        hits: Dict[str, _StrategyHit],
        design_principles: List[str],
        avoid_texts: List[str],
    ) -> InferenceResult:
        color_strategies: Set[str] = set()
        color_palettes: Dict[str, List[str]] = {}
        typography_styles: Set[str] = set()
        typography_weights: Set[str] = set()
        typography_chars: Set[str] = set()
        layout_strategies: Set[str] = set()
        layout_intents: Set[str] = set()
        layout_patterns: Set[str] = set()
        decoration_styles: Dict[str, Any] = {}
        best_deco_weight: float = -1.0

        for emo_name in emotion_names:
            emo_data = self.graph.get_node_data(emo_name) or {}
            emo_palettes = emo_data.get("palettes", {})
            for pal_key, colors in emo_palettes.items():
                if pal_key not in color_palettes:
                    color_palettes[pal_key] = []
                color_palettes[pal_key].extend(colors)

        for pal_key in color_palettes:
            color_palettes[pal_key] = list(set(color_palettes[pal_key]))

        nt = NodeType

        for hit in hits.values():
            if hit.node_type == nt.COLOR_STRATEGY.value:
                color_strategies.add(hit.name)

            elif hit.node_type == nt.TYPOGRAPHY_STYLE.value:
                typography_styles.add(hit.name)
                ctx = hit.context
                if ctx.get("weight"):
                    typography_weights.add(ctx["weight"])
                typography_chars.update(ctx.get("characteristics", []))

            elif hit.node_type == nt.LAYOUT_PATTERN.value:
                lp_data = self.graph.get_node_data(hit.name) or {}
                layout_strategies.add(lp_data.get("strategy", ""))
                layout_intents.add(lp_data.get("intent", ""))
                layout_patterns.update(lp_data.get("patterns", [hit.name]))

            elif hit.node_type == nt.DECORATION_THEME.value:
                if hit.weight > best_deco_weight:
                    best_deco_weight = hit.weight
                    dt_data = self.graph.get_node_data(hit.name) or {}
                    decoration_styles = {}
                    for deco_key in ("divider", "overlay", "shape"):
                        if deco_key in dt_data:
                            decoration_styles[deco_key] = dt_data[deco_key]

        layout_strategies.discard("")
        layout_intents.discard("")

        return InferenceResult(
            emotions=emotion_names,
            color_strategies=sorted(color_strategies),
            color_palettes=color_palettes,
            typography_styles=sorted(typography_styles),
            typography_weights=sorted(typography_weights),
            typography_characteristics=sorted(typography_chars),
            layout_strategies=sorted(layout_strategies),
            layout_intents=sorted(layout_intents),
            layout_patterns=sorted(layout_patterns),
            decoration_styles=decoration_styles,
            design_principles=design_principles,
            avoid=avoid_texts,
        )

    # ==================================================================
    # Phase 6: 推理链追踪
    # ==================================================================

    def _phase6_build_traces(
        self,
        keywords: List[str],
        emotions: Dict[str, float],
        hits: Dict[str, _StrategyHit],
    ) -> List[InferenceTrace]:
        # 构建 keyword → emotion 的真实映射，避免伪路径
        kw_to_emotions: Dict[str, Set[str]] = {}
        for kw in keywords:
            if not self.graph.has_node(kw):
                continue
            for emo_hit in self.graph.get_embodied_emotions(kw):
                kw_to_emotions.setdefault(kw, set()).add(emo_hit["target"])

        traces: List[InferenceTrace] = []
        for hit in hits.values():
            for emo in hit.source_emotions:
                for kw, emo_set in kw_to_emotions.items():
                    if emo not in emo_set:
                        continue  # 跳过伪路径：该 keyword 并不 EMBODIES 该 emotion
                    traces.append(InferenceTrace(
                        path=[kw, emo, hit.name],
                        relation_chain=["EMBODIES", "EVOKES"],
                        weight=hit.weight,  # 已是 emo_weight * edge_weight，不再重复乘
                    ))
        return traces
