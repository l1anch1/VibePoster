"""
API 请求模型定义

职责：
1. 定义 API 请求参数验证模型
2. 请求参数校验逻辑

注意：响应模型统一定义在 models/response.py 中

Author: VibePoster Team
Date: 2025-01
"""

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# 请求模型
# ============================================================================

class PosterGenerateRequest(BaseModel):
    """海报生成请求模型（多模态）"""
    
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="用户输入的提示词，描述想要生成的海报内容"
    )
    canvas_width: int = Field(
        ...,
        ge=100,
        le=10000,
        description="画布宽度（像素），范围：100-10000"
    )
    canvas_height: int = Field(
        ...,
        ge=100,
        le=10000,
        description="画布高度（像素），范围：100-10000"
    )
    
    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        """验证提示词"""
        if not v or not v.strip():
            raise ValueError("提示词不能为空")
        return v.strip()
    
    @field_validator("canvas_width", "canvas_height")
    @classmethod
    def validate_canvas_size(cls, v: int) -> int:
        """验证画布尺寸"""
        if v < 100:
            raise ValueError("画布尺寸不能小于 100 像素")
        if v > 10000:
            raise ValueError("画布尺寸不能大于 10000 像素")
        return v
