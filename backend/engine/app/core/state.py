"""
状态定义 - AgentState (LangGraph 工作流状态)
所有 Pydantic Schema 定义在 schemas.py 中，避免重复定义
"""
from typing import TypedDict, Optional, List, Dict, Any


# === LangGraph 状态定义 ===

class AgentState(TypedDict, total=False):
    """工作流状态定义"""
    user_prompt: str
    chat_history: Optional[List[Dict[str, str]]]  # 多轮对话历史
    user_images: Optional[List[Dict[str, Any]]]  # 用户上传的图片列表 [{"type": "person"|"background", "data": bytes}]
    canvas_width: int  # 画布宽度（用户输入的技术参数）
    canvas_height: int  # 画布高度（用户输入的技术参数）
    design_brief: Dict[str, Any]  # 设计简报（仅包含设计决策：标题、颜色、风格等）
    asset_list: Optional[Dict[str, Any]]  # 资产列表（背景图、前景图等）
    final_poster: Dict[str, Any]  # 最终海报数据
    review_feedback: Optional[Dict[str, Any]]  # 审核反馈
    _retry_count: int  # 重试计数器


# 注意：所有 Pydantic Schema（BaseLayer, TextLayer, ImageLayer, Canvas, PosterData 等）
# 都定义在 schemas.py 中，如需使用请从 schemas.py 导入
# 
# 工作流内部使用的数据结构（asset_list, review_feedback 等）目前使用 Dict[str, Any]
# 传递，未定义专门的 Pydantic Schema
