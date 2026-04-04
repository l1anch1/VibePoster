"""
DesignRuleSkill 执行逻辑

支持多模态意图融合：
1. 文字模态：从 industry/vibe 正向推理到 Emotion
2. 视觉模态：从参考图 VLM 分析逆向映射到 Emotion
3. 否定约束：动态注入 KG AVOIDS

融合公式：S_final(e) = α·S_text(e) + β·S_visual(e)
其中 α, β 基于各模态置信度动态计算。
"""

from typing import Dict, Any, List, Optional, Set, Tuple

from ..base import BaseSkill, SkillResult
from ..types import DesignRuleInput, DesignRuleOutput
from ...core.logger import get_logger
from ...core.interfaces import IKnowledgeGraph

logger = get_logger(__name__)


class DesignRuleSkill(BaseSkill[DesignRuleInput, DesignRuleOutput]):
    """
    设计规则推理技能（多模态融合版）

    从知识图谱获取设计规则，支持文字+视觉双模态意图融合。
    """

    def __init__(self, knowledge_graph: Optional[IKnowledgeGraph] = None):
        super().__init__()
        self._knowledge_graph = knowledge_graph
        self._kg_initialized = knowledge_graph is not None

    @property
    def knowledge_graph(self) -> IKnowledgeGraph:
        if not self._kg_initialized:
            from ...core.dependencies import get_knowledge_graph
            logger.debug("延迟初始化 KnowledgeGraph")
            self._knowledge_graph = get_knowledge_graph()
            self._kg_initialized = True
        return self._knowledge_graph

    def run(self, input: DesignRuleInput) -> SkillResult[DesignRuleOutput]:
        text_keywords = input.get_all_keywords()

        # 多模态融合：文字 + 视觉 → 统一的 Emotion 入口
        fused_keywords, dynamic_avoids = self._fuse_multimodal(
            text_keywords=text_keywords,
            image_analyses=input.image_analyses,
            negative_constraints=input.negative_constraints,
        )

        if not fused_keywords:
            logger.warning("多模态融合后无关键词，返回空规则")
            return SkillResult.success(
                DesignRuleOutput(source_keywords=text_keywords),
                method="empty_input",
            )

        logger.info(f"🔮 多模态融合后关键词: {fused_keywords}, 动态约束: {dynamic_avoids}")

        try:
            kg_result = self.knowledge_graph.infer_rules(
                fused_keywords, extra_avoids=dynamic_avoids,
            )
            output = self._convert_kg_result(kg_result, fused_keywords)
            logger.info(
                f"✅ KG 推理完成: emotions={output.emotions}, "
                f"strategies={output.color_strategies[:2]}..."
            )
            return SkillResult.success(output, method="multimodal_fusion")

        except Exception as e:
            logger.error(f"❌ KG 推理失败: {e}")
            return SkillResult.partial(
                DesignRuleOutput(source_keywords=text_keywords),
                error=str(e),
                method="fallback",
            )

    # ------------------------------------------------------------------
    # 多模态融合（D: Cross-Modal Intent Alignment）
    # ------------------------------------------------------------------

    def _fuse_multimodal(
        self,
        text_keywords: List[str],
        image_analyses: Optional[List[Dict[str, Any]]],
        negative_constraints: List[str],
    ) -> Tuple[List[str], Set[str]]:
        """
        融合文字+视觉模态，返回 (推理关键词, 动态AVOIDS)

        当无参考图时，退化为原始行为（直接用 text_keywords）。
        当有参考图时，把 VLM 特征逆向映射到 Emotion，与文字模态加权融合。
        """
        # 如果没有参考图且没有否定约束，走原始路径（兼容）
        if not image_analyses and not negative_constraints:
            return text_keywords, set()

        # S_text: 从 industry/vibe 获取 Emotion 得分
        text_emotions: Dict[str, float] = {}
        if text_keywords:
            kg = self.knowledge_graph
            if hasattr(kg, '_graph'):
                graph = kg._graph
                for kw in text_keywords:
                    if hasattr(graph, 'get_embodied_emotions'):
                        for hit in graph.get_embodied_emotions(kw):
                            emo = hit["target"]
                            text_emotions[emo] = max(
                                text_emotions.get(emo, 0), hit["weight"]
                            )

        # S_visual: 从参考图逆向映射 Emotion
        visual_emotions: Dict[str, float] = {}
        if image_analyses:
            try:
                from ..visual_intent.mapper import VisualIntentMapper
                mapper = VisualIntentMapper()
                graph_obj = getattr(self.knowledge_graph, '_graph', None)
                for item in image_analyses:
                    understanding = (
                        item.get("analysis", {}).get("understanding", {})
                        or item.get("understanding", {})
                    )
                    if understanding:
                        ve = mapper.map_visual_to_emotions(understanding, graph_obj)
                        for emo, score in ve.items():
                            visual_emotions[emo] = max(
                                visual_emotions.get(emo, 0), score
                            )
            except Exception as e:
                logger.warning(f"视觉意图映射失败: {e}")

        # 融合权重：基于各模态是否有结果
        has_text = bool(text_emotions)
        has_visual = bool(visual_emotions)

        if has_text and has_visual:
            alpha, beta = 0.6, 0.4  # 文字优先
        elif has_text:
            alpha, beta = 1.0, 0.0
        elif has_visual:
            alpha, beta = 0.0, 1.0
        else:
            return text_keywords, set(negative_constraints)

        # 加权融合
        all_emotions = set(text_emotions.keys()) | set(visual_emotions.keys())
        fused: Dict[str, float] = {}
        for emo in all_emotions:
            score = (alpha * text_emotions.get(emo, 0)
                     + beta * visual_emotions.get(emo, 0))
            fused[emo] = score

        # 取 score > 0.3 的 Emotion 作为推理入口
        top_emotions = [
            e for e, s in sorted(fused.items(), key=lambda x: -x[1])
            if s > 0.3
        ]

        if top_emotions:
            logger.info(
                f"🔗 多模态融合: text={text_emotions}, visual={visual_emotions}"
                f" → fused_top={top_emotions}"
            )
            return top_emotions, set(negative_constraints)

        # 融合失败时回退到文字关键词
        return text_keywords, set(negative_constraints)

    def _convert_kg_result(
        self, kg_result: Dict[str, Any], source_keywords: List[str]
    ) -> DesignRuleOutput:
        return DesignRuleOutput(
            emotions=kg_result.get("emotions", []),
            color_strategies=kg_result.get("color_strategies", []),
            color_palettes=kg_result.get("color_palettes", {}),
            typography_styles=kg_result.get("typography_styles", []),
            typography_weights=kg_result.get("typography_weights", []),
            typography_characteristics=kg_result.get("typography_characteristics", []),
            layout_strategies=kg_result.get("layout_strategies", []),
            layout_intents=kg_result.get("layout_intents", []),
            layout_patterns=kg_result.get("layout_patterns", []),
            decoration_styles=kg_result.get("decoration_styles", {}),
            inference_traces=kg_result.get("inference_traces", []),
            design_principles=kg_result.get("design_principles", []),
            avoid=kg_result.get("avoid", []),
            source_keywords=source_keywords,
        )

    def get_supported_keywords(self) -> Dict[str, List[str]]:
        try:
            if hasattr(self.knowledge_graph, "get_supported_keywords"):
                return self.knowledge_graph.get_supported_keywords()
        except Exception as e:
            logger.warning(f"获取支持的关键词失败: {e}")
        return {
            "industries": ["Tech", "Food", "Luxury", "Healthcare", "Education", "Entertainment"],
            "vibes": ["Minimalist", "Energetic", "Professional", "Friendly", "Bold"],
            "emotions": ["Trust", "Innovation", "Premium", "Excitement", "Warmth", "Freshness"],
        }

