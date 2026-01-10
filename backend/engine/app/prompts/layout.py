"""
Layout Agent Prompt - DSL 布局指令生成
"""
import json
from typing import Dict, Any, Optional


SYSTEM_PROMPT = """
[System Request]
你是一个智能布局规划器。请根据设计简报和素材，输出 DSL (Domain Specific Language) 指令列表。

[User Request]
你是一个专业的海报布局规划器。请根据输入生成布局指令。

【DSL 指令格式】
你需要输出一个 JSON 数组，每个元素是一条布局指令。

可用的指令类型：
1. add_title - 添加主标题
   {{
     "command": "add_title",
     "content": "标题文本",
     "font_size": 64,  // 可选，默认 48
     "color": "#FFFFFF",  // 可选，默认使用设计简报中的主色调
     "text_align": "center"  // 可选，left/center/right，默认 center
   }}

2. add_subtitle - 添加副标题
   {{
     "command": "add_subtitle", 
     "content": "副标题文本",
     "font_size": 36,  // 可选，默认 32
     "color": "#CCCCCC"  // 可选，默认 #666666
   }}

3. add_text - 添加正文文本
   {{
     "command": "add_text",
     "content": "正文内容...",
     "font_size": 24,  // 可选，默认 24
     "color": "#333333",  // 可选
     "text_align": "left"  // 可选
   }}

4. add_image - 添加图片（背景或主图）
   {{
     "command": "add_image",
     "src": "{{ASSET_BG}}" 或 "{{ASSET_FG}}",  // 使用占位符，系统会自动填充
     "width": 800,  // 建议宽度
     "height": 600,  // 建议高度
     "layer_type": "background" | "foreground"  // 图片类型
   }}

5. add_cta - 添加行动号召按钮文本
   {{
     "command": "add_cta",
     "content": "立即行动 →",
     "font_size": 28,  // 可选
     "color": "#0066FF"  // 可选，默认使用强调色
   }}

【注意】背景色从 design_brief.background_color 自动获取，不需要输出指令。

【设计原则】
1. 从设计简报 (design_brief) 中获取：
   - title: 主标题文本
   - subtitle: 副标题文本
   - main_color: 主色调
   - background_color: 背景色
   - kg_rules: 知识图谱推荐的颜色/字体/布局
   - brand_knowledge: 品牌知识（如有）

2. 布局顺序建议（从上到下）：
   - 背景图（如果有）
   - 主标题
   - 副标题
   - 主图/前景图（如果有）
   - 正文描述（如果有）
   - 行动号召（CTA）

3. 颜色对比度：
   - 确保文字颜色与背景对比度足够
   - 深色背景用浅色文字，浅色背景用深色文字

4. 素材使用：
   - 如果 asset_list 中有 background_layer，添加背景图
   - 如果 asset_list 中有 foreground_layer，添加前景图
   - 图片 src 使用占位符，系统会自动填充
"""


USER_PROMPT_TEMPLATE = """
【输入】
- 设计简报: {design_brief}
- 素材列表: {asset_list}
- 画布尺寸: {canvas_width}x{canvas_height}
{review_feedback_section}

【输出格式】
仅输出 JSON，不要包含任何其他文本：

{{
  "dsl_instructions": [
    {{"command": "add_image", "src": "{{ASSET_BG}}", "width": 1080, "height": 1920, "layer_type": "background"}},
    {{"command": "add_title", "content": "主标题", "font_size": 64, "color": "#FFFFFF"}},
    {{"command": "add_subtitle", "content": "副标题", "font_size": 36, "color": "#AAAAAA"}},
    {{"command": "add_cta", "content": "了解更多 →", "color": "#FF6B6B"}}
  ]
}}

请根据输入生成合适的 DSL 指令列表。
"""


def get_prompt(
    design_brief: Dict[str, Any],
    asset_list: Dict[str, Any],
    canvas_width: int,
    canvas_height: int,
    review_feedback: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """
    获取 Layout Agent 的 DSL prompt
    
    Args:
        design_brief: 设计简报
        asset_list: 素材列表
        canvas_width: 画布宽度
        canvas_height: 画布高度
        review_feedback: 审核反馈（可选）
    
    Returns:
        包含 system 和 user prompt 的字典
    """
    # 构建审核反馈部分
    review_feedback_section = ""
    if review_feedback and review_feedback.get("status") == "REJECT":
        issues = review_feedback.get('issues', [])
        issues_text = '\n'.join([f"  - {issue}" for issue in issues]) if issues else ""
        
        review_feedback_section = f"""

【⚠️ 审核反馈（需要修正）】
审核意见: {review_feedback.get('feedback', '')}
具体问题:
{issues_text}

请根据反馈调整 DSL 指令。
"""
    
    user_prompt = USER_PROMPT_TEMPLATE.format(
        design_brief=json.dumps(design_brief, ensure_ascii=False, indent=2),
        asset_list=json.dumps(asset_list, ensure_ascii=False, indent=2),
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        review_feedback_section=review_feedback_section
    )
    
    return {
        "system": SYSTEM_PROMPT,
        "user": user_prompt,
    }

