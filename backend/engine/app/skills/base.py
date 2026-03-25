"""
Skill 基类定义（Semantic Kernel 风格）

每个 Skill 是一个独立目录，包含三个文件：
  config.json  ← 机器可读：name, description, input_variables, version, tags
  prompt.md    ← 人类可读：详细说明、Prompt 模板（支持 {{$变量}} 占位符）、示例
  run.py       ← 执行逻辑

BaseSkill 在实例化时自动加载同目录下的 config.json 和 prompt.md：
  - self.config          → SkillConfig (从 config.json 解析)
  - self.spec_text       → prompt.md 完整正文
  - self.sections        → {"Prompt Template": "...", "Examples": "..."}
  - self.prompt_template → sections["Prompt Template"] 的快捷访问
  - self.render_prompt(vars) → 用 {{$key}} 占位符替换生成最终 Prompt
"""

import re
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypeVar, Generic, Dict, Any, Optional, List
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from enum import Enum

from ..core.logger import get_logger

logger = get_logger(__name__)

InputT = TypeVar("InputT", bound=BaseModel)
OutputT = TypeVar("OutputT", bound=BaseModel)


# ============================================================================
# Skill 配置 (从 config.json 解析)
# ============================================================================

@dataclass
class InputVariable:
    """Prompt 模板输入变量声明"""
    name: str
    description: str = ""
    default: str = ""


@dataclass
class SkillConfig:
    """从 config.json 解析出的 Skill 配置"""
    name: str = ""
    description: str = ""
    version: str = "1.0"
    tags: List[str] = field(default_factory=list)
    input_schema: str = ""
    output_schema: str = ""
    input_variables: List[InputVariable] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# 文件加载器
# ============================================================================

def load_config(config_path: Path) -> SkillConfig:
    """加载 config.json → SkillConfig"""
    if not config_path.exists():
        logger.warning(f"config.json 不存在: {config_path}")
        return SkillConfig()

    raw = json.loads(config_path.read_text(encoding="utf-8"))

    input_vars = [
        InputVariable(
            name=v.get("name", ""),
            description=v.get("description", ""),
            default=v.get("default", ""),
        )
        for v in raw.pop("input_variables", [])
    ]

    return SkillConfig(
        name=raw.pop("name", ""),
        description=raw.pop("description", ""),
        version=raw.pop("version", "1.0"),
        tags=raw.pop("tags", []),
        input_schema=raw.pop("input_schema", ""),
        output_schema=raw.pop("output_schema", ""),
        input_variables=input_vars,
        extra=raw,
    )


def load_prompt_md(md_path: Path) -> tuple:
    """
    加载 prompt.md → (spec_text, sections)

    sections 是 {heading: content} 字典，
    按二级标题拆分，可用于提取 "## Prompt Template" 等特定段落。
    """
    if not md_path.exists():
        logger.warning(f"prompt.md 不存在: {md_path}")
        return "", {}

    body = md_path.read_text(encoding="utf-8").strip()

    sections: Dict[str, str] = {}
    current_heading = ""
    current_lines: List[str] = []

    for line in body.splitlines():
        heading_match = re.match(r"^##\s+(.+)", line)
        if heading_match:
            if current_heading:
                sections[current_heading] = "\n".join(current_lines).strip()
            current_heading = heading_match.group(1).strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_heading:
        sections[current_heading] = "\n".join(current_lines).strip()

    return body, sections


# ============================================================================
# 占位符渲染（Semantic Kernel 风格 {{$variable}}）
# ============================================================================

_VAR_PATTERN = re.compile(r"\{\{\$(\w+)\}\}")


def render_template(template: str, variables: Dict[str, str]) -> str:
    """
    将 {{$variable}} 占位符替换为实际值。

    未匹配的占位符保留原样（避免误删）。
    """
    def _replace(match: re.Match) -> str:
        key = match.group(1)
        return variables.get(key, match.group(0))

    return _VAR_PATTERN.sub(_replace, template)


# ============================================================================
# Skill 执行状态 & 结果
# ============================================================================

class SkillStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


class SkillResult(BaseModel, Generic[OutputT]):
    """Skill 执行结果包装器"""
    status: SkillStatus = Field(default=SkillStatus.SUCCESS)
    output: Optional[OutputT] = Field(default=None)
    error: Optional[str] = Field(default=None)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def success(cls, output: OutputT, **metadata) -> "SkillResult[OutputT]":
        return cls(status=SkillStatus.SUCCESS, output=output, metadata=metadata)

    @classmethod
    def failed(cls, error: str, **metadata) -> "SkillResult[OutputT]":
        return cls(status=SkillStatus.FAILED, error=error, metadata=metadata)

    @classmethod
    def partial(cls, output: OutputT, error: str, **metadata) -> "SkillResult[OutputT]":
        return cls(status=SkillStatus.PARTIAL, output=output, error=error, metadata=metadata)

    def is_success(self) -> bool:
        return self.status == SkillStatus.SUCCESS

    def is_failed(self) -> bool:
        return self.status == SkillStatus.FAILED


# ============================================================================
# Skill 抽象基类
# ============================================================================

class BaseSkill(ABC, Generic[InputT, OutputT]):
    """
    Skill 抽象基类（Semantic Kernel 风格）

    实例化时自动加载同目录的 config.json 和 prompt.md：
      - self.config          → SkillConfig
      - self.spec_text       → prompt.md 完整正文
      - self.sections        → {"Prompt Template": "...", ...}
      - self.prompt_template → 快捷访问 "## Prompt Template"
      - self.render_prompt() → {{$var}} 替换
    """

    def __init__(self):
        import importlib
        mod = importlib.import_module(self.__class__.__module__)
        if hasattr(mod, "__file__") and mod.__file__:
            skill_dir = Path(mod.__file__).parent
        else:
            skill_dir = Path(__file__).parent

        self.config = load_config(skill_dir / "config.json")
        self.spec_text, self.sections = load_prompt_md(skill_dir / "prompt.md")

    @property
    def name(self) -> str:
        return self.config.name or self.__class__.__name__

    @property
    def description(self) -> str:
        return self.config.description

    @property
    def prompt_template(self) -> str:
        """快捷访问 ## Prompt Template 段落"""
        return self.sections.get("Prompt Template", "")

    def get_section(self, heading: str) -> str:
        """获取 prompt.md 中指定二级标题的内容"""
        return self.sections.get(heading, "")

    def render_prompt(self, variables: Dict[str, str]) -> str:
        """
        用变量字典渲染 Prompt Template。

        读取 prompt.md 的 "## Prompt Template" 段落，
        将 {{$key}} 替换为 variables[key]。
        """
        template = self.prompt_template
        if not template:
            logger.warning(f"Skill {self.name}: prompt.md 中无 Prompt Template 段落")
            return ""
        return render_template(template, variables)

    @abstractmethod
    def run(self, input: InputT) -> SkillResult[OutputT]:
        pass

    def __call__(self, input: InputT) -> SkillResult[OutputT]:
        logger.info(f"🔧 执行 Skill: {self.name}")
        try:
            result = self.run(input)
            if result.is_success():
                logger.info(f"✅ Skill {self.name} 执行成功")
            elif result.is_failed():
                logger.warning(f"❌ Skill {self.name} 执行失败: {result.error}")
            else:
                logger.info(f"⚠️ Skill {self.name} 部分成功: {result.error}")
            return result
        except Exception as e:
            logger.error(f"❌ Skill {self.name} 异常: {e}")
            return SkillResult.failed(str(e))
