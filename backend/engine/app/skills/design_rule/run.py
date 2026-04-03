"""
DesignRuleSkill 执行逻辑

调用 KnowledgeGraph.infer_rules 获取设计规则。
推理链路和输出字段说明见 skill.md。
"""

from typing import Dict, Any, List, Optional

from ..base import BaseSkill, SkillResult
from ..types import DesignRuleInput, DesignRuleOutput
from ...core.logger import get_logger
from ...core.interfaces import IKnowledgeGraph

logger = get_logger(__name__)


class DesignRuleSkill(BaseSkill[DesignRuleInput, DesignRuleOutput]):
    """
    设计规则推理技能

    从知识图谱获取 Industry/Vibe → Emotion → Visual Elements 的完整推理结果。
    详细说明见 skill.md。
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
        keywords = input.get_all_keywords()

        if not keywords:
            logger.warning("没有提供关键词，返回空规则")
            return SkillResult.success(
                DesignRuleOutput(source_keywords=[]),
                method="empty_input",
            )

        logger.info(f"🔮 KG 推理关键词: {keywords}")

        try:
            kg_result = self.knowledge_graph.infer_rules(keywords)
            output = self._convert_kg_result(kg_result, keywords)
            logger.info(
                f"✅ KG 推理完成: emotions={output.emotions}, "
                f"strategies={output.color_strategies[:2]}..."
            )
            return SkillResult.success(output, method="knowledge_graph")

        except Exception as e:
            logger.error(f"❌ KG 推理失败: {e}")
            return SkillResult.partial(
                DesignRuleOutput(source_keywords=keywords),
                error=str(e),
                method="fallback",
            )

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

