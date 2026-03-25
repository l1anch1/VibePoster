"""
VibePoster MCP Server

将海报设计能力通过 MCP 协议标准化暴露，
任何支持 MCP 的 AI 助手都可以调用。

Tools:
- analyze_intent: 分析用户输入的设计意图
- infer_design_rules: 基于行业/风格推理设计规则
- search_brand_knowledge: 检索品牌设计规范
- generate_design_brief: 生成完整的设计简报
- generate_poster: 生成海报（调用完整工作流）

Resources:
- vibeposter://industries: 支持的行业列表
- vibeposter://vibes: 支持的风格列表
- vibeposter://emotions: 情绪-视觉映射规则
- vibeposter://stats: 知识图谱和知识库统计信息

Usage:
    # 直接运行
    python -m app.mcp.server

    # 或在 Cursor / Claude Desktop 中配置：
    {
        "mcpServers": {
            "vibeposter": {
                "command": "python",
                "args": ["-m", "app.mcp.server"],
                "cwd": "/path/to/backend/engine"
            }
        }
    }

Author: VibePoster Team
Date: 2025-01
"""

import json
import sys
import os
from typing import Optional

from mcp.server.fastmcp import FastMCP

# 确保项目根目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# ============================================================================
# 初始化 MCP Server
# ============================================================================

mcp = FastMCP(
    "VibePoster",
    description="AI 海报设计助手 - 通过多 Agent 协作和知识图谱生成专业海报",
)


# ============================================================================
# 延迟初始化（避免启动时加载全部依赖）
# ============================================================================

_skills_initialized = False


def _ensure_skills():
    """确保 Skills 已初始化"""
    global _skills_initialized
    if not _skills_initialized:
        # 加载 dotenv
        from dotenv import load_dotenv
        load_dotenv()
        _skills_initialized = True


def _get_intent_skill():
    _ensure_skills()
    from app.core.dependencies import get_intent_parse_skill
    return get_intent_parse_skill()


def _get_rule_skill():
    _ensure_skills()
    from app.core.dependencies import get_design_rule_skill
    return get_design_rule_skill()


def _get_brand_skill():
    _ensure_skills()
    from app.core.dependencies import get_brand_context_skill
    return get_brand_context_skill()


def _get_brief_skill():
    _ensure_skills()
    from app.core.dependencies import get_design_brief_skill
    return get_design_brief_skill()


# ============================================================================
# Tools - 可执行的能力
# ============================================================================

@mcp.tool()
def analyze_intent(
    prompt: str,
) -> str:
    """
    分析用户输入的设计意图。

    从自然语言中提取行业、风格、海报类型、品牌名称等结构化信息。
    
    示例输入: "帮我做一个华为科技风的极简海报"
    
    Args:
        prompt: 用户的海报需求描述
    """
    from app.skills import IntentParseInput

    skill = _get_intent_skill()
    result = skill(IntentParseInput(user_prompt=prompt))

    if result.output:
        output = result.output.to_dict()
        return json.dumps(output, ensure_ascii=False, indent=2)
    else:
        return json.dumps({"error": result.error}, ensure_ascii=False)


@mcp.tool()
def infer_design_rules(
    industry: Optional[str] = None,
    vibe: Optional[str] = None,
) -> str:
    """
    基于行业和风格，从知识图谱推理设计规则。

    返回推荐的情绪基调、配色方案、字体风格、布局模式等。
    知识图谱数据来源于《创意海报版式设计》和《Photoshop海报设计》。

    支持的行业: Tech, Food, Luxury, Healthcare, Education, Entertainment
    支持的风格: Minimalist, Energetic, Professional, Friendly, Bold

    Args:
        industry: 行业关键词，如 Tech、Food、Luxury
        vibe: 风格关键词，如 Minimalist、Energetic、Bold
    """
    from app.skills import DesignRuleInput

    skill = _get_rule_skill()
    result = skill(DesignRuleInput(industry=industry, vibe=vibe))

    if result.output:
        output = result.output.to_dict()
        return json.dumps(output, ensure_ascii=False, indent=2)
    else:
        return json.dumps({"error": result.error}, ensure_ascii=False)


@mcp.tool()
def search_brand_knowledge(
    brand_name: str,
) -> str:
    """
    检索品牌相关的设计规范和知识。

    从 RAG 知识库中检索品牌的配色方案、设计风格、设计规范等信息。

    Args:
        brand_name: 品牌名称，如 华为、苹果、小米
    """
    from app.skills import BrandContextInput

    skill = _get_brand_skill()
    result = skill(BrandContextInput(brand_name=brand_name))

    if result.output:
        output = result.output.to_dict()
        return json.dumps(output, ensure_ascii=False, indent=2)
    else:
        return json.dumps({"error": result.error}, ensure_ascii=False)


@mcp.tool()
def generate_design_brief(
    prompt: str,
    brand_name: Optional[str] = None,
) -> str:
    """
    生成完整的设计简报。

    综合意图解析、知识图谱推理、品牌知识检索，
    通过 LLM 生成包含标题、配色、风格关键词的设计简报。

    这是一个复合调用，内部依次执行：
    1. 意图解析（IntentParseSkill）
    2. 设计规则推理（DesignRuleSkill）
    3. 品牌知识检索（BrandContextSkill，如有品牌名）
    4. LLM 生成设计简报（DesignBriefSkill）

    Args:
        prompt: 用户的海报需求描述
        brand_name: 品牌名称（可选，用于检索品牌设计规范）
    """
    from app.skills import SkillOrchestrator

    _ensure_skills()

    orchestrator = SkillOrchestrator(
        intent_skill=_get_intent_skill(),
        rule_skill=_get_rule_skill(),
        brand_skill=_get_brand_skill(),
        brief_skill=_get_brief_skill(),
    )

    context = orchestrator.run(
        user_prompt=prompt,
        brand_name=brand_name,
    )

    result = context.to_dict()
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def generate_poster(
    prompt: str,
    brand_name: Optional[str] = None,
    canvas_width: int = 1080,
    canvas_height: int = 1920,
) -> str:
    """
    生成完整的海报。

    调用完整的 4-Agent 工作流：
    Planner(Skills) → Visual(Flux) → Layout → Critic
    
    返回可渲染的海报 JSON 数据（包含图层、样式、位置等）。

    Args:
        prompt: 用户的海报需求描述
        brand_name: 品牌名称（可选）
        canvas_width: 画布宽度（默认 1080）
        canvas_height: 画布高度（默认 1920）
    """
    _ensure_skills()

    from app.services.poster_service import PosterService

    service = PosterService()
    poster_data = service.generate_poster(
        prompt=prompt,
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        brand_name=brand_name,
    )

    return json.dumps(poster_data, ensure_ascii=False, indent=2)


# ============================================================================
# Resources - 只读数据
# ============================================================================

@mcp.resource("vibeposter://industries")
def get_industries() -> str:
    """VibePoster 支持的行业列表及描述"""
    _ensure_skills()

    try:
        from app.core.dependencies import get_knowledge_graph
        kg = get_knowledge_graph()
        keywords = kg.get_supported_keywords()
        industries = keywords.get("industries", [])

        result = {
            "description": "VibePoster 知识图谱支持的行业列表",
            "source": "《创意海报版式设计》《Photoshop海报设计》",
            "industries": industries,
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "industries": ["Tech", "Food", "Luxury", "Healthcare", "Education", "Entertainment"],
            "error": str(e)
        }, ensure_ascii=False, indent=2)


@mcp.resource("vibeposter://vibes")
def get_vibes() -> str:
    """VibePoster 支持的设计风格列表及描述"""
    try:
        _ensure_skills()
        from app.core.dependencies import get_knowledge_graph
        kg = get_knowledge_graph()
        keywords = kg.get_supported_keywords()
        vibes = keywords.get("vibes", [])

        result = {
            "description": "VibePoster 知识图谱支持的设计风格列表",
            "vibes": vibes,
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "vibes": ["Minimalist", "Energetic", "Professional", "Friendly", "Bold"],
            "error": str(e)
        }, ensure_ascii=False, indent=2)


@mcp.resource("vibeposter://emotions")
def get_emotions() -> str:
    """VibePoster 知识图谱中的情绪-视觉映射规则"""
    try:
        _ensure_skills()
        from app.core.dependencies import get_knowledge_graph
        kg = get_knowledge_graph()
        keywords = kg.get_supported_keywords()
        emotions = keywords.get("emotions", [])

        # 获取每个情绪的视觉规则
        emotion_details = {}
        for emotion in emotions:
            rules = kg.get_emotion_visual_rules(emotion)
            if rules:
                emotion_details[emotion] = rules

        result = {
            "description": "情绪语义层：从行业/风格推理出情绪，再映射到视觉元素",
            "inference_chain": "Industry/Vibe → Emotion → Visual Elements (配色、字体、布局)",
            "emotions": emotions,
            "details": emotion_details,
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "emotions": ["Trust", "Innovation", "Premium", "Excitement", "Warmth", "Freshness", "Playfulness"],
            "error": str(e)
        }, ensure_ascii=False, indent=2)


@mcp.resource("vibeposter://stats")
def get_stats() -> str:
    """VibePoster 知识图谱和知识库的统计信息"""
    stats = {}

    try:
        _ensure_skills()
        from app.core.dependencies import get_knowledge_graph, get_knowledge_base

        kg = get_knowledge_graph()
        stats["knowledge_graph"] = kg.get_graph_stats()
    except Exception as e:
        stats["knowledge_graph"] = {"error": str(e)}

    try:
        kb = get_knowledge_base()
        stats["knowledge_base"] = kb.get_stats()
    except Exception as e:
        stats["knowledge_base"] = {"error": str(e)}

    return json.dumps(stats, ensure_ascii=False, indent=2)


# ============================================================================
# 入口
# ============================================================================

if __name__ == "__main__":
    mcp.run()
