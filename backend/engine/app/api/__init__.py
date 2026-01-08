"""
API 模块 - 路由层

包含：
- routes/: API 路由定义
- schemas.py: API 请求模型
- middleware.py: 全局中间件（异常处理等）
"""
from .routes import poster_router
from .middleware import (
    exception_handler,
    vibe_poster_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)

__all__ = [
    "poster_router",
    "exception_handler",
    "vibe_poster_exception_handler",
    "http_exception_handler",
    "validation_exception_handler",
]
