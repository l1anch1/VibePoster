"""
工作流编排 - LangGraph 编排

工作流结构：
    Planner -> Visual -> Layout -> Critic
                            ^        |
                            +--retry--+ (if reject)
                                      |
                                     END (if pass)
"""

from langgraph.graph import StateGraph, END

from .state import AgentState
from ..agents import (
    planner_node,
    visual_node,
    layout_node,
    critic_node,
    should_retry_layout,
)


def build_workflow():
    """构建并编译海报生成工作流"""
    workflow = StateGraph(AgentState)

    workflow.add_node("planner", planner_node)
    workflow.add_node("visual", visual_node)
    workflow.add_node("layout", layout_node)
    workflow.add_node("critic", critic_node)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "visual")
    workflow.add_edge("visual", "layout")
    workflow.add_edge("layout", "critic")
    workflow.add_conditional_edges(
        "critic",
        should_retry_layout,
        {"retry": "layout", "end": END},
    )

    return workflow.compile()


# 编译工作流（单例）
app_workflow = build_workflow()
