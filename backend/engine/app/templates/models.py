"""
风格模板数据模型

定义海报风格模板的数据结构
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field


class ColorScheme(BaseModel):
    """配色方案"""

    name: str = Field(..., description="配色方案名称")
    primary: str = Field(..., description="主色调（HEX）")
    secondary: str = Field(..., description="辅助色（HEX）")
    accent: str = Field(..., description="强调色（HEX）")
    background: str = Field(..., description="背景色（HEX）")
    text_primary: str = Field(..., description="主要文字颜色（HEX）")
    text_secondary: str = Field(..., description="次要文字颜色（HEX）")
    description: str = Field(default="", description="配色方案描述")


class FontRecommendation(BaseModel):
    """字体推荐"""

    title_fonts: List[str] = Field(..., description="标题字体列表（优先级从高到低）")
    body_fonts: List[str] = Field(..., description="正文字体列表（优先级从高到低）")
    font_size_range: Dict[str, Dict[str, int]] = Field(
        ...,
        description="字体大小范围，如 {'title': {'min': 48, 'max': 72}, 'subtitle': {'min': 24, 'max': 36}}",
    )
    font_weight: Dict[str, str] = Field(
        ..., description="字体粗细，如 {'title': 'bold', 'body': 'normal'}"
    )


class LayoutRule(BaseModel):
    """布局规则"""

    alignment: str = Field(..., description="对齐方式：center, left, right")
    spacing: Dict[str, Union[int, float]] = Field(
        ..., description="间距设置，如 {'title_to_subtitle': 20, 'text_padding': 30, 'line_height': 1.5}"
    )
    element_distribution: str = Field(
        ..., description="元素分布：balanced（平衡）, top_heavy（上重）, bottom_heavy（下重）"
    )
    text_area_ratio: float = Field(
        ..., ge=0.1, le=0.9, description="文字区域占画布比例（0.1-0.9）"
    )
    image_area_ratio: float = Field(
        ..., ge=0.1, le=0.9, description="图片区域占画布比例（0.1-0.9）"
    )
    preferred_positions: Dict[str, str] = Field(
        ...,
        description="首选位置，如 {'title': 'top', 'image': 'center', 'subtitle': 'bottom'}",
    )


class StylePreference(BaseModel):
    """风格偏好"""

    keywords: List[str] = Field(..., description="风格关键词列表")
    mood: str = Field(..., description="情绪基调：professional, energetic, calm, festive, etc.")
    target_audience: str = Field(..., description="目标受众：business, students, general, etc.")
    design_principles: List[str] = Field(..., description="设计原则列表")
    avoid_elements: List[str] = Field(default_factory=list, description="应避免的元素")
    recommended_elements: List[str] = Field(..., description="推荐的元素")


class StyleTemplate(BaseModel):
    """
    风格模板
    
    包含完整的风格定义，包括配色、字体、布局规则和风格偏好
    """

    id: str = Field(..., description="风格模板唯一标识符")
    name: str = Field(..., description="风格名称")
    display_name: str = Field(..., description="显示名称（中文）")
    description: str = Field(..., description="风格描述")
    
    # 配色方案（多个可选）
    color_schemes: List[ColorScheme] = Field(..., description="配色方案列表")
    
    # 字体推荐
    font_recommendation: FontRecommendation = Field(..., description="字体推荐")
    
    # 布局规则
    layout_rule: LayoutRule = Field(..., description="布局规则")
    
    # 风格偏好
    style_preference: StylePreference = Field(..., description="风格偏好")
    
    # 使用场景
    use_cases: List[str] = Field(..., description="适用场景列表")
    
    # 示例提示词
    example_prompts: List[str] = Field(
        default_factory=list, description="示例提示词（帮助用户理解该风格）"
    )

    def get_default_color_scheme(self) -> ColorScheme:
        """获取默认配色方案（第一个）"""
        return self.color_schemes[0]

    def to_prompt_context(self) -> str:
        """
        转换为 Prompt 上下文
        
        用于注入到 Planner Agent 的 Prompt 中
        """
        color_scheme = self.get_default_color_scheme()
        
        context = f"""
【风格模板：{self.display_name}】
- 风格描述：{self.description}
- 情绪基调：{self.style_preference.mood}
- 目标受众：{self.style_preference.target_audience}

【配色方案：{color_scheme.name}】
- 主色调：{color_scheme.primary}
- 辅助色：{color_scheme.secondary}
- 强调色：{color_scheme.accent}
- 背景色：{color_scheme.background}
- 主要文字：{color_scheme.text_primary}
- 次要文字：{color_scheme.text_secondary}

【字体推荐】
- 标题字体：{', '.join(self.font_recommendation.title_fonts[:3])}
- 正文字体：{', '.join(self.font_recommendation.body_fonts[:3])}

【布局原则】
- 对齐方式：{self.layout_rule.alignment}
- 元素分布：{self.layout_rule.element_distribution}
- 文字区域占比：{self.layout_rule.text_area_ratio * 100:.0f}%
- 图片区域占比：{self.layout_rule.image_area_ratio * 100:.0f}%

【设计原则】
{chr(10).join(f'- {principle}' for principle in self.style_preference.design_principles)}

【推荐元素】
{', '.join(self.style_preference.recommended_elements)}

【应避免元素】
{', '.join(self.style_preference.avoid_elements) if self.style_preference.avoid_elements else '无特别限制'}
"""
        return context.strip()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于 API 响应）"""
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "color_schemes": [scheme.dict() for scheme in self.color_schemes],
            "font_recommendation": self.font_recommendation.dict(),
            "layout_rule": self.layout_rule.dict(),
            "style_preference": self.style_preference.dict(),
            "use_cases": self.use_cases,
            "example_prompts": self.example_prompts,
        }

