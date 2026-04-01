"""
素材服务 — 从 step_assets 路由中提取的业务逻辑

三种模式：
- Text Only:       纯文本 → 搜索/生成背景
- Style Reference:  背景参考图 → 分析风格后搜索匹配背景
- With Material:    主体素材 + 可选背景 → 处理主体，搜索/生成背景
"""

from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field

from ..tools import search_assets_multiple
from ..tools.vision import image_to_base64, analyze_image
from ..tools.image_understanding import understand_image
from ..core.logger import get_logger

logger = get_logger(__name__)


class AssetResult(BaseModel):
    """step_assets 的统一返回结构"""
    candidates: List[str]
    keywords_used: List[str]
    design_brief: Dict[str, Any]
    image_analyses: List[Dict[str, Any]] = Field(default_factory=list)
    color_suggestions: Optional[Dict[str, Any]] = None
    subject_url: Optional[str] = None
    subject_width: Optional[int] = None
    subject_height: Optional[int] = None


class AssetService:
    """素材搜索与处理服务"""

    def process_text_only(
        self,
        design_brief: Dict[str, Any],
        count: int,
    ) -> AssetResult:
        """模式 1: 纯文本 — 直接搜索/生成背景候选"""
        keywords = design_brief.get("style_keywords", [])
        candidates = search_assets_multiple(
            keywords=keywords,
            design_brief=design_brief,
            count=count,
        )
        return AssetResult(
            candidates=candidates,
            keywords_used=keywords,
            design_brief=design_brief,
        )

    def process_style_reference(
        self,
        design_brief: Dict[str, Any],
        bg_bytes: bytes,
        count: int,
    ) -> AssetResult:
        """模式 2: 风格参考图 — 分析风格后搜索匹配的新背景"""
        keywords = design_brief.get("style_keywords", [])

        analysis = understand_image(
            image_data=bg_bytes,
            user_prompt=design_brief.get("user_prompt", ""),
        )
        understanding = analysis.get("understanding", {})
        suggestions = analysis.get("suggestions", {})

        # 将参考图分析结果注入 design_brief
        ref_style = understanding.get("style")
        ref_palette = understanding.get("color_palette", [])
        ref_mood = understanding.get("mood")
        ref_theme = understanding.get("theme")
        ref_desc = understanding.get("description")
        ref_layout = understanding.get("layout_hints", {})

        if ref_style and ref_style not in keywords:
            keywords = keywords + [ref_style]
            design_brief["style_keywords"] = keywords
        if ref_palette:
            design_brief["reference_palette"] = ref_palette
        if ref_mood and ref_mood != "其他":
            design_brief["reference_mood"] = ref_mood
        if ref_theme and ref_theme != "其他":
            design_brief["reference_theme"] = ref_theme
        if ref_desc:
            design_brief["reference_description"] = ref_desc
        if ref_layout:
            design_brief["reference_layout_hints"] = ref_layout
        if suggestions.get("color_scheme"):
            design_brief["reference_color_scheme"] = suggestions["color_scheme"]

        logger.info(
            f"🎨 参考图分析: style={ref_style}, mood={ref_mood}, "
            f"theme={ref_theme}, palette={ref_palette}"
        )

        candidates = search_assets_multiple(
            keywords=keywords,
            design_brief=design_brief,
            count=count,
        )

        # 构建背景分析结果
        image_analyses: List[Dict[str, Any]] = []
        color_suggestions: Optional[Dict[str, Any]] = None

        bg_analysis_entry: Dict[str, Any] = {"type": "background", "analysis": {}}
        if ref_desc:
            bg_analysis_entry["analysis"]["understanding"] = {
                "description": ref_desc,
                "theme": ref_theme,
                "mood": ref_mood,
                "layout_hints": ref_layout,
            }
            if ref_palette:
                color_suggestions = {
                    "primary": ref_palette[0] if ref_palette else None,
                    "palette": ref_palette,
                    "text_color": ref_layout.get("text_color_suggestion"),
                }
        image_analyses.append(bg_analysis_entry)

        return AssetResult(
            candidates=candidates,
            keywords_used=keywords,
            design_brief=design_brief,
            image_analyses=image_analyses,
            color_suggestions=color_suggestions,
        )

    def process_with_material(
        self,
        design_brief: Dict[str, Any],
        subject_bytes: bytes,
        bg_bytes: Optional[bytes],
        count: int,
        user_prompt: str,
    ) -> AssetResult:
        """模式 3: 主体素材 — 处理主体，可选背景"""
        keywords = design_brief.get("style_keywords", [])

        # 处理主体素材
        subject_url = image_to_base64(subject_bytes)
        dims = analyze_image(subject_bytes)
        subject_width = dims["width"]
        subject_height = dims["height"]
        logger.info(f"🧩 Material 模式：主体素材 {subject_width}×{subject_height}")

        subject_analysis = understand_image(
            image_data=subject_bytes,
            user_prompt=user_prompt,
        )
        logger.info(
            f"🔍 主体素材分析: {subject_analysis.get('understanding', {}).get('description', '?')[:60]}"
        )

        # 确定背景候选
        if bg_bytes:
            user_bg_url = image_to_base64(bg_bytes)
            logger.info("🖼️ Material 模式：使用用户上传的背景图")
            candidates = [user_bg_url]
        else:
            candidates = search_assets_multiple(
                keywords=keywords,
                design_brief=design_brief,
                count=count,
            )

        # 构建分析结果
        image_analyses: List[Dict[str, Any]] = [
            {"type": "subject", "analysis": subject_analysis}
        ]
        color_suggestions: Optional[Dict[str, Any]] = None
        understanding = subject_analysis.get("understanding", {})
        if understanding:
            color_suggestions = {
                "primary": understanding.get("main_color"),
                "palette": understanding.get("color_palette", []),
                "text_color": understanding.get("layout_hints", {}).get("text_color_suggestion"),
            }

        return AssetResult(
            candidates=candidates,
            keywords_used=keywords,
            design_brief=design_brief,
            image_analyses=image_analyses,
            color_suggestions=color_suggestions,
            subject_url=subject_url,
            subject_width=subject_width,
            subject_height=subject_height,
        )
