"""
Visual Agent - 视觉感知中心
处理图片（分析、搜图、素材处理）
"""

from typing import Dict, Any, Optional, List
from ..core.config import settings, ERROR_FALLBACKS
from ..core.logger import get_logger
from ..tools.vision import image_to_base64
from ..tools import search_assets
from ..tools.image_understanding import understand_image

logger = get_logger(__name__)


def run_visual_agent(
    user_images: Optional[List[Dict[str, Any]]], 
    design_brief: Dict[str, Any]
) -> Dict[str, Any]:
    """
    运行 Visual Agent（增强版：包含 OCR + 图像理解）

    路由逻辑（对应前端三种模式）：
    - Text Only（无图）：去素材库搜/生成背景
    - Style Reference（单图 type=background）：提取参考图风格，生成新背景
    - With Material（单图 type=subject）：直接使用主体素材 + 搜索/生成背景

    Args:
        user_images: 用户上传的图片列表 [{"type": "subject"|"background", "data": bytes}]
        design_brief: 设计简报

    Returns:
        资产列表字典（包含 OCR 和图像理解结果）
    """
    logger.info("🎨 Visual Agent 正在处理图片...")

    image_count = len(user_images) if user_images else 0
    
    # 存储所有图片的理解结果
    image_analyses = []

    try:
        # 如果有用户上传的图片，进行 OCR + 图像理解
        if user_images:
            user_prompt = design_brief.get("user_prompt", "")
            for img in user_images:
                image_data = img.get("data")
                image_type = img.get("type", "unknown")
                
                if image_data:
                    logger.info(f"🔍 正在分析图片（类型: {image_type}）...")
                    
                    # OCR + 图像理解
                    analysis_result = understand_image(
                        image_data=image_data,
                        user_prompt=user_prompt
                    )
                    
                    # 将分析结果添加到图片信息中
                    img["ocr"] = analysis_result.get("ocr", {})
                    img["understanding"] = analysis_result.get("understanding", {})
                    img["suggestions"] = analysis_result.get("suggestions", {})
                    
                    image_analyses.append({
                        "type": image_type,
                        "analysis": analysis_result
                    })
                    
                    logger.info(f"✅ 图片分析完成: 风格={analysis_result.get('understanding', {}).get('style')}, "
                              f"识别文字数={len(analysis_result.get('ocr', {}).get('texts', []))}")
        
        # 如果 OCR 识别出文字，可以用于优化设计简报
        # 收集所有识别出的文字作为标题候选
        all_title_candidates = []
        all_style_keywords = []
        color_scheme_suggestions = {}
        
        for analysis in image_analyses:
            suggestions = analysis.get("analysis", {}).get("suggestions", {})
            all_title_candidates.extend(suggestions.get("title_candidates", []))
            all_style_keywords.extend(suggestions.get("style_keywords", []))
            
            # 合并配色方案建议（优先使用第一个）
            if not color_scheme_suggestions:
                color_scheme_suggestions = suggestions.get("color_scheme", {})
        
        # 如果识别出标题候选，更新设计简报（可选）
        if all_title_candidates and not design_brief.get("title"):
            # 使用第一个标题候选
            design_brief["title"] = all_title_candidates[0]
            logger.info(f"📝 使用 OCR 识别的标题: {all_title_candidates[0]}")
        
        # 合并风格关键词
        if all_style_keywords:
            existing_keywords = design_brief.get("style_keywords", [])
            # 去重并合并
            combined_keywords = list(set(existing_keywords + all_style_keywords))
            design_brief["style_keywords"] = combined_keywords[:5]  # 最多5个
            logger.info(f"🎨 合并后的风格关键词: {combined_keywords[:5]}")

        # 情况 C：无图，使用文生图或搜索素材库
        if image_count == 0:
            logger.info("📚 情况 C：无图，生成/搜索背景图...")
            keywords = design_brief.get("style_keywords", [])
            # 传递 design_brief 以便构建更精确的 Flux 提示词
            bg_url = search_assets(keywords, design_brief=design_brief, use_generation=True)

            return {
                "background_layer": {
                    "type": "image",
                    "src": bg_url,
                    "source_type": "generated" if bg_url.startswith("data:") else "stock",
                },
                "image_analyses": image_analyses,  # 即使无图也返回（为空列表）
            }

        # 情况 A 或 B：有图，需要路由决策
        if image_count == 1:
            img = user_images[0]
            image_data = img.get("data")
            image_type = img.get("type", "unknown")
            image_analysis = image_analyses[0] if image_analyses else None

            if image_type == "background":
                # Style Clone：提取参考图的风格，然后生成全新背景
                logger.info("🎨 Style Clone：提取参考图风格，生成新背景...")

                # 图像理解已在上方完成，风格关键词已合并进 design_brief
                # 额外将参考图的配色注入 design_brief，让 Flux/搜索更精准
                if image_analysis:
                    understanding = image_analysis.get("analysis", {}).get("understanding", {})
                    if understanding:
                        ref_palette = understanding.get("color_palette", [])
                        ref_style = understanding.get("style")
                        if ref_palette:
                            design_brief["reference_palette"] = ref_palette
                        if ref_style:
                            existing = design_brief.get("style_keywords", [])
                            if ref_style not in existing:
                                design_brief["style_keywords"] = (existing + [ref_style])[:6]
                        logger.info(f"🎨 参考图风格: {ref_style}, 配色: {ref_palette}")

                keywords = design_brief.get("style_keywords", [])
                bg_url = search_assets(keywords, design_brief=design_brief, use_generation=True)

                result = {
                    "background_layer": {
                        "type": "image",
                        "src": bg_url,
                        "source_type": "generated" if bg_url.startswith("data:") else "stock",
                    },
                    "image_analyses": image_analyses,
                }

                if image_analysis:
                    understanding = image_analysis.get("analysis", {}).get("understanding", {})
                    if understanding:
                        result["color_suggestions"] = {
                            "primary": understanding.get("main_color"),
                            "palette": understanding.get("color_palette", []),
                            "text_color": understanding.get("layout_hints", {}).get("text_color_suggestion"),
                        }

                return result

            # 情况 B：单图(主体素材) → 直接编码 + 搜索/生成背景
            logger.info("📸 情况 B：单图(主体素材)，直接使用透明 PNG...")

            if image_data:
                subject_b64 = image_to_base64(image_data)

                keywords = design_brief.get("style_keywords", [])
                bg_url = search_assets(keywords, design_brief=design_brief, use_generation=True)

                result = {
                    "background_layer": {
                        "type": "image",
                        "src": bg_url,
                        "source_type": "stock",
                    },
                    "subject_layer": {
                        "type": "image",
                        "src": subject_b64,
                        "source_type": "user_upload",
                        "suggested_position": settings.visual.DEFAULT_POSITION,
                    },
                    "image_analyses": image_analyses,
                }

                if image_analysis:
                    understanding = image_analysis.get("analysis", {}).get("understanding", {})
                    if understanding:
                        result["color_suggestions"] = {
                            "primary": understanding.get("main_color"),
                            "palette": understanding.get("color_palette", []),
                            "text_color": understanding.get("layout_hints", {}).get("text_color_suggestion"),
                        }

                return result

        # 不支持的图片数量
        raise ValueError(f"不支持的图片数量: {image_count}，请使用 Text Only / Style Reference / With Material 三种模式")

    except Exception as e:
        logger.error(f"❌ Visual Agent 出错: {e}")
        return ERROR_FALLBACKS["visual"]


def visual_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Visual Agent 工作流节点

    Args:
        state: 工作流状态

    Returns:
        更新后的状态
    """
    user_images = state.get("user_images")
    design_brief = state.get("design_brief", {})
    user_prompt = state.get("user_prompt", "")
    
    # 将 user_prompt 添加到 design_brief 中，供 OCR + 图像理解使用
    if user_prompt and "user_prompt" not in design_brief:
        design_brief["user_prompt"] = user_prompt

    asset_list = run_visual_agent(user_images, design_brief)

    return {"asset_list": asset_list}
