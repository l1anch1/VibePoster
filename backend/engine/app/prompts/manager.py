"""
Prompt 管理器 - 动态组装 Prompt 的逻辑
"""
from typing import Dict, Any, Optional, List
from .templates import (
    DIRECTOR_SYSTEM_PROMPT,
    PROMPTER_ROUTING_PROMPT,
    LAYOUT_PROMPT_TEMPLATE,
    REVIEWER_PROMPT_TEMPLATE,
)
from ..core.config import CANVAS_DEFAULTS


def get_director_prompt(
    user_prompt: str,
    chat_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, str]:
    """
    获取 Director Agent 的 prompt
    
    Args:
        user_prompt: 用户输入的提示词
        chat_history: 对话历史（可选）
        
    Returns:
        包含 system 和 user prompt 的字典
    """
    # 如果有对话历史，构建上下文
    user_content = user_prompt
    if chat_history:
        context = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in chat_history[-5:]  # 只取最近5轮对话
        ])
        user_content = f"【对话历史】\n{context}\n\n【当前请求】\n{user_prompt}"
    
    return {
        "system": DIRECTOR_SYSTEM_PROMPT,
        "user": user_content,
    }


def get_prompter_routing_prompt(
    image_count: int,
    design_brief: Dict[str, Any]
) -> str:
    """
    获取 Prompter Agent 的路由决策 Prompt
    
    Args:
        image_count: 用户上传的图片数量
        design_brief: 设计简报
        
    Returns:
        格式化后的 prompt 字符串
    """
    import json
    
    prompt = PROMPTER_ROUTING_PROMPT.format(
        image_count=image_count,
        design_brief=json.dumps(design_brief, ensure_ascii=False),
    )
    
    return prompt


def get_layout_prompt(
    design_brief: Dict[str, Any],
    asset_list: Dict[str, Any],
    canvas_width: int = None,
    canvas_height: int = None,
    review_feedback: Optional[Dict[str, Any]] = None,
) -> str:
    """
    获取 Layout Agent 的 prompt
    
    Args:
        design_brief: 设计简报
        asset_list: 资产列表
        canvas_width: 画布宽度（默认从配置读取）
        canvas_height: 画布高度（默认从配置读取）
        review_feedback: 审核反馈（可选）
        
    Returns:
        格式化后的 prompt 字符串
    """
    import json
    
    canvas_width = canvas_width or CANVAS_DEFAULTS["width"]
    canvas_height = canvas_height or CANVAS_DEFAULTS["height"]
    
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
    
    # 格式化 prompt
    prompt = LAYOUT_PROMPT_TEMPLATE.format(
        design_brief=json.dumps(design_brief, ensure_ascii=False),
        asset_list=json.dumps(asset_list, ensure_ascii=False),
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        review_feedback_section=review_feedback_section,
    )
    
    return prompt


def get_reviewer_prompt(poster_data: Dict[str, Any]) -> str:
    """
    获取 Reviewer Agent 的 prompt
    
    Args:
        poster_data: 海报数据
        
    Returns:
        格式化后的 prompt 字符串
    """
    import json
    
    prompt = REVIEWER_PROMPT_TEMPLATE.format(
        poster_data=json.dumps(poster_data, ensure_ascii=False),
    )
    
    return prompt
