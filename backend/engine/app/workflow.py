"""
工作流编排 - LangGraph 编排 (只负责连线)
支持条件边，实现审核反馈循环
"""
from langgraph.graph import StateGraph, END

# 引入状态定义
from .core.state import AgentState

# 引入配置
from .core.config import settings

# 引入各个 Agent 节点
from .agents import (
    planner_node,
    visual_node,
    layout_node,
    critic_node,
    should_retry_layout,
)


def build_workflow():
    """
    根据配置构建工作流
    
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
    workflow.set_entry_point(settings.WORKFLOW_CONFIG["entry_point"])
    
    # 添加边（根据配置）
    # 先添加普通边
    for edge in settings.WORKFLOW_CONFIG["edges"]:
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


# 编译工作流
app_workflow = build_workflow()
