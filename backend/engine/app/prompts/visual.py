"""
Visual Agent Prompt - 图像分析
"""
from typing import Dict, Any


SYSTEM_PROMPT = """
请分析这张图片，提取以下信息：

## 📝 1. OCR 文字识别

识别图片中的所有可见文字（包括标题、副标题、标语、说明文字等），对于每个文字区域，请提供：
- 文字内容
- 位置描述（如：左上角、居中、右下角等）
- 文字大小（大标题、小标题、正文等）
- 识别置信度（高/中/低）

## 🎨 2. 图像理解

### 2.1 风格识别
判断图片的风格类型，从以下选项中选择一个：
- business（商务风格）
- campus（校园风格）
- event（活动风格）
- product（产品推广风格）
- festival（节日风格）
- other（其他风格）

### 2.2 配色分析
- 主色调：提取图片的主要颜色，以 Hex 格式输出（如 #1E3A8A）
- 配色方案：提取图片中的主要颜色组合，以 Hex 格式数组输出（如 ["#1E3A8A", "#3B82F6", "#FFFFFF"]）

### 2.3 元素识别
识别图片中包含的元素（可多选）：
- person（人物）
- product（产品）
- text（文字）
- background（背景）
- logo（标志）
- other（其他）

### 2.4 主题和情感
- 主题：判断图片的主题，如：招聘、活动、产品推广、宣传、其他
- 情感：判断图片传达的情感，如：正式、活泼、温馨、科技感、其他

### 2.5 布局建议
- text_position：文字位置建议（top/center/bottom）
- text_color_suggestion：建议的文字颜色（基于背景分析，确保可读性）

### 2.6 描述
用一句话描述这张图片的整体风格和内容。
"""


USER_PROMPT_TEMPLATE = """
**用户需求**: {user_prompt}

---

## 输出格式

请严格按照以下 JSON 格式输出，不要包含 Markdown 格式（如 ```json ... ```）：

{{
    "texts": [
        {{
            "content": "文字内容",
            "position": "位置描述",
            "size": "大小描述",
            "confidence": "高/中/低"
        }}
    ],
    "has_text": true,
    "style": "business",
    "main_color": "#1E3A8A",
    "color_palette": ["#1E3A8A", "#3B82F6", "#FFFFFF"],
    "elements": ["text", "background"],
    "theme": "招聘",
    "mood": "正式",
    "layout_hints": {{
        "text_position": "top",
        "text_color_suggestion": "#FFFFFF"
    }},
    "description": "一张深蓝色商务风格的招聘海报"
}}

注意：如果图片中没有文字，请将 `has_text` 设为 false，`texts` 设为空数组。
"""


def get_prompt(user_prompt: str) -> Dict[str, str]:
    """
    获取 Visual Agent 图像分析的 prompt
    
    Args:
        user_prompt: 用户输入的提示词
        
    Returns:
        包含 system 和 user prompt 的字典
    """
    return {
        "system": SYSTEM_PROMPT,
        "user": USER_PROMPT_TEMPLATE.format(user_prompt=user_prompt),
    }

