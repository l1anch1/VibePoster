"""
海报生成相关路由
"""
from fastapi import APIRouter, UploadFile, File, Form, Depends, status, HTTPException
from typing import Optional, Dict, Any
from pydantic import ValidationError

from ...services import PosterService
from ...core.schemas import PosterData
from ...core.exceptions import ValidationException, ServiceException
from ...core.dependencies import get_poster_service
from ...core.logger import logger
from ...templates.manager import template_manager
from ..schemas import (
    PosterGenerateResponse,
    ErrorResponse,
    PosterGenerateRequest,
)

# 创建路由实例
router = APIRouter(prefix="/api", tags=["poster"])


# 注意：get_poster_service 已从 core.dependencies 导入
# 使用单例模式，确保整个应用只有一个服务实例


# 依赖注入：验证多模态请求参数
async def validate_multimodal_request(
    prompt: str = Form(...),
    canvas_width: int = Form(...),
    canvas_height: int = Form(...),
    style_template: Optional[str] = Form(None),
) -> PosterGenerateRequest:
    """
    验证多模态请求参数
    
    将 Form 参数转换为 Pydantic 模型进行验证
    """
    try:
        return PosterGenerateRequest(
            prompt=prompt,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            style_template=style_template,
        )
    except ValidationError as e:
        # 使用自定义异常，由全局异常处理器统一处理
        raise ValidationException(
            message="请求参数验证失败",
            detail={"errors": e.errors()}
        )


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
    request: PosterGenerateRequest = Depends(validate_multimodal_request),
    image_person: Optional[UploadFile] = File(None, description="人物图片（可选）"),
    image_bg: Optional[UploadFile] = File(None, description="背景图片（可选）"),
    poster_service: PosterService = Depends(get_poster_service),
) -> PosterGenerateResponse:
    """
    多模态海报生成接口
    
    支持文字、图片输入，生成个性化海报。
    
    - **prompt**: 用户输入的提示词，描述想要生成的海报内容（1-1000 字符）
    - **canvas_width**: 画布宽度（像素），范围：100-10000
    - **canvas_height**: 画布高度（像素），范围：100-10000
    - **image_person**: 人物图片（可选），用于抠图并合成到海报中
    - **image_bg**: 背景图片（可选），用作海报背景
    
    Returns:
        PosterGenerateResponse: 包含生成的海报数据
    """
    try:
        # 读取图片二进制数据
        image_person_bytes = None
        image_bg_bytes = None
        
        if image_person:
            image_person_bytes = await image_person.read()
        
        if image_bg:
            image_bg_bytes = await image_bg.read()
        
        # 调用服务层处理业务逻辑
        poster_data_dict = poster_service.generate_poster(
            prompt=request.prompt,
            canvas_width=request.canvas_width,
            canvas_height=request.canvas_height,
            image_person=image_person_bytes,
            image_bg=image_bg_bytes,
            chat_history=None,  # 暂时不支持多轮对话
            style_template=request.style_template,  # 传递风格模板 ID
        )
        
        # 将字典转换为 Pydantic 模型
        poster_data = PosterData(**poster_data_dict)
        
        return PosterGenerateResponse(
            success=True,
            data=poster_data,
            message="海报生成成功"
        )
    
    except ValueError as e:
        # 使用自定义异常，由全局异常处理器统一处理
        raise ValidationException(
            message="请求参数错误",
            detail={"detail": str(e)}
        )
    except Exception as e:
        # 使用自定义异常，由全局异常处理器统一处理
        raise ServiceException(
            message="海报生成失败",
            detail={"detail": str(e)}
        )


@router.get("/styles", summary="获取所有风格模板")
async def get_style_templates() -> Dict[str, Any]:
    """
    获取所有可用的风格模板列表
    
    Returns:
        包含所有风格模板信息的字典
    """
    try:
        templates = template_manager.list_templates()
        logger.info(f"返回 {len(templates)} 个风格模板")
        return {
            "success": True,
            "data": {
                "templates": templates,
                "default_template_id": template_manager.default_template_id,
            },
            "message": "风格模板列表获取成功",
        }
    except Exception as e:
        logger.error(f"获取风格模板列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取风格模板列表失败: {str(e)}")


@router.get("/styles/{template_id}", summary="获取指定风格模板详情")
async def get_style_template_detail(template_id: str) -> Dict[str, Any]:
    """
    获取指定风格模板的详细信息
    
    Args:
        template_id: 模板 ID（business, campus, event, product, festival）
        
    Returns:
        风格模板详细信息
    """
    try:
        template = template_manager.get_template(template_id)
        if not template:
            raise HTTPException(
                status_code=404, detail=f"风格模板 '{template_id}' 不存在"
            )

        logger.info(f"返回风格模板详情: {template_id}")
        return {
            "success": True,
            "data": template.to_dict(),
            "message": "风格模板详情获取成功",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取风格模板详情失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取风格模板详情失败: {str(e)}")

