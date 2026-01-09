"""
工作流编排 - LangGraph 编排

职责：
1. 构建工作流图
2. 配置节点和边
3. 处理条件边（审核反馈循环）

Author: VibePoster Team
Date: 2025-01
"""

from langgraph.graph import StateGraph, END

from .state import AgentState
from ..core.config import settings, WORKFLOW_CONFIG
from ..agents import (
    planner_node,
    visual_node,
    layout_node,
    critic_node,
    should_retry_layout,
)


def build_workflow():
    """
    根据配置构建工作流
    
    工作流结构：
        Planner -> Visual -> Layout -> Critic
                                ↑        ↓
                                └── retry ←─ (if reject)
                                         ↓
                                        END (if pass)
    
    Returns:
        编译后的工作流
    """
    workflow = StateGraph(AgentState)
    
    # 添加节点（从各个 agent 文件导入）
    workflow.add_node("planner", planner_node)
    workflow.add_node("visual", visual_node)
    workflow.add_node("layout", layout_node)
    workflow.add_node("critic", critic_node)
    
    # 设置入口点（从配置读取）
    workflow.set_entry_point(WORKFLOW_CONFIG["entry_point"])
    
    # 添加边（根据配置）
    # 先添加普通边
    for edge in WORKFLOW_CONFIG["edges"]:
        if not edge.get("condition"):
            if edge["to"] == "END":
                # 跳过，后面用条件边处理
                continue
            else:
                workflow.add_edge(edge["from"], edge["to"])
    
    # 添加条件边（critic -> layout 或 END）
    workflow.add_conditional_edges(
        "critic",
        should_retry_layout,
        {
            "retry": "layout",  # 重试 layout
            "end": END,  # 结束
        }
    )
    
    return workflow.compile()


# 编译工作流（单例）
app_workflow = build_workflow()

