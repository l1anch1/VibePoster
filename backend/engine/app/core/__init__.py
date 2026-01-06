"""
Core 模块 - 系统基础
"""
from .state import AgentState

# 注意：config 模块使用显式导入，避免 import * 带来的命名空间污染
# 使用方式：from ..core.config import settings

__all__ = ["AgentState"]

