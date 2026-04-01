"""
设计简报与素材列表的类型定义

在路由、Agent、Service 之间传递数据时使用这些类型化模型，
替代原来的 Dict[str, Any]，提供端到端的类型安全。
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class DesignBrief(BaseModel):
    """设计简报 — 贯穿整个生成流水线的核心数据结构"""

    model_config = ConfigDict(extra="allow")

    title: str = ""
    subtitle: str = ""
    main_color: str = "#000000"
    background_color: str = "#FFFFFF"
    style_keywords: List[str] = Field(default_factory=list)
    intent: str = "promotion"
    industry: Optional[str] = None
    vibe: Optional[str] = None

    # 由 step 路由注入
    user_prompt: Optional[str] = None
    canvas_width: Optional[int] = None
    canvas_height: Optional[int] = None

    # 参考图分析字段（由 step_assets 注入）
    reference_palette: Optional[List[str]] = None
    reference_mood: Optional[str] = None
    reference_theme: Optional[str] = None
    reference_description: Optional[str] = None
    reference_layout_hints: Optional[Dict[str, Any]] = None
    reference_color_scheme: Optional[Dict[str, Any]] = None

    # 知识模块字段
    decision_trace: Optional[Dict[str, Any]] = None
    kg_rules: Optional[Dict[str, Any]] = None
    brand_knowledge: Optional[List[Dict[str, Any]]] = None
    design_source: Optional[Dict[str, Any]] = None


class AssetLayer(BaseModel):
    """素材图层信息"""

    model_config = ConfigDict(extra="allow")

    type: str = "image"
    src: str = ""
    source_type: str = "selected"
    width: Optional[int] = None
    height: Optional[int] = None


class AssetList(BaseModel):
    """素材列表 — Layout Agent 的输入"""

    model_config = ConfigDict(extra="allow")

    background_layer: AssetLayer
    subject_layer: Optional[AssetLayer] = None
    image_analyses: Optional[List[Dict[str, Any]]] = None
    color_suggestions: Optional[Dict[str, Any]] = None
