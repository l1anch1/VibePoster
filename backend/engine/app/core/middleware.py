"""
全局中间件
包括异常处理中间件等
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .exceptions import VibePosterException
from .logger import get_logger
from ..api.schemas import ErrorResponse

logger = get_logger(__name__)


async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    全局异常处理中间件
    
    捕获所有未处理的异常，返回统一的错误响应格式
    
    Args:
        request: FastAPI 请求对象
        exc: 异常对象
        
    Returns:
        JSONResponse: 统一的错误响应
    """
    # 记录异常信息
    logger.error(
        f"未处理的异常: {type(exc).__name__}: {exc}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
        }
    )
    
    # 返回统一的错误响应
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="服务器内部错误",
            detail={
                "type": type(exc).__name__,
                "message": str(exc),
            }
        ).model_dump()
    )


async def vibe_poster_exception_handler(request: Request, exc: VibePosterException) -> JSONResponse:
    """
    自定义异常处理
    
    处理 VibePosterException 及其子类
    
    Args:
        request: FastAPI 请求对象
        exc: VibePosterException 异常对象
        
    Returns:
        JSONResponse: 统一的错误响应
    """
    # 记录异常信息（不记录堆栈，因为这是预期的业务异常）
    logger.warning(
        f"业务异常: {type(exc).__name__}: {exc.message}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
            "detail": exc.detail,
        }
    )
    
    # 返回统一的错误响应
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.message,
            detail=exc.detail
        ).model_dump()
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    HTTP 异常处理
    
    处理 FastAPI 的 HTTPException
    
    Args:
        request: FastAPI 请求对象
        exc: StarletteHTTPException 异常对象
        
    Returns:
        JSONResponse: 统一的错误响应
    """
    # 记录异常信息
    logger.warning(
        f"HTTP 异常: {exc.status_code} - {exc.detail}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
        }
    )
    
    # 处理 detail 可能是字符串或字典的情况
    if isinstance(exc.detail, dict):
        error_message = exc.detail.get("error", "请求错误")
        detail = exc.detail
    else:
        error_message = str(exc.detail) if exc.detail else "请求错误"
        detail = {"message": error_message}
    
    # 返回统一的错误响应
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=error_message,
            detail=detail
        ).model_dump()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    请求验证异常处理
    
    处理 Pydantic 验证错误
    
    Args:
        request: FastAPI 请求对象
        exc: RequestValidationError 异常对象
        
    Returns:
        JSONResponse: 统一的错误响应
    """
    # 记录验证错误
    logger.warning(
        f"请求验证失败: {exc.errors()}",
        extra={
            "path": request.url.path,
            "method": request.method,
        }
    )
    
    # 返回统一的错误响应
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="请求参数验证失败",
            detail={
                "errors": exc.errors()
            }
        ).model_dump()
    )

