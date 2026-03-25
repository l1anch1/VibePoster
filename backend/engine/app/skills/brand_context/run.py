"""
BrandContextSkill 执行逻辑

从 RAG 知识库按 color/style/guideline 三个方面检索品牌知识。
检索策略和查询模板见 skill.md。
"""

from typing import Dict, Any, List, Optional

from ..base import BaseSkill, SkillResult
from ..types import BrandContextInput, BrandContextOutput
from ...core.logger import get_logger
from ...core.interfaces import IKnowledgeBase

logger = get_logger(__name__)

ASPECT_QUERY_TEMPLATES: Dict[str, str] = {
    "color": "{brand_name}的配色",
    "style": "{brand_name}设计风格",
    "guideline": "{brand_name}设计规范",
}


class BrandContextSkill(BaseSkill[BrandContextInput, BrandContextOutput]):
    """
    品牌上下文检索技能

    从 RAG 知识库中检索品牌配色、风格、设计规范。
    详细说明见 skill.md。
    """

    def __init__(self, knowledge_base: Optional[IKnowledgeBase] = None):
        super().__init__()
        self._knowledge_base = knowledge_base
        self._kb_initialized = knowledge_base is not None

    @property
    def knowledge_base(self) -> IKnowledgeBase:
        if not self._kb_initialized:
            from ...core.dependencies import get_knowledge_base
            logger.debug("延迟初始化 KnowledgeBase")
            self._knowledge_base = get_knowledge_base()
            self._kb_initialized = True
        return self._knowledge_base

    def run(self, input: BrandContextInput) -> SkillResult[BrandContextOutput]:
        brand_name = input.brand_name
        logger.info(f"📚 检索品牌上下文: {brand_name}, aspects={input.aspects}")

        try:
            all_documents: List[Dict[str, Any]] = []
            guidelines: List[str] = []
            brand_colors: Dict[str, str] = {}
            brand_style: Optional[str] = None

            for aspect in input.aspects:
                query_template = ASPECT_QUERY_TEMPLATES.get(
                    aspect, "{brand_name}" + aspect
                )
                query = query_template.format(brand_name=brand_name)
                filter_metadata = {"brand": brand_name}
                results = self.knowledge_base.search(
                    query, top_k=1, filter_metadata=filter_metadata
                )

                for doc in results:
                    all_documents.append(doc)
                    text = doc.get("text", "")
                    category = doc.get("metadata", {}).get("category", "")

                    if "配色" in category or aspect == "color":
                        brand_colors["description"] = text
                    elif "风格" in category or aspect == "style":
                        brand_style = text

                    if text:
                        guidelines.append(text)

            logger.info(f"📚 检索到 {len(all_documents)} 条品牌知识")

            output = BrandContextOutput(
                brand_name=brand_name,
                brand_colors=brand_colors,
                brand_style=brand_style,
                guidelines=guidelines,
                source_documents=all_documents,
            )
            return SkillResult.success(output, method="rag_retrieval")

        except Exception as e:
            logger.error(f"❌ 品牌上下文检索失败: {e}")
            return SkillResult.partial(
                BrandContextOutput(brand_name=brand_name),
                error=str(e),
                method="fallback",
            )
