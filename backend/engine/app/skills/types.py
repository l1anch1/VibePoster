"""
Skills 类型定义

定义所有 Skill 的输入输出 Schema。
使用 Pydantic BaseModel 确保类型安全和数据验证。

Author: VibePoster Team
Date: 2025-01
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field


# ============================================================================
# 枚举定义
# ============================================================================

class PosterType(str, Enum):
    """海报类型枚举"""
    PROMOTION = "promotion"        # 促销/宣传
    INVITATION = "invitation"      # 邀请函
    ANNOUNCEMENT = "announcement"  # 公告/通知
    COVER = "cover"                # 封面
    EVENT = "event"                # 活动
    OTHER = "other"                # 其他


class Industry(str, Enum):
    """行业枚举（与 KG v3 本体对齐）"""
    TECH = "Tech"
    FOOD = "Food"
    LUXURY = "Luxury"
    HEALTHCARE = "Healthcare"
    EDUCATION = "Education"
    ENTERTAINMENT = "Entertainment"
    FINANCE = "Finance"
    BEAUTY = "Beauty"


class Vibe(str, Enum):
    """风格枚举（与 KG v3 本体对齐）"""
    MINIMALIST = "Minimalist"
    ENERGETIC = "Energetic"
    PROFESSIONAL = "Professional"
    FRIENDLY = "Friendly"
    BOLD = "Bold"
    RETRO = "Retro"
    FUTURISTIC = "Futuristic"


# ============================================================================
# IntentParseSkill 类型
# ============================================================================

class IntentParseInput(BaseModel):
    """意图解析输入"""
    user_prompt: str = Field(..., description="用户输入的原始提示词")
    chat_history: Optional[List[Dict[str, str]]] = Field(
        default=None, 
        description="对话历史（可选）"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_prompt": "帮我做一个苹果发布会的科技风海报",
                "chat_history": None
            }
        }


class IntentParseOutput(BaseModel):
    """意图解析输出"""
    industry: Optional[str] = Field(
        default=None, 
        description="识别到的行业（Tech, Food, Luxury 等）"
    )
    vibe: Optional[str] = Field(
        default=None, 
        description="识别到的风格（Minimalist, Energetic 等）"
    )
    poster_type: str = Field(
        default="promotion", 
        description="海报类型（promotion, invitation, announcement, cover, event, other）"
    )
    brand_name: Optional[str] = Field(
        default=None, 
        description="识别到的品牌名称"
    )
    key_elements: List[str] = Field(
        default_factory=list, 
        description="用户提到的关键元素"
    )
    extracted_keywords: List[str] = Field(
        default_factory=list, 
        description="提取到的 KG 关键词"
    )
    confidence: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="解析置信度"
    )
    negative_constraints: List[str] = Field(
        default_factory=list,
        description="用户否定约束对应的 KG 节点名（如 Grid, Multi-color）"
    )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.model_dump()
    
    class Config:
        json_schema_extra = {
            "example": {
                "industry": "Tech",
                "vibe": "Minimalist",
                "poster_type": "promotion",
                "brand_name": "Apple",
                "key_elements": ["发布会", "新品"],
                "extracted_keywords": ["Tech", "Minimalist"],
                "confidence": 0.9
            }
        }


# ============================================================================
# DesignRuleSkill 类型
# ============================================================================

class DesignRuleInput(BaseModel):
    """设计规则推理输入"""
    industry: Optional[str] = Field(
        default=None, 
        description="行业关键词"
    )
    vibe: Optional[str] = Field(
        default=None, 
        description="风格关键词"
    )
    additional_keywords: List[str] = Field(
        default_factory=list,
        description="额外的关键词"
    )
    image_analyses: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="参考图 VLM 分析结果（用于视觉意图逆向映射）"
    )
    negative_constraints: List[str] = Field(
        default_factory=list,
        description="用户否定约束对应的 KG 节点名"
    )

    def get_all_keywords(self) -> List[str]:
        """获取所有非空关键词"""
        keywords = []
        if self.industry:
            keywords.append(self.industry)
        if self.vibe:
            keywords.append(self.vibe)
        keywords.extend(self.additional_keywords)
        return keywords
    
    class Config:
        json_schema_extra = {
            "example": {
                "industry": "Tech",
                "vibe": "Minimalist",
                "additional_keywords": []
            }
        }


class DesignRuleOutput(BaseModel):
    """设计规则推理输出（与 KG InferenceResult 对齐）"""
    # 情绪层
    emotions: List[str] = Field(
        default_factory=list, 
        description="推理出的情绪基调"
    )
    
    # 颜色层
    color_strategies: List[str] = Field(
        default_factory=list, 
        description="推荐的配色策略"
    )
    color_palettes: Dict[str, List[str]] = Field(
        default_factory=dict, 
        description="推荐的配色方案 {primary: [...], accent: [...]}"
    )
    
    # 排版层
    typography_styles: List[str] = Field(
        default_factory=list, 
        description="推荐的字体风格"
    )
    typography_weights: List[str] = Field(
        default_factory=list, 
        description="推荐的字重"
    )
    typography_characteristics: List[str] = Field(
        default_factory=list, 
        description="排版特征"
    )
    
    # 布局层
    layout_strategies: List[str] = Field(
        default_factory=list, 
        description="布局策略"
    )
    layout_intents: List[str] = Field(
        default_factory=list, 
        description="布局意图"
    )
    layout_patterns: List[str] = Field(
        default_factory=list,
        description="布局模式"
    )

    # 装饰层
    decoration_styles: Dict[str, Any] = Field(
        default_factory=dict,
        description="装饰风格推荐 {divider: {...}, overlay: {...}, shape: {...}}"
    )

    # 推理链路追踪（XAI）
    inference_traces: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="KG 推理链路 [{path, relation_chain, weight}]"
    )

    # 设计原则
    design_principles: List[str] = Field(
        default_factory=list, 
        description="设计原则"
    )
    avoid: List[str] = Field(
        default_factory=list, 
        description="应避免的元素"
    )
    
    # 元信息
    source_keywords: List[str] = Field(
        default_factory=list, 
        description="用于推理的关键词"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.model_dump()
    
    def get_primary_color(self) -> Optional[str]:
        """获取主色调"""
        primary_colors = self.color_palettes.get("primary", [])
        return primary_colors[0] if primary_colors else None
    
    def is_empty(self) -> bool:
        """检查是否为空结果"""
        return len(self.emotions) == 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "emotions": ["Trust", "Innovation"],
                "color_strategies": ["Monochromatic", "Triadic"],
                "color_palettes": {
                    "primary": ["#0066CC", "#6366F1"],
                    "accent": ["#48BB78", "#22D3EE"]
                },
                "typography_styles": ["Sans-Serif"],
                "typography_weights": ["Medium", "Bold"],
                "typography_characteristics": ["Clean", "Modern"],
                "layout_strategies": ["Structured", "Dynamic"],
                "layout_intents": ["Stability", "Forward-thinking"],
                "layout_patterns": ["Grid", "Diagonal"],
                "design_principles": ["Clean interfaces", "Scalable design system"],
                "avoid": ["Warm earth tones", "Script fonts"],
                "source_keywords": ["Tech", "Minimalist"]
            }
        }


# ============================================================================
# BrandContextSkill 类型
# ============================================================================

class BrandContextInput(BaseModel):
    """品牌上下文输入"""
    brand_name: str = Field(..., description="品牌名称")
    aspects: List[str] = Field(
        default_factory=lambda: ["color", "style", "guideline"],
        description="检索的方面"
    )


class BrandContextOutput(BaseModel):
    """品牌上下文输出"""
    brand_name: str = Field(..., description="品牌名称")
    brand_colors: Dict[str, str] = Field(
        default_factory=dict, 
        description="品牌色 {primary: '#xxx', secondary: '#xxx'}"
    )
    brand_style: Optional[str] = Field(
        default=None, 
        description="品牌风格描述"
    )
    guidelines: List[str] = Field(
        default_factory=list, 
        description="设计规范"
    )
    source_documents: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="RAG 检索到的原文（可追溯）"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.model_dump()


# ============================================================================
# DesignBriefSkill 类型
# ============================================================================

class DesignBriefInput(BaseModel):
    """设计简报生成输入"""
    user_prompt: str = Field(..., description="用户原始输入")
    intent: IntentParseOutput = Field(..., description="意图解析结果")
    design_rules: DesignRuleOutput = Field(..., description="设计规则")
    brand_context: Optional[BrandContextOutput] = Field(
        default=None, 
        description="品牌上下文（可选）"
    )


class DesignBriefOutput(BaseModel):
    """设计简报输出"""
    title: str = Field(..., description="海报主标题")
    subtitle: str = Field(default="", description="副标题")
    main_color: str = Field(..., description="主色调 Hex 值")
    background_color: str = Field(default="#FFFFFF", description="背景色 Hex 值")
    style_keywords: List[str] = Field(
        default_factory=list, 
        description="背景图搜索关键词（英文）"
    )
    intent: str = Field(default="promotion", description="海报意图类型")
    industry: Optional[str] = Field(default=None, description="行业（来自意图解析）")
    vibe: Optional[str] = Field(default=None, description="风格（来自意图解析）")
    
    # 决策追溯
    decision_trace: Dict[str, Any] = Field(
        default_factory=dict, 
        description="决策来源追溯"
    )
    
    # 知识模块上下文
    kg_rules: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="KG 推理规则"
    )
    brand_knowledge: Optional[List[Dict[str, Any]]] = Field(
        default=None, 
        description="品牌知识"
    )
    design_source: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="设计来源标记"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.model_dump()
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "创新科技 引领未来",
                "subtitle": "2025 新品发布会",
                "main_color": "#0066CC",
                "background_color": "#F5F5F5",
                "style_keywords": ["tech", "minimal", "gradient"],
                "intent": "promotion",
                "decision_trace": {
                    "main_color_source": "kg_inference",
                    "style_source": "intent_parse"
                }
            }
        }
