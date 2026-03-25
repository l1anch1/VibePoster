"""
Skills 模块 - 模块化能力封装（MD 核心模式）

每个 Skill 是一个独立目录:
  skills/
    intent_parse/   skill.md + run.py
    design_rule/    skill.md + run.py
    brand_context/  skill.md + run.py
    design_brief/   skill.md + run.py

skill.md 是核心描述文件，包含：
  - YAML frontmatter: name, description, input/output schema, version, tags
  - Markdown 正文: 详细说明、Prompt 模板、示例、约束

run.py 只负责执行逻辑，BaseSkill 自动加载 skill.md。
"""

from .base import BaseSkill, SkillResult, SkillStatus, SkillConfig, InputVariable, load_config, load_prompt_md, render_template
from .types import (
    IntentParseInput,
    IntentParseOutput,
    DesignRuleInput,
    DesignRuleOutput,
    BrandContextInput,
    BrandContextOutput,
    DesignBriefInput,
    DesignBriefOutput,
    PosterType,
    Industry,
    Vibe,
)
from .intent_parse import IntentParseSkill
from .design_rule import DesignRuleSkill
from .brand_context import BrandContextSkill
from .design_brief import DesignBriefSkill
from .orchestrator import SkillOrchestrator, PlannerContext

__all__ = [
    # 基类 & 工具
    "BaseSkill",
    "SkillResult",
    "SkillStatus",
    "SkillConfig",
    "InputVariable",
    "load_config",
    "load_prompt_md",
    "render_template",
    # 枚举
    "PosterType",
    "Industry",
    "Vibe",
    # 类型
    "IntentParseInput",
    "IntentParseOutput",
    "DesignRuleInput",
    "DesignRuleOutput",
    "BrandContextInput",
    "BrandContextOutput",
    "DesignBriefInput",
    "DesignBriefOutput",
    # Skills
    "IntentParseSkill",
    "DesignRuleSkill",
    "BrandContextSkill",
    "DesignBriefSkill",
    # Orchestrator
    "SkillOrchestrator",
    "PlannerContext",
]
