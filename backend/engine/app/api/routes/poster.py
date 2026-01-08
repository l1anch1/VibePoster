"""
海报生成路由

职责：
1. 处理海报生成请求 /api/generate_multimodal

Author: VibePoster Team
Date: 2025-01
"""

from fastapi import APIRouter, UploadFile, File, Form, Depends
from typing import Optional, Dict, Any
from pydantic import ValidationError

from ...services import PosterService
from ...models.poster import PosterData
from ...core.exceptions import ValidationException, ServiceException
from ...core.dependencies import get_poster_service
from ..schemas import PosterGenerateRequest
from ...models.response import (
    ErrorResponse,
    PosterGenerateResponse,
)

# 创建路由实例
router = APIRouter(prefix="/api", tags=["poster"])


# ============================================================================
# 依赖注入
# ============================================================================

async def validate_multimodal_request(
    prompt: str = Form(...),
    canvas_width: int = Form(...),
    canvas_height: int = Form(...),
    brand_name: Optional[str] = Form(None, description="品牌名称（用于 RAG 检索）"),
) -> Dict[str, Any]:
    """验证多模态请求参数"""
    try:
        request = PosterGenerateRequest(
            prompt=prompt,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
        )
        return {
            "request": request,
            "brand_name": brand_name,
        }
    except ValidationError as e:
        raise ValidationException(
            message="请求参数验证失败",
            detail={"errors": e.errors()}
        )


# ============================================================================
# 海报生成 API
# ============================================================================

@router.post(
    "/generate_multimodal",
    response_model=PosterGenerateResponse,
    responses={
        200: {"description": "海报生成成功", "model": PosterGenerateResponse},
        400: {"description": "请求参数错误", "model": ErrorResponse},
        422: {"description": "请求参数验证失败", "model": ErrorResponse},
        500: {"description": "服务器内部错误", "model": ErrorResponse},
    },
)
async def generate_multimodal(
    validated_data: Dict[str, Any] = Depends(validate_multimodal_request),
    image_person: Optional[UploadFile] = File(None, description="人物图片（可选）"),
    image_bg: Optional[UploadFile] = File(None, description="背景图片（可选）"),
    poster_service: PosterService = Depends(get_poster_service),
) -> PosterGenerateResponse:
    """
    多模态海报生成接口（集成 KG + RAG）
    
    参数说明：
    - **prompt**: 用户输入的提示词（1-1000 字符）
    - **canvas_width**: 画布宽度（像素，100-10000）
    - **canvas_height**: 画布高度（像素，100-10000）
    - **image_person**: 人物图片（可选）
    - **image_bg**: 背景图片（可选）
    - **brand_name**: 品牌名称（可选，用于 RAG 检索）
    """
    request = validated_data["request"]
    brand_name = validated_data.get("brand_name")
    
    try:
        image_person_bytes = None
        image_bg_bytes = None
        
        if image_person:
            image_person_bytes = await image_person.read()
        
        if image_bg:
            image_bg_bytes = await image_bg.read()
        
        poster_data_dict = poster_service.generate_poster(
            prompt=request.prompt,
            canvas_width=request.canvas_width,
            canvas_height=request.canvas_height,
            image_person=image_person_bytes,
            image_bg=image_bg_bytes,
            chat_history=None,
            brand_name=brand_name,
        )
        
        poster_data = PosterData(**poster_data_dict)
        
        return PosterGenerateResponse(
            success=True,
            data=poster_data,
            message="海报生成成功"
        )
    
    except ValueError as e:
        raise ValidationException(
            message="请求参数错误",
            detail={"detail": str(e)}
        )
    except Exception as e:
        raise ServiceException(
            message="海报生成失败",
            detail={"detail": str(e)}
        )
