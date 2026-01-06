"""
Visual Agent - 视觉感知中心
处理图片（抠图、分析、搜图），是"视觉感知中心"
"""

from typing import Dict, Any, Optional, List
from ..core.config import settings
from ..core.llm import LLMClientFactory
from ..core.logger import get_logger
from ..tools.vision import process_cutout, image_to_base64
from ..tools import search_assets
from ..tools.image_understanding import understand_image
from .base import BaseAgent

logger = get_logger(__name__)


class VisualAgent(BaseAgent):
    """Visual Agent 实现类（用于路由决策）"""

    def _create_client(self):
        return LLMClientFactory.get_client(
            provider=self.config.get("provider", "deepseek"),
            api_key=self.config.get("api_key"),
            base_url=self.config.get("base_url"),
        )

    def invoke(self, messages: list, **kwargs) -> Dict[str, Any]:
        """调用 Visual Agent"""
        response = self.client.chat.completions.create(
            model=self.config["model"],
            messages=messages,
            temperature=self.config["temperature"],
            response_format=self.config.get("response_format"),
            **kwargs,
        )
        return response


def run_visual_agent(
    user_images: Optional[List[Dict[str, Any]]], 
    design_brief: Dict[str, Any]
) -> Dict[str, Any]:
    """
    运行 Visual Agent（增强版：包含 OCR + 图像理解）

    路由逻辑：
    - 情况 A（双图）：用户传了 Image A (背景) + Image B (人) -> 抠图 B，保留 A
    - 情况 B（单图）：用户传了 Image B (人) -> 抠图 B，去素材库搜/生成背景 A
    - 情况 C（无图）：去素材库搜/生成背景 A

    Args:
        user_images: 用户上传的图片列表 [{"type": "person"|"background", "data": bytes}]
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

        # 情况 C：无图，直接搜索素材库
        if image_count == 0:
            logger.info("📚 情况 C：无图，搜索素材库...")
            keywords = design_brief.get("style_keywords", [])
            bg_url = search_assets(keywords)

            return {
                "background_layer": {
                    "type": "image",
                    "src": bg_url,
                    "source_type": "stock",
                },
                "image_analyses": image_analyses,  # 即使无图也返回（为空列表）
            }

        # 情况 A 或 B：有图，需要路由决策
        # 使用 LLM 做路由决策（如果图片数量不明确）
        if image_count == 1:
            # 单图情况：判断是人物还是背景
            # 简化处理：假设是人物，进行抠图
            logger.info("📸 情况 B：单图，假设是人物，进行抠图...")
            image_data = user_images[0].get("data")
            image_analysis = image_analyses[0] if image_analyses else None

            if image_data:
                # 抠图
                cutout_result = process_cutout(image_data)

                # 搜索背景（优先使用图像理解提取的风格关键词）
                keywords = design_brief.get("style_keywords", [])
                bg_url = search_assets(keywords)

                result = {
                    "background_layer": {
                        "type": "image",
                        "src": bg_url,
                        "source_type": "stock",
                    },
                    "foreground_layer": {
                        "type": "image",
                        "src": cutout_result["processed_image_base64"],
                        "source_type": "user_upload",
                        "width": cutout_result["width"],
                        "height": cutout_result["height"],
                        "suggested_position": settings.visual.DEFAULT_POSITION,
                        "subject_bbox": cutout_result.get("subject_bbox"),
                    },
                    "image_analyses": image_analyses,
                }
                
                # 如果图像理解提供了配色建议，添加到结果中
                if image_analysis:
                    understanding = image_analysis.get("analysis", {}).get("understanding", {})
                    if understanding:
                        result["color_suggestions"] = {
                            "primary": understanding.get("main_color"),
                            "palette": understanding.get("color_palette", []),
                            "text_color": understanding.get("layout_hints", {}).get("text_color_suggestion")
                        }
                
                return result

        elif image_count >= 2:
            # 情况 A：双图，第一张是背景，第二张是人物
            logger.info("📸 情况 A：双图融合，第一张背景，第二张人物...")
            bg_data = user_images[0].get("data")
            person_data = user_images[1].get("data")
            
            bg_analysis = image_analyses[0] if len(image_analyses) > 0 else None
            person_analysis = image_analyses[1] if len(image_analyses) > 1 else None

            # 背景图转 Base64
            bg_base64 = image_to_base64(bg_data) if bg_data else None

            # 人物图抠图
            cutout_result = process_cutout(person_data) if person_data else None

            if not bg_base64 or not cutout_result:
                raise ValueError("图片处理失败")

            result = {
                "background_layer": {
                    "type": "image",
                    "src": bg_base64,
                    "source_type": "user_upload",
                },
                "foreground_layer": {
                    "type": "image",
                    "src": cutout_result["processed_image_base64"],
                    "source_type": "user_upload",
                    "width": cutout_result["width"],
                    "height": cutout_result["height"],
                    "suggested_position": settings.visual.DEFAULT_POSITION,
                    "subject_bbox": cutout_result.get("subject_bbox"),
                },
                "image_analyses": image_analyses,
            }
            
            # 如果背景图有图像理解结果，添加配色建议
            if bg_analysis:
                understanding = bg_analysis.get("analysis", {}).get("understanding", {})
                if understanding:
                    result["color_suggestions"] = {
                        "primary": understanding.get("main_color"),
                        "palette": understanding.get("color_palette", []),
                        "text_color": understanding.get("layout_hints", {}).get("text_color_suggestion")
                    }
            
            return result

        # 默认情况
        raise ValueError(f"无法处理的图片数量: {image_count}")

    except Exception as e:
        logger.error(f"❌ Visual Agent 出错: {e}")
        return settings.ERROR_FALLBACKS["visual"]


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
