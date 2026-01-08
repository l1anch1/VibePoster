"""
API 路由模块

包含：
- poster.py: 海报生成路由 /api/generate_multimodal
- knowledge.py: 知识模块路由 /api/kg/*, /api/brand/*

Author: VibePoster Team
Date: 2025-01
"""

from .poster import router as poster_router
from .knowledge import router as knowledge_router

__all__ = ["poster_router", "knowledge_router"]
