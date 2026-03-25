"""
图像理解工具 - 使用 LLM Vision API 理解图片的风格、元素、主题等
同时完成 OCR 文字识别（一次 API 调用完成两个任务）
"""
import base64
from typing import Dict, Any, Optional
from ..core.logger import get_logger
from ..core.llm import LLMClientFactory
from ..core.config import settings
from ..core.exceptions import VibePosterException
from ..prompts import visual as visual_prompt
from ..core.utils import parse_llm_json_response

logger = get_logger(__name__)


def analyze_image_with_llm(
    image_data: bytes,
    user_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    使用 LLM Vision API 分析图片（OCR + 图像理解，一次调用完成）
    
    Args:
        image_data: 图片二进制数据
        user_prompt: 用户文字描述（可选，用于上下文）
        
    Returns:
        完整的分析结果字典，包含所有图像理解信息（OCR + 风格 + 配色等）
    """
    try:
        vision_provider = (settings.visual.VISION_PROVIDER or settings.visual.PROVIDER).value
        vision_api_key = settings.visual.VISION_API_KEY or settings.visual.API_KEY
        vision_base_url = settings.visual.VISION_BASE_URL or settings.visual.BASE_URL
        vision_model = settings.visual.VISION_MODEL

        client = LLMClientFactory.get_client(
            provider=vision_provider,
            api_key=vision_api_key,
            base_url=vision_base_url,
        )
        
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        prompts = visual_prompt.get_prompt(user_prompt if user_prompt else "无")
        prompt = f"{prompts['system']}\n\n{prompts['user']}"
        
        logger.info(f"🔍 开始图像分析（{vision_model} @ {vision_provider}）...")
        
        response = client.chat.completions.create(
            model=vision_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.2,  # 较低温度，确保准确性和一致性
        )
        
        content = response.choices[0].message.content
        
        # 使用统一的 JSON 解析工具
        fallback = {
            "texts": [],
            "has_text": False,
            "style": "other",
            "main_color": "#000000",
            "color_palette": ["#000000", "#FFFFFF"],
            "elements": [],
            "theme": "其他",
            "mood": "其他",
            "layout_hints": {
                "text_position": "center",
                "text_color_suggestion": "#000000"
            },
            "description": "无法识别图片内容"
        }
        result = parse_llm_json_response(content, fallback=fallback, context="图像分析")
        
        # 确保关键字段存在
        if "texts" not in result:
            result["texts"] = []
        if "has_text" not in result:
            result["has_text"] = False
        if "style" not in result:
            result["style"] = "other"
        
        ocr_count = len(result.get("texts", []))
        style = result.get("style", "unknown")
        
        logger.info(f"✅ 图像分析完成: 风格={style}, 识别文字数={ocr_count}")
        return result
        
    except Exception as e:
        logger.error(f"❌ 图像分析失败: {e}")
        # 返回默认值
        return {
            "texts": [],
            "has_text": False,
            "style": "other",
            "main_color": "#000000",
            "color_palette": ["#000000", "#FFFFFF"],
            "elements": [],
            "theme": "其他",
            "mood": "其他",
            "layout_hints": {
                "text_position": "center",
                "text_color_suggestion": "#000000"
            },
            "description": "图像分析失败",
            "error": str(e)
        }


def generate_suggestions(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    基于图像分析结果生成建议
    
    Args:
        analysis_result: 图像分析结果（包含 OCR + 图像理解）
        
    Returns:
        建议字典
    """
    # 从 OCR 提取标题候选
    title_candidates = []
    if analysis_result.get("has_text"):
        texts = analysis_result.get("texts", [])
        for text_info in texts:
            content = text_info.get("content", "")
            if content and len(content) > 0:
                # 优先选择较短的文字作为标题候选
                if len(content) <= 20:  # 标题通常较短
                    title_candidates.append(content)
    
    # 提取风格关键词
    style = analysis_result.get("style", "other")
    theme = analysis_result.get("theme", "其他")
    mood = analysis_result.get("mood", "其他")
    
    style_keywords = []
    if style != "other":
        style_keywords.append(style)
    if theme != "其他":
        style_keywords.append(theme.lower())
    if mood != "其他":
        style_keywords.append(mood.lower())
    
    # 配色方案建议
    color_scheme = {
        "primary": analysis_result.get("main_color", "#000000"),
        "secondary": analysis_result.get("color_palette", ["#000000"])[0] if analysis_result.get("color_palette") else "#000000",
        "text_color": analysis_result.get("layout_hints", {}).get("text_color_suggestion", "#000000")
    }
    
    # 字体风格建议（基于风格和情感）
    font_style_map = {
        "business": "现代、简洁",
        "campus": "活泼、年轻",
        "event": "醒目、动感",
        "product": "专业、现代",
        "festival": "装饰性、喜庆",
        "other": "通用"
    }
    font_style = font_style_map.get(style, "通用")
    
    return {
        "title_candidates": title_candidates[:3],  # 最多3个候选
        "style_keywords": style_keywords,
        "color_scheme": color_scheme,
        "font_style": font_style
    }


def understand_image(
    image_data: bytes,
    user_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    理解图片（统一接口，包含 OCR + 图像理解）
    
    Args:
        image_data: 图片二进制数据
        user_prompt: 用户文字描述（可选）
        
    Returns:
        综合结果字典，包含所有分析信息和建议
    """
    # 一次 API 调用完成 OCR + 图像理解（优化版本）
    analysis_result = analyze_image_with_llm(image_data, user_prompt)
    
    # 生成建议
    suggestions = generate_suggestions(analysis_result)
    
    # 合并结果（保持向后兼容）
    result = {
        # 保留旧的分离格式（向后兼容）
        "ocr": {
            "texts": analysis_result.get("texts", []),
            "has_text": analysis_result.get("has_text", False)
        },
        "understanding": {
            "style": analysis_result.get("style", "other"),
            "main_color": analysis_result.get("main_color", "#000000"),
            "color_palette": analysis_result.get("color_palette", ["#000000", "#FFFFFF"]),
            "elements": analysis_result.get("elements", []),
            "theme": analysis_result.get("theme", "其他"),
            "mood": analysis_result.get("mood", "其他"),
            "layout_hints": analysis_result.get("layout_hints", {
                "text_position": "center",
                "text_color_suggestion": "#000000"
            }),
            "description": analysis_result.get("description", "未识别")
        },
        "suggestions": suggestions
    }
    
    return result

