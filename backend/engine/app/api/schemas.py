"""
API 请求/响应模型定义
用于 API 接口的请求/响应验证和文档生成
"""
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field, field_validator

from ..core.schemas import PosterData


class PosterGenerateResponse(BaseModel):
    """海报生成成功响应"""
    
    success: bool = Field(default=True, description="请求是否成功")
    data: PosterData = Field(..., description="生成的海报数据")
    message: str = Field(default="海报生成成功", description="响应消息")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    
    success: bool = Field(default=False, description="请求是否成功")
    error: str = Field(..., description="错误信息")
    detail: Optional[Dict[str, Any]] = Field(default=None, description="错误详情")


class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    
    status: str = Field(default="healthy", description="服务状态")
    version: str = Field(default="1.0.0", description="API 版本")


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
    style_template: Optional[str] = Field(
        default=None,
        description="风格模板 ID（可选）：business, campus, event, product, festival。不指定则自动匹配"
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
    
    @field_validator("style_template")
    @classmethod
    def validate_style_template(cls, v: Optional[str]) -> Optional[str]:
        """验证风格模板 ID"""
        if v is not None:
            # 'auto' 表示自动选择，转换为 None
            if v == "auto":
                return None
            
            valid_templates = ["business", "campus", "event", "product", "festival"]
            if v not in valid_templates:
                raise ValueError(
                    f"无效的风格模板 ID: {v}。有效值: {', '.join(valid_templates + ['auto'])}"
                )
        return v



