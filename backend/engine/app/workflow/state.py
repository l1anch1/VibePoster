"""
工作流状态定义 - AgentState (LangGraph 工作流状态)

职责：
1. 定义工作流状态结构
2. 作为 Agent 之间传递数据的契约

注意：所有 Pydantic Schema（BaseLayer, TextLayer, ImageLayer, Canvas, PosterData 等）
都定义在 models/ 目录中，如需使用请从 models 导入

Author: VibePoster Team
Date: 2025-01
"""

from typing import TypedDict, Optional, List, Dict, Any, Callable


class AgentState(TypedDict, total=False):
    """
    工作流状态定义
    
    字段说明：
    - user_prompt: 用户输入的提示词
    - chat_history: 多轮对话历史（可选）
    - user_images: 用户上传的图片列表
    - canvas_width: 画布宽度（用户输入的技术参数）
    - canvas_height: 画布高度（用户输入的技术参数）
    - brand_name: 品牌名称（用于 RAG 检索）
    - design_brief: 设计简报（由 Planner Agent 生成）
    - asset_list: 资产列表（背景图、前景图等）
    - final_poster: 最终海报数据
    - review_feedback: 审核反馈
    - _retry_count: 重试计数器
    - search_assets: 素材搜索函数（依赖注入）
    """
    user_prompt: str
    chat_history: Optional[List[Dict[str, str]]]
    user_images: Optional[List[Dict[str, Any]]]
    canvas_width: int
    canvas_height: int
    brand_name: Optional[str]
    design_brief: Dict[str, Any]
    asset_list: Optional[Dict[str, Any]]
    final_poster: Dict[str, Any]
    review_feedback: Optional[Dict[str, Any]]
    _retry_count: int
    search_assets: Optional[Callable]

