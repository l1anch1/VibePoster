"""
Services 模块 - 业务逻辑层

负责处理业务逻辑，不涉及 HTTP 请求/响应

服务类：
- PosterService: 海报生成服务
- KnowledgeService: 知识服务（KG + RAG）
- RendererService: OOP 布局渲染服务（拆分为 renderer/ 子模块）
"""

from .poster_service import PosterService
from .knowledge_service import KnowledgeService
from .renderer import RendererService, create_simple_poster_from_text

__all__ = [
    "PosterService",
    "KnowledgeService", 
    "RendererService",
    "create_simple_poster_from_text"
]
