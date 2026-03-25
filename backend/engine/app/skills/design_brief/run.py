"""
DesignBriefSkill 执行逻辑

LLM Prompt 模板定义在 prompt.md 的 "## Prompt Template" 段落中，
使用 {{$knowledge_context}}、{{$user_prompt}}、{{$key_elements}} 占位符。
本文件负责拼接变量、调用 render_prompt()、调用 LLM、解析 JSON 输出。
"""

import json
from typing import Dict, Any, Optional, List

from ..base import BaseSkill, SkillResult, render_template
from ..types import (
    DesignBriefInput,
    DesignBriefOutput,
    DesignRuleOutput,
    BrandContextOutput,
    IntentParseOutput,
)
from ...core.logger import get_logger

logger = get_logger(__name__)


def _build_knowledge_context(
    intent: IntentParseOutput,
    design_rules: DesignRuleOutput,
    brand_context: Optional[BrandContextOutput],
) -> str:
    """将上游 Skill 输出拼接为 LLM 可读的上下文（格式见 prompt.md）"""
    parts: List[str] = []

    parts.append("【意图解析】")
    if intent.industry:
        parts.append(f"- 行业: {intent.industry}")
    if intent.vibe:
        parts.append(f"- 风格: {intent.vibe}")
    parts.append(f"- 海报类型: {intent.poster_type}")
    if intent.brand_name:
        parts.append(f"- 品牌: {intent.brand_name}")
    if intent.key_elements:
        parts.append(f"- 关键元素: {', '.join(intent.key_elements)}")
    parts.append("")

    if not design_rules.is_empty():
        parts.append("【知识图谱推荐】")
        parts.append(f"- 情绪基调: {', '.join(design_rules.emotions)}")
        if design_rules.color_strategies:
            parts.append(f"- 配色策略: {', '.join(design_rules.color_strategies)}")
        palettes = design_rules.color_palettes
        if palettes.get("primary"):
            parts.append(f"- 主色调: {', '.join(palettes['primary'][:3])}")
        if palettes.get("accent"):
            parts.append(f"- 强调色: {', '.join(palettes['accent'][:2])}")
        if design_rules.typography_styles:
            parts.append(f"- 字体风格: {', '.join(design_rules.typography_styles)}")
        if design_rules.layout_patterns:
            parts.append(f"- 布局模式: {', '.join(design_rules.layout_patterns)}")
        if design_rules.design_principles:
            parts.append(f"- 设计原则: {', '.join(design_rules.design_principles)}")
        if design_rules.avoid:
            parts.append(f"- 避免使用: {', '.join(design_rules.avoid)}")
        parts.append("")

    if brand_context and brand_context.guidelines:
        parts.append("【品牌知识库】")
        for guideline in brand_context.guidelines:
            category = "通用"
            if brand_context.brand_colors and "description" in brand_context.brand_colors:
                if guideline == brand_context.brand_colors["description"]:
                    category = "配色方案"
            if brand_context.brand_style and guideline == brand_context.brand_style:
                category = "设计风格"
            parts.append(f"- [{category}] {guideline}")
        parts.append("")

    parts.append("【设计指导】")
    parts.append("请根据上述知识图谱推荐和品牌知识来生成设计简报。")
    parts.append("如果没有具体推荐，请根据用户意图自主决策。")

    return "\n".join(parts)


class DesignBriefSkill(BaseSkill[DesignBriefInput, DesignBriefOutput]):
    """
    设计简报生成技能

    从 prompt.md 加载 Prompt Template（含 {{$变量}} 占位符），
    填充知识上下文后调用 LLM。
    """

    def __init__(self, agent=None):
        super().__init__()
        self._agent = agent

    @property
    def agent(self):
        if self._agent is None:
            from ...agents.base import AgentFactory
            self._agent = AgentFactory.get_planner_agent()
        return self._agent

    def run(self, input: DesignBriefInput) -> SkillResult[DesignBriefOutput]:
        logger.info(f"📝 生成设计简报: {input.user_prompt[:50]}...")

        try:
            # 1. 构建知识上下文
            knowledge_context = _build_knowledge_context(
                input.intent, input.design_rules, input.brand_context
            )

            # 2. 用 {{$变量}} 渲染 System Prompt（从 prompt.md 读取）
            system_prompt = self.render_prompt({
                "knowledge_context": knowledge_context,
            })
            if not system_prompt:
                logger.warning("prompt.md 中无 Prompt Template，使用内置 fallback")
                system_prompt = _FALLBACK_PROMPT + "\n\n" + knowledge_context

            # 3. 用 {{$变量}} 渲染 User Prompt
            key_elements_str = ""
            if input.intent.key_elements:
                key_elements_str = f"（关键元素: {', '.join(input.intent.key_elements)}）"

            user_template = self.get_section("User Prompt Template")
            if user_template:
                user_content = render_template(user_template, {
                    "user_prompt": input.user_prompt,
                    "key_elements": key_elements_str,
                })
            else:
                user_content = input.user_prompt + ("\n" + key_elements_str if key_elements_str else "")

            # 4. 调用 LLM
            response = self.agent.invoke(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ]
            )

            content = response.choices[0].message.content
            brief_data = json.loads(content)

            if "intent" not in brief_data:
                brief_data["intent"] = input.intent.poster_type

            kg_primary = input.design_rules.get_primary_color()
            if not brief_data.get("main_color") and kg_primary:
                brief_data["main_color"] = kg_primary
                logger.info(f"🔮 使用 KG 推荐的主色调: {kg_primary}")

            decision_trace = self._build_decision_trace(brief_data, input)

            kg_rules_dict = (
                input.design_rules.to_dict()
                if not input.design_rules.is_empty()
                else None
            )
            brand_knowledge = None
            if input.brand_context and input.brand_context.source_documents:
                brand_knowledge = [
                    {
                        "text": doc.get("text", ""),
                        "category": doc.get("metadata", {}).get("category", ""),
                    }
                    for doc in input.brand_context.source_documents
                ]

            design_source = {
                "kg_keywords": input.intent.extracted_keywords,
                "kg_active": not input.design_rules.is_empty(),
                "rag_active": bool(
                    input.brand_context and input.brand_context.guidelines
                ),
                "brand_name": input.intent.brand_name,
                "skills_active": True,
            }

            output = DesignBriefOutput(
                title=brief_data.get("title", ""),
                subtitle=brief_data.get("subtitle", ""),
                main_color=brief_data.get("main_color", "#000000"),
                background_color=brief_data.get("background_color", "#FFFFFF"),
                style_keywords=brief_data.get("style_keywords", []),
                intent=brief_data.get("intent", "promotion"),
                decision_trace=decision_trace,
                kg_rules=kg_rules_dict,
                brand_knowledge=brand_knowledge,
                design_source=design_source,
            )

            logger.info(f"✅ 设计简报生成完成: {output.title}")
            return SkillResult.success(output, method="llm_generation")

        except json.JSONDecodeError as e:
            logger.error(f"❌ LLM 返回的 JSON 解析失败: {e}")
            return self._build_fallback(input, str(e))

        except Exception as e:
            logger.error(f"❌ 设计简报生成失败: {e}")
            return self._build_fallback(input, str(e))

    def _build_decision_trace(
        self, brief_data: Dict[str, Any], input: DesignBriefInput
    ) -> Dict[str, Any]:
        trace: Dict[str, Any] = {"intent_source": "intent_parse_skill"}
        kg_primary = input.design_rules.get_primary_color()
        if kg_primary and brief_data.get("main_color") == kg_primary:
            trace["main_color_source"] = "kg_inference"
        else:
            trace["main_color_source"] = "llm_generation"
        if not input.design_rules.is_empty():
            trace["design_rules_source"] = "kg_inference"
            trace["emotions"] = input.design_rules.emotions
        if input.brand_context and input.brand_context.guidelines:
            trace["brand_source"] = "rag_retrieval"
            trace["brand_name"] = input.brand_context.brand_name
        return trace

    def _build_fallback(
        self, input: DesignBriefInput, error: str
    ) -> SkillResult[DesignBriefOutput]:
        from ...core.config import ERROR_FALLBACKS

        fallback = ERROR_FALLBACKS["planner"]
        kg_primary = input.design_rules.get_primary_color()

        output = DesignBriefOutput(
            title=fallback["title"],
            subtitle=fallback["subtitle"],
            main_color=kg_primary or fallback["main_color"],
            background_color=fallback["background_color"],
            style_keywords=fallback["style_keywords"],
            intent=input.intent.poster_type or fallback["intent"],
            decision_trace={"source": "fallback", "error": error},
            design_source={
                "kg_keywords": input.intent.extracted_keywords,
                "kg_active": not input.design_rules.is_empty(),
                "rag_active": False,
                "brand_name": input.intent.brand_name,
                "skills_active": True,
            },
        )
        return SkillResult.partial(output, error=error, method="fallback")


_FALLBACK_PROMPT = """你是一个专业的海报设计总监。你的任务是将用户的模糊需求转化为结构化的设计简报。
请严格按照以下 JSON 格式输出：
{
    "title": "海报主标题",
    "subtitle": "副标题",
    "main_color": "#FF0000",
    "background_color": "#FFFFFF",
    "style_keywords": ["keyword1", "keyword2"],
    "intent": "promotion"
}"""
