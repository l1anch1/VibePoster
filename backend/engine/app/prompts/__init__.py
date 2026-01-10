"""
Prompts 模块 - 按 Agent 组织的 Prompt 管理

每个 Agent 有独立的 prompt 文件：
- planner.py: Planner Agent (设计简报生成)
- visual.py: Visual Agent (图像分析)
- layout.py: Layout Agent (DSL 布局指令)
- critic.py: Critic Agent (质量审核)
"""
from . import planner
from . import visual
from . import layout
from . import critic

__all__ = ["planner", "visual", "layout", "critic"]
