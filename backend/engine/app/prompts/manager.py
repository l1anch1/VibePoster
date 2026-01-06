"""
Prompt 管理器 - 动态组装 Prompt 的逻辑
"""
from typing import Dict, Any, Optional, List
from .templates import (
    PLANNER_SYSTEM_PROMPT,
    VISUAL_ROUTING_PROMPT,
    LAYOUT_PROMPT_TEMPLATE,
    CRITIC_PROMPT_TEMPLATE,
)
from ..core.config import settings
from ..core.schemas import PosterData, Canvas, TextLayer, ImageLayer


def get_planner_prompt(
    user_prompt: str,
    chat_history: Optional[List[Dict[str, str]]] = None,
    template_context: Optional[str] = None
) -> Dict[str, str]:
    """
    获取 Planner Agent 的 prompt
    
    Args:
        user_prompt: 用户输入的提示词
        chat_history: 对话历史（可选）
        template_context: 风格模板上下文（可选）
        
    Returns:
        包含 system 和 user prompt 的字典
    """
    # 构建 system prompt（如果有风格模板，添加到 system prompt 中）
    system_prompt = PLANNER_SYSTEM_PROMPT
    if template_context:
        system_prompt = f"{PLANNER_SYSTEM_PROMPT}\n\n{template_context}\n\n请根据上述风格模板的配色、字体、布局原则来生成设计简报。"
    
    # 如果有对话历史，构建上下文
    user_content = user_prompt
    if chat_history:
        context = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in chat_history[-5:]  # 只取最近5轮对话
        ])
        user_content = f"【对话历史】\n{context}\n\n【当前请求】\n{user_prompt}"
    
    return {
        "system": system_prompt,
        "user": user_content,
    }


def get_visual_routing_prompt(
    image_count: int,
    design_brief: Dict[str, Any]
) -> str:
    """
    获取 Visual Agent 的路由决策 Prompt
    
    Args:
        image_count: 用户上传的图片数量
        design_brief: 设计简报
        
    Returns:
        格式化后的 prompt 字符串
    """
    import json
    
    prompt = VISUAL_ROUTING_PROMPT.format(
        image_count=image_count,
        design_brief=json.dumps(design_brief, ensure_ascii=False),
    )
    
    return prompt


def _generate_schema_description(canvas_width: int, canvas_height: int) -> str:
    """
    从 Pydantic Schema 生成易读的 Schema 描述
    
    基于 schemas.py 中定义的 PosterData、Canvas、TextLayer、ImageLayer 等模型
    生成符合实际 Schema 定义的描述，而不是硬编码。
    
    Args:
        canvas_width: 画布宽度（技术参数）
        canvas_height: 画布高度（技术参数）
        
    Returns:
        Schema 描述字符串
    """
    
    # 基于 Pydantic Schema 定义生成描述
    # 参考: schemas.py 中的 PosterData, Canvas, TextLayer, ImageLayer
    
    schema_desc = f"""{{
    "canvas": {{
        "width": {canvas_width},  // int, 画布宽度
        "height": {canvas_height},  // int, 画布高度
        "backgroundColor": "#000000"  // str, 背景色 Hex 值，可从 design_brief.background_color 获取
    }},
    "layers": [
        // 背景图层（必须存在，id="bg"）
        {{
            "id": "bg",  // str, 必须为 "bg"
            "name": "Background",  // str, 图层名称
            "type": "image",  // Literal["image"], 图层类型
            "src": "{{asset_list.background_layer.src}}",  // str, 必须使用 asset_list.background_layer.src
            "x": 0,  // int, 位置 X
            "y": 0,  // int, 位置 Y
            "width": {canvas_width},  // int, 宽度（必须 > 0）
            "height": {canvas_height},  // int, 高度（必须 > 0）
            "rotation": 0,  // int, 旋转角度（可选，默认 0）
            "opacity": 1.0,  // float, 透明度 0-1（可选，默认 1.0）
            "z_index": 0  // int, 图层顺序，背景必须为 0
        }},
        // 前景图层（可选，如果有 asset_list.foreground_layer，id="person" 或 "foreground"）
        {{
            "id": "person" | "foreground",  // str, 前景图层 ID
            "name": "Foreground",  // str, 图层名称
            "type": "image",  // Literal["image"]
            "src": "{{asset_list.foreground_layer.src}}",  // str, 必须使用 asset_list.foreground_layer.src
            "x": 200,  // int, 示例位置，请根据实际情况调整
            "y": 600,  // int, 示例位置，请根据实际情况调整
            "width": 400,  // int, ⚠️ 不超过画布宽度的50%（{canvas_width} * 0.5）
            "height": 600,  // int, ⚠️ 不超过画布高度的60%（{canvas_height} * 0.6）
            "rotation": 0,  // int, 可选
            "opacity": 1.0,  // float, 可选
            "z_index": 1  // int, 前景图层必须为 1
        }},
        // 标题图层（必须存在，id="title"）
        {{
            "id": "title",  // str, 必须为 "title"
            "name": "Title",  // str, 图层名称
            "type": "text",  // Literal["text"]
            "content": "{{design_brief.title}}",  // str, 从 design_brief.title 获取
            "x": 100,  // int, 示例位置，请根据实际情况调整
            "y": 100,  // int, 示例位置，请根据实际情况调整
            "width": 800,  // int, 必须设置，不能为 0
            "height": 120,  // int, 必须设置，不能为 0（考虑换行，可适当增加）
            "fontSize": 80,  // int, 字体大小（默认 24）
            "fontFamily": "Yuanti TC",  // str, 必须使用此字体
            "color": "#FFFFFF",  // str, 文字颜色 Hex 值，确保与背景对比度足够
            "textAlign": "left" | "center" | "right",  // str, 文本对齐方式（默认 "left"）
            "fontWeight": "normal" | "bold",  // str, 字体粗细（默认 "normal"）
            "rotation": 0,  // int, 可选
            "opacity": 1.0,  // float, 可选
            "z_index": 2  // int, 文字图层必须为 2
        }},
        // 副标题图层（必须存在，id="subtitle"）
        {{
            "id": "subtitle",  // str, 必须为 "subtitle"
            "name": "Subtitle",  // str, 图层名称
            "type": "text",  // Literal["text"]
            "content": "{{design_brief.subtitle}}",  // str, 从 design_brief.subtitle 获取
            "x": 100,  // int, 示例位置，请根据实际情况调整
            "y": 250,  // int, 示例位置，请根据实际情况调整（注意不要与标题重叠）
            "width": 800,  // int, 必须设置，不能为 0
            "height": 80,  // int, 必须设置，不能为 0（考虑换行，可适当增加）
            "fontSize": 50,  // int, 字体大小
            "fontFamily": "Yuanti TC",  // str, 必须使用此字体
            "color": "#FFFFFF",  // str, 文字颜色 Hex 值，确保与背景对比度足够
            "textAlign": "left" | "center" | "right",  // str, 文本对齐方式
            "fontWeight": "normal" | "bold",  // str, 字体粗细
            "rotation": 0,  // int, 可选
            "opacity": 1.0,  // float, 可选
            "z_index": 2  // int, 文字图层必须为 2
        }}
    ]
}}

【字段说明（基于 schemas.py 定义）】
- Canvas: width (int), height (int), backgroundColor (str)
- BaseLayer (所有图层共有): id (str), name (str), type (Literal), x (int), y (int), width (int), height (int), rotation (int, 默认0), opacity (float, 默认1.0)
- ImageLayer: 继承 BaseLayer，额外需要 src (str)
- TextLayer: 继承 BaseLayer，额外需要 content (str), fontSize (int, 默认24), color (str, 默认"#000000"), fontFamily (str, 默认"Yuanti TC"), textAlign (str, 默认"left"), fontWeight (str, 默认"normal")
- z_index: 虽然不在 BaseLayer 中，但 Layout Agent 必须为每个图层设置（背景=0, 前景=1, 文字=2）
- ⚠️ width 和 height 不能为 0，必须根据实际内容计算
- ⚠️ 文字图层的高度应考虑换行，适当增加高度值"""
    
    return schema_desc


def get_layout_prompt(
    design_brief: Dict[str, Any],
    asset_list: Dict[str, Any],
    canvas_width: int,
    canvas_height: int,
    review_feedback: Optional[Dict[str, Any]] = None,
) -> str:
    """
    获取 Layout Agent 的 prompt
    
    Args:
        design_brief: 设计简报（仅包含设计决策：标题、颜色、风格等）
        asset_list: 资产列表
        canvas_width: 画布宽度（技术参数，独立传入）
        canvas_height: 画布高度（技术参数，独立传入）
        review_feedback: 审核反馈（可选）
        
    Returns:
        格式化后的 prompt 字符串
    """
    import json
    
    # 构建审核反馈部分
    review_feedback_section = ""
    if review_feedback and review_feedback.get("status") == "REJECT":
        issues = review_feedback.get('issues', [])
        issues_text = '\n'.join([f"  - {issue}" for issue in issues]) if issues else "  - 无具体问题列表"
        
        review_feedback_section = f"""
【⚠️ 重要：审核反馈（必须修正）】
上一轮审核未通过，请仔细阅读以下反馈并修正：

审核意见: {review_feedback.get('feedback', '')}

具体问题列表:
{issues_text}

【修正要求】
1. 必须解决上述所有问题
2. 如果问题是"文字遮挡前景图层"，请将文字移动到不遮挡的位置
3. 如果问题是"文字超出画布范围"，请调整文字位置和大小，确保在画布内
4. 如果问题是"文字对比度不合格"，请更换文字颜色，确保与背景有足够对比度
5. 如果问题是"图层顺序不正确"，请确保 z_index 正确：背景=0，前景=1，文字=2
6. 如果问题是"图层缺少 width/height"，请为所有图层添加有效的 width 和 height

请根据以上反馈重新生成布局，确保所有问题都已解决。
"""
    
    # 动态生成 Schema 描述（画布尺寸作为独立参数传入）
    schema_description = _generate_schema_description(canvas_width, canvas_height)
    
    # 格式化 prompt（将 {schema} 替换为动态生成的 schema）
    prompt = LAYOUT_PROMPT_TEMPLATE.format(
        design_brief=json.dumps(design_brief, ensure_ascii=False),
        asset_list=json.dumps(asset_list, ensure_ascii=False),
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        review_feedback_section=review_feedback_section,
        schema=schema_description,  # 新增：动态生成的 schema
    )
    
    return prompt


def get_critic_prompt(poster_data: Dict[str, Any]) -> str:
    """
    获取 Critic Agent 的 prompt
    
    Args:
        poster_data: 海报数据
        
    Returns:
        格式化后的 prompt 字符串
    """
    import json
    
    prompt = CRITIC_PROMPT_TEMPLATE.format(
        poster_data=json.dumps(poster_data, ensure_ascii=False),
    )
    
    return prompt
