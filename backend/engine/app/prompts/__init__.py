"""
Prompts 模块 - 按 Agent 组织的 Prompt 管理

每个 Agent 有独立的 prompt 文件：
- visual.py: Visual Agent (图像分析)
- layout.py: Layout Agent (DSL 布局指令)
- critic.py: Critic Agent (质量审核)

注意：Planner 的 Prompt 已迁移至 skills/design_brief/
"""
from . import planner
from . import visual
from . import layout
from . import critic

__all__ = ["planner", "visual", "layout", "critic"]
