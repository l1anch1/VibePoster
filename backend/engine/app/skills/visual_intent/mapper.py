"""
视觉意图逆向映射器

将 VLM 图像分析结果映射到 KG Emotion 空间，实现参考图 → 设计意图的逆向推理。

三条映射路径：
1. mood/theme 直接映射到 Emotion（语义查表）
2. color_palette 与 KG Emotion palettes 做色彩距离匹配（LAB ΔE）
3. layout_hints 映射到 LayoutPattern，反向追溯 Emotion（图反向遍历）
"""

from typing import Dict, Any, List, Optional

from ...core.logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# 映射表：VLM 输出 → KG 节点
# ============================================================================

# VLM mood/theme 关键词 → KG Emotion（直接映射，高置信度）
MOOD_TO_EMOTION: Dict[str, str] = {
    # Trust
    "professional": "Trust", "reliable": "Trust", "corporate": "Trust",
    "stable": "Trust", "formal": "Trust", "trustworthy": "Trust",
    "专业": "Trust", "商务": "Trust", "正式": "Trust",
    # Innovation
    "innovative": "Innovation", "futuristic": "Innovation", "tech": "Innovation",
    "modern": "Innovation", "cutting-edge": "Innovation", "digital": "Innovation",
    "科技": "Innovation", "未来": "Innovation", "创新": "Innovation",
    # Excitement
    "energetic": "Excitement", "dynamic": "Excitement", "bold": "Excitement",
    "passionate": "Excitement", "intense": "Excitement", "vibrant": "Excitement",
    "活力": "Excitement", "热情": "Excitement", "动感": "Excitement",
    # Premium
    "luxury": "Premium", "elegant": "Premium", "high-end": "Premium",
    "sophisticated": "Premium", "refined": "Premium", "premium": "Premium",
    "奢华": "Premium", "高端": "Premium", "优雅": "Premium",
    # Warmth
    "warm": "Warmth", "friendly": "Warmth", "cozy": "Warmth",
    "inviting": "Warmth", "organic": "Warmth", "homely": "Warmth",
    "温暖": "Warmth", "亲切": "Warmth", "温馨": "Warmth",
    # Freshness
    "fresh": "Freshness", "natural": "Freshness", "healthy": "Freshness",
    "clean": "Freshness", "green": "Freshness", "pure": "Freshness",
    "清新": "Freshness", "自然": "Freshness", "健康": "Freshness",
    # Playfulness
    "playful": "Playfulness", "fun": "Playfulness", "creative": "Playfulness",
    "whimsical": "Playfulness", "colorful": "Playfulness", "youthful": "Playfulness",
    "趣味": "Playfulness", "童趣": "Playfulness", "创意": "Playfulness",
    # Serenity
    "calm": "Serenity", "peaceful": "Serenity", "serene": "Serenity",
    "tranquil": "Serenity", "zen": "Serenity", "minimal": "Serenity",
    "宁静": "Serenity", "平静": "Serenity", "禅意": "Serenity",
    # Urgency
    "urgent": "Urgency", "limited": "Urgency", "sale": "Urgency",
    "flash": "Urgency", "hurry": "Urgency", "countdown": "Urgency",
    "紧急": "Urgency", "限时": "Urgency", "抢购": "Urgency",
}

# VLM style（6 类） → KG Emotion
STYLE_TO_EMOTION: Dict[str, str] = {
    "business": "Trust",
    "campus": "Playfulness",
    "event": "Excitement",
    "product": "Premium",
    "festival": "Excitement",
}

# VLM layout position → KG LayoutPattern 节点名
POSITION_TO_PATTERN: Dict[str, str] = {
    "top": "Grid",
    "center": "Centered",
    "bottom": "Flowing",
}

# mood 直接映射的置信度
_MOOD_DIRECT_SCORE = 0.85
# style 映射的置信度
_STYLE_SCORE = 0.7
# layout 反向映射的置信度
_LAYOUT_REVERSE_SCORE = 0.5
# 色彩距离匹配的最高置信度
_COLOR_MAX_SCORE = 0.75


# ============================================================================
# 核心映射器
# ============================================================================

class VisualIntentMapper:
    """
    视觉意图逆向映射器

    将 VLM 分析结果（mood, theme, style, palette, layout_hints）映射到
    KG Emotion 空间的得分分布 {emotion_name: score}。

    这个映射不修改 KG，只是把视觉特征当作"查询条件"匹配已有节点。
    """

    def map_visual_to_emotions(
        self,
        understanding: Dict[str, Any],
        graph: Any = None,
    ) -> Dict[str, float]:
        """
        从 VLM 分析结果映射到 KG Emotion 空间

        Args:
            understanding: VLM 输出的 understanding 字典
                {mood, theme, style, description, elements, layout_hints, ...}
            graph: DesignGraph 实例（用于反向查询，可选）

        Returns:
            {emotion_name: score} 得分分布，score ∈ (0, 1]
        """
        emotions: Dict[str, float] = {}

        # 路径 1：mood/theme 直接映射（最高优先级）
        self._map_mood_theme(understanding, emotions)

        # 路径 2：style 映射
        self._map_style(understanding, emotions)

        # 路径 3：layout hints 反向映射（需要 graph）
        if graph is not None:
            self._map_layout_reverse(understanding, graph, emotions)

        if emotions:
            logger.info(
                f"视觉意图映射: {dict(sorted(emotions.items(), key=lambda x: -x[1]))}"
            )
        return emotions

    def _map_mood_theme(
        self, understanding: Dict[str, Any], emotions: Dict[str, float]
    ) -> None:
        """路径 1：mood 和 theme 直接映射到 Emotion"""
        for field in ("mood", "theme"):
            value = understanding.get(field, "")
            if not value or value == "其他" or value == "other":
                continue
            # 支持逗号分隔的多关键词
            for keyword in str(value).lower().replace("、", ",").split(","):
                keyword = keyword.strip()
                emotion = MOOD_TO_EMOTION.get(keyword)
                if emotion:
                    emotions[emotion] = max(
                        emotions.get(emotion, 0), _MOOD_DIRECT_SCORE
                    )

    def _map_style(
        self, understanding: Dict[str, Any], emotions: Dict[str, float]
    ) -> None:
        """路径 2：VLM style 映射到 Emotion"""
        style = understanding.get("style", "")
        if style and style != "other":
            emotion = STYLE_TO_EMOTION.get(style.lower())
            if emotion:
                emotions[emotion] = max(emotions.get(emotion, 0), _STYLE_SCORE)

    def _map_layout_reverse(
        self, understanding: Dict[str, Any], graph: Any,
        emotions: Dict[str, float],
    ) -> None:
        """路径 3：layout hints → LayoutPattern → 反向查 Emotion"""
        layout_hints = understanding.get("layout_hints", {})
        if not layout_hints:
            return
        text_pos = layout_hints.get("text_position", "")
        if not text_pos:
            return
        pattern = POSITION_TO_PATTERN.get(text_pos.lower())
        if not pattern:
            return
        # 反向查询：哪些 Emotion EVOKES 了这个 LayoutPattern
        if hasattr(graph, "get_emotions_that_evoke"):
            reverse_hits = graph.get_emotions_that_evoke(pattern)
            for hit in reverse_hits:
                emo = hit["source"]
                score = hit["weight"] * _LAYOUT_REVERSE_SCORE
                emotions[emo] = max(emotions.get(emo, 0), score)
