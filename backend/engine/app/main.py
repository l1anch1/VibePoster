"""
FastAPI 入口 - 应用初始化 - 应用配置和路由注册
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# 引入路由和配置
from .api.routes import poster_router, knowledge_router
from .core.config import settings
from .core.exceptions import VibePosterException
from .api.middleware import (
    vibe_poster_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    exception_handler,
)

# 创建 FastAPI 应用实例
app = FastAPI(
    title="VibePoster API",
    description="AI 驱动的海报生成系统",
    version="1.0.0",
)

# 配置跨域（从配置文件读取，更安全）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allow_origins_list,
    allow_methods=settings.cors.allow_methods_list,
    allow_headers=settings.cors.allow_headers_list,
    allow_credentials=settings.cors.ALLOW_CREDENTIALS,
)

# 注册全局异常处理器（按优先级从高到低）
# 1. 自定义业务异常（优先级最高）
app.add_exception_handler(VibePosterException, vibe_poster_exception_handler)

# 2. HTTP 异常（FastAPI 的 HTTPException）
app.add_exception_handler(StarletteHTTPException, http_exception_handler)

# 3. 请求验证异常（Pydantic 验证错误）
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# 4. 通用异常（兜底，捕获所有未处理的异常）
app.add_exception_handler(Exception, exception_handler)

# 注册路由
app.include_router(poster_router)
app.include_router(knowledge_router)
