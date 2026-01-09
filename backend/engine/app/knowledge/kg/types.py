"""
KG 类型定义 v2

支持语义化推理链：Industry → Emotion → Visual Elements

Author: VibePoster Team
Date: 2025-01
"""

from typing import List, Dict, Any, Optional, Set
from enum import Enum
from pydantic import BaseModel, Field


class NodeType(str, Enum):
    """节点类型枚举"""
    INDUSTRY = "industry"
    VIBE = "vibe"
    EMOTION = "emotion"
    COLOR_STRATEGY = "color_strategy"
    LAYOUT_INTENT = "layout_intent"


class EdgeType(str, Enum):
    """边类型枚举"""
    EMBODIES = "embodies"           # Industry/Vibe → Emotion
    USES_STRATEGY = "uses_strategy" # Emotion → ColorStrategy
    HAS_INTENT = "has_intent"       # Emotion → LayoutIntent


# ============================================================================
# 设计元素模型
# ============================================================================

class ColorPalette(BaseModel):
    """配色方案"""
    primary: List[str] = Field(default_factory=list, description="主色调")
    accent: List[str] = Field(default_factory=list, description="强调色")
    gradient: List[str] = Field(default_factory=list, description="渐变色")
    metallic: List[str] = Field(default_factory=list, description="金属色")
    natural: List[str] = Field(default_factory=list, description="自然色")
    fresh: List[str] = Field(default_factory=list, description="清新色")
    pop: List[str] = Field(default_factory=list, description="流行色")
    
    def all_colors(self) -> List[str]:
        """获取所有颜色"""
        colors = []
        for field in ['primary', 'accent', 'gradient', 'metallic', 'natural', 'fresh', 'pop']:
            colors.extend(getattr(self, field, []))
        return colors


class Typography(BaseModel):
    """排版风格"""
    style: str = Field(..., description="字体风格")
    weight: str = Field(..., description="字重")
    characteristics: List[str] = Field(default_factory=list, description="特征")


class LayoutStyle(BaseModel):
    """布局风格"""
    strategy: str = Field(..., description="布局策略")
    intent: str = Field(..., description="布局意图")
    patterns: List[str] = Field(default_factory=list, description="布局模式")


class EmotionDefinition(BaseModel):
    """情绪定义"""
    description: str = Field(..., description="情绪描述")
    color_strategies: List[str] = Field(default_factory=list, description="配色策略")
    color_palettes: ColorPalette = Field(default_factory=ColorPalette, description="配色方案")
    typography: Typography = Field(default=None, description="排版风格")
    layout: LayoutStyle = Field(default=None, description="布局风格")


class IndustryDefinition(BaseModel):
    """行业定义"""
    description: str = Field(..., description="行业描述")
    embodies: List[str] = Field(default_factory=list, description="体现的情绪")
    design_principles: List[str] = Field(default_factory=list, description="设计原则")
    avoid: List[str] = Field(default_factory=list, description="应避免的元素")


class VibeDefinition(BaseModel):
    """风格定义"""
    description: str = Field(..., description="风格描述")
    embodies: List[str] = Field(default_factory=list, description="体现的情绪")
    modifiers: Dict[str, Any] = Field(default_factory=dict, description="修饰参数")


# ============================================================================
# 推理结果模型
# ============================================================================

class InferenceResult(BaseModel):
    """推理结果 v2"""
    # 情绪层
    emotions: List[str] = Field(default_factory=list, description="识别到的情绪")
    
    # 颜色层
    color_strategies: List[str] = Field(default_factory=list, description="推荐的配色策略")
    color_palettes: Dict[str, List[str]] = Field(default_factory=dict, description="推荐的配色方案")
    
    # 排版层
    typography_styles: List[str] = Field(default_factory=list, description="推荐的字体风格")
    typography_weights: List[str] = Field(default_factory=list, description="推荐的字重")
    typography_characteristics: List[str] = Field(default_factory=list, description="排版特征")
    
    # 布局层
    layout_strategies: List[str] = Field(default_factory=list, description="布局策略")
    layout_intents: List[str] = Field(default_factory=list, description="布局意图")
    layout_patterns: List[str] = Field(default_factory=list, description="布局模式")
    
    # 设计原则
    design_principles: List[str] = Field(default_factory=list, description="设计原则")
    avoid: List[str] = Field(default_factory=list, description="应避免的元素")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.model_dump()
    
    def merge(self, other: 'InferenceResult') -> 'InferenceResult':
        """合并两个推理结果"""
        merged_palettes = dict(self.color_palettes)
        for key, colors in other.color_palettes.items():
            if key in merged_palettes:
                merged_palettes[key] = list(set(merged_palettes[key] + colors))
            else:
                merged_palettes[key] = colors
        
        return InferenceResult(
            emotions=list(set(self.emotions + other.emotions)),
            color_strategies=list(set(self.color_strategies + other.color_strategies)),
            color_palettes=merged_palettes,
            typography_styles=list(set(self.typography_styles + other.typography_styles)),
            typography_weights=list(set(self.typography_weights + other.typography_weights)),
            typography_characteristics=list(set(self.typography_characteristics + other.typography_characteristics)),
            layout_strategies=list(set(self.layout_strategies + other.layout_strategies)),
            layout_intents=list(set(self.layout_intents + other.layout_intents)),
            layout_patterns=list(set(self.layout_patterns + other.layout_patterns)),
            design_principles=list(set(self.design_principles + other.design_principles)),
            avoid=list(set(self.avoid + other.avoid))
        )


class GraphStats(BaseModel):
    """图谱统计信息"""
    node_count: int = Field(..., description="节点数量")
    edge_count: int = Field(..., description="边数量")
    rules_file: str = Field(..., description="规则文件路径")
    version: str = Field(default="2.0.0", description="数据版本")
    industries: List[str] = Field(default_factory=list, description="支持的行业")
    vibes: List[str] = Field(default_factory=list, description="支持的风格")
    emotions: List[str] = Field(default_factory=list, description="支持的情绪")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.model_dump()
