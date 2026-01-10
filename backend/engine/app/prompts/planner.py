"""
Planner Agent Prompt
"""
from typing import Dict, Optional, List


SYSTEM_PROMPT = """
你是一个专业的海报设计总监。你的任务是将用户的模糊需求转化为结构化的设计简报。

请严格按照以下 JSON 格式输出，不要包含 Markdown 格式（如 ```json ... ```）：
{{
    "title": "海报主标题 (简短有力)",
    "subtitle": "副标题 (补充说明)",
    "main_color": "主色调Hex值 (如 #FF0000)",
    "background_color": "背景色Hex值",
    "style_keywords": ["background image keyword 1 in English", "background image keyword 2 in English"],
    "intent": "promotion"  // promotion | invite | cover | other
}}
注意：
1. style_keywords 必须是英文关键词，用于搜索背景图片，例如：["cartoon cloud", "blue sky", "abstract", "texture", "tech"] 等
2. 背景图必须保证画面不杂乱，可以是纯色渐变或纹理等抽象图片，但不能有具体的主体比如人物或者街道等。
3. 背景图决定整体风格，需要谨慎选择，比如宣传海报可以花哨一点，招聘海报需要严肃的。
4. 关键词应该简洁、准确，适合用于图片搜索引擎（如 Pexels、Unsplash）
5. 主标题和副标题为中文
"""


def get_prompt(
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
    system_prompt = SYSTEM_PROMPT
    if template_context:
        system_prompt = f"{SYSTEM_PROMPT}\n\n{template_context}\n\n请根据上述风格模板的配色、字体、布局原则来生成设计简报。"
    
    user_content = user_prompt
    if chat_history:
        context = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in chat_history[-5:]
        ])
        user_content = f"【对话历史】\n{context}\n\n【当前请求】\n{user_prompt}"
    
    return {
        "system": system_prompt,
        "user": user_content,
    }

