"""
KG 类型定义 v3 — 五层设计知识本体

本体层次:
    Layer 0: Domain Entry    — Industry / Vibe（应用场景入口）
    Layer 1: Emotion         — 语义中枢（9 种情绪）
    Layer 2: Visual Strategy — ColorStrategy / TypographyStyle / LayoutPattern / DecorationTheme
    Layer 3: Concrete Value  — 色值、字体参数等（承载在 EVOKES 边属性或策略节点属性中）

语义关系:
    EMBODIES        Entry → Emotion          行业/风格体现某种情绪
    EVOKES          Emotion → Strategy       情绪唤起某种视觉策略
    AVOIDS          Entry → Strategy         领域禁忌约束
    CONFLICTS_WITH  Strategy ↔ Strategy      策略间互斥
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field


# ============================================================================
# 节点类型 & 边类型枚举
# ============================================================================

class NodeType(str, Enum):
    """本体节点类型"""
    INDUSTRY = "industry"
    VIBE = "vibe"
    EMOTION = "emotion"
    COLOR_STRATEGY = "color_strategy"
    TYPOGRAPHY_STYLE = "typography_style"
    LAYOUT_PATTERN = "layout_pattern"
    DECORATION_THEME = "decoration_theme"


class EdgeType(str, Enum):
    """本体语义关系类型"""
    EMBODIES = "embodies"
    EVOKES = "evokes"
    AVOIDS = "avoids"
    CONFLICTS_WITH = "conflicts_with"


# ============================================================================
# Layer 0 — Domain Entry 节点
# ============================================================================

class IndustryDefinition(BaseModel):
    """行业定义"""
    description: str = Field(..., description="行业描述")
    design_principles: List[str] = Field(default_factory=list)
    avoid: List[str] = Field(default_factory=list)


class VibeDefinition(BaseModel):
    """风格定义"""
    description: str = Field(..., description="风格描述")
    modifiers: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# Layer 1 — Emotion 节点
# ============================================================================

class EmotionDefinition(BaseModel):
    """情绪定义（语义中枢节点）"""
    description: str = Field(..., description="情绪描述")
    palettes: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="该情绪的调色板 {primary: [...], accent: [...], ...}",
    )


# ============================================================================
# Layer 2 — Visual Strategy 节点
# ============================================================================

class ColorStrategyDefinition(BaseModel):
    """配色策略定义"""
    description: str = Field(..., description="策略描述")
    method: str = Field(default="", description="配色方法论")
    effect: str = Field(default="", description="视觉效果")


class TypographyStyleDefinition(BaseModel):
    """排版风格定义"""
    description: str = Field(..., description="字体风格描述")
    family_hints: List[str] = Field(default_factory=list, description="推荐字体族")


class LayoutPatternDefinition(BaseModel):
    """布局模式定义"""
    description: str = Field(..., description="布局模式描述")
    strategy: str = Field(..., description="布局策略标签")
    intent: str = Field(..., description="布局意图标签")
    patterns: List[str] = Field(default_factory=list, description="产出的模式名列表")
    effect: str = Field(default="", description="视觉效果")


class DecorationThemeDefinition(BaseModel):
    """装饰主题定义"""
    description: str = Field(..., description="装饰主题描述")
    divider: Dict[str, Any] = Field(default_factory=dict)
    overlay: Dict[str, Any] = Field(default_factory=dict)
    shape: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# 关系模型
# ============================================================================

class Relation(BaseModel):
    """语义三元组"""
    source: str = Field(..., description="源节点 ID")
    target: str = Field(..., description="目标节点 ID")
    type: str = Field(..., description="关系类型")
    weight: float = Field(default=1.0, ge=0.0, le=1.0, description="关系权重")
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="边上下文（如 EVOKES typography 的 weight/characteristics）",
    )


# ============================================================================
# 推理结果模型（与 v2 输出格式完全兼容）
# ============================================================================

class InferenceTrace(BaseModel):
    """单条推理链路追踪"""
    path: List[str] = Field(..., description="推理路径 [entry, emotion, strategy]")
    relation_chain: List[str] = Field(..., description="关系链 [EMBODIES, EVOKES]")
    weight: float = Field(..., description="路径累积权重（乘积）")


class InferenceResult(BaseModel):
    """推理结果 v3 — 输出格式与 v2 完全兼容"""
    # 情绪层
    emotions: List[str] = Field(default_factory=list)

    # 颜色层
    color_strategies: List[str] = Field(default_factory=list)
    color_palettes: Dict[str, List[str]] = Field(default_factory=dict)

    # 排版层
    typography_styles: List[str] = Field(default_factory=list)
    typography_weights: List[str] = Field(default_factory=list)
    typography_characteristics: List[str] = Field(default_factory=list)

    # 布局层
    layout_strategies: List[str] = Field(default_factory=list)
    layout_intents: List[str] = Field(default_factory=list)
    layout_patterns: List[str] = Field(default_factory=list)

    # 装饰层
    decoration_styles: Dict[str, Any] = Field(default_factory=dict)

    # 设计原则
    design_principles: List[str] = Field(default_factory=list)
    avoid: List[str] = Field(default_factory=list)

    # v3 新增：推理链追踪
    inference_traces: List[InferenceTrace] = Field(
        default_factory=list,
        description="完整推理链路（可选，用于可解释性）",
    )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（兼容 v2 消费方）"""
        d = self.model_dump()
        d.pop("inference_traces", None)
        return d

    def merge(self, other: "InferenceResult") -> "InferenceResult":
        """合并两个推理结果"""
        merged_palettes = dict(self.color_palettes)
        for key, colors in other.color_palettes.items():
            if key in merged_palettes:
                merged_palettes[key] = list(set(merged_palettes[key] + colors))
            else:
                merged_palettes[key] = colors

        merged_decorations = dict(self.decoration_styles)
        for key, val in other.decoration_styles.items():
            if key not in merged_decorations:
                merged_decorations[key] = val

        return InferenceResult(
            emotions=list(set(self.emotions + other.emotions)),
            color_strategies=list(set(self.color_strategies + other.color_strategies)),
            color_palettes=merged_palettes,
            typography_styles=list(set(self.typography_styles + other.typography_styles)),
            typography_weights=list(set(self.typography_weights + other.typography_weights)),
            typography_characteristics=list(set(
                self.typography_characteristics + other.typography_characteristics
            )),
            layout_strategies=list(set(self.layout_strategies + other.layout_strategies)),
            layout_intents=list(set(self.layout_intents + other.layout_intents)),
            layout_patterns=list(set(self.layout_patterns + other.layout_patterns)),
            decoration_styles=merged_decorations,
            design_principles=list(set(self.design_principles + other.design_principles)),
            avoid=list(set(self.avoid + other.avoid)),
            inference_traces=self.inference_traces + other.inference_traces,
        )


class GraphStats(BaseModel):
    """图谱统计信息"""
    node_count: int = Field(..., description="节点数量")
    edge_count: int = Field(..., description="边数量")
    rules_file: str = Field(..., description="本体数据文件路径")
    version: str = Field(default="3.0.0")
    industries: List[str] = Field(default_factory=list)
    vibes: List[str] = Field(default_factory=list)
    emotions: List[str] = Field(default_factory=list)
    node_type_counts: Dict[str, int] = Field(default_factory=dict)
    edge_type_counts: Dict[str, int] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
