"""
Core 模块 - 系统基础设施

职责：
1. 配置管理 (config.py)
2. 依赖注入 (dependencies.py)
3. 日志系统 (logger.py)
4. 异常定义 (exceptions.py)
5. 接口抽象 (interfaces.py)
6. LLM 客户端 (llm.py)
7. 工具函数 (utils.py)
8. OOP 布局引擎 (layout/)

注意：工作流相关代码已移至 workflow/ 模块
- AgentState -> workflow/state.py
- app_workflow -> workflow/orchestrator.py

Author: VibePoster Team
Date: 2025-01
"""

from .interfaces import (
    IKnowledgeGraph,
    IKnowledgeBase,
    IRendererService,
    IAssetSearcher,
)
from .utils import parse_llm_json_response, extract_json_from_text
from .layout import (
    Style,
    Element,
    TextBlock,
    ImageBlock,
    Container,
    VerticalContainer,
    HorizontalContainer,
)

__all__ = [
    # Interfaces
    "IKnowledgeGraph",
    "IKnowledgeBase",
    "IRendererService",
    "IAssetSearcher",
    # Utils
    "parse_llm_json_response",
    "extract_json_from_text",
    # Layout Engine
    "Style",
    "Element",
    "TextBlock",
    "ImageBlock",
    "Container",
    "VerticalContainer",
    "HorizontalContainer",
]
