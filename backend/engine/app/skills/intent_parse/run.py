"""
IntentParseSkill 执行逻辑

核心知识（关键词映射表、品牌列表、置信度公式）
记录在 skill.md 中，本文件只负责执行。
"""

import re
from typing import Dict, List, Optional, Tuple

from ..base import BaseSkill, SkillResult
from ..types import IntentParseInput, IntentParseOutput
from ...core.logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# 关键词映射表（与 skill.md 保持一致）
# ============================================================================

INDUSTRY_KEYWORDS: Dict[str, str] = {
    "科技": "Tech", "tech": "Tech", "数码": "Tech", "互联网": "Tech",
    "ai": "Tech", "人工智能": "Tech", "软件": "Tech", "it": "Tech",
    "电子": "Tech", "智能": "Tech", "云": "Tech", "大数据": "Tech",
    "software": "Tech", "digital": "Tech", "startup": "Tech", "saas": "Tech",
    "食品": "Food", "food": "Food", "美食": "Food", "餐饮": "Food",
    "餐厅": "Food", "饮料": "Food", "咖啡": "Food", "茶": "Food",
    "烘焙": "Food", "甜品": "Food",
    "restaurant": "Food", "coffee": "Food", "bakery": "Food", "drink": "Food",
    "奢侈": "Luxury", "luxury": "Luxury", "高端": "Luxury", "豪华": "Luxury",
    "尊贵": "Luxury", "顶级": "Luxury", "奢华": "Luxury",
    "premium": "Luxury", "exclusive": "Luxury",
    "医疗": "Healthcare", "healthcare": "Healthcare", "健康": "Healthcare",
    "医院": "Healthcare", "诊所": "Healthcare", "养生": "Healthcare",
    "保健": "Healthcare", "医药": "Healthcare",
    "health": "Healthcare", "medical": "Healthcare", "wellness": "Healthcare",
    "教育": "Education", "education": "Education", "培训": "Education",
    "学校": "Education", "课程": "Education", "学习": "Education",
    "考试": "Education", "留学": "Education",
    "school": "Education", "course": "Education", "training": "Education", "learn": "Education",
    "娱乐": "Entertainment", "entertainment": "Entertainment", "游戏": "Entertainment",
    "电影": "Entertainment", "音乐": "Entertainment", "演出": "Entertainment",
    "演唱会": "Entertainment", "综艺": "Entertainment",
    "music": "Entertainment", "movie": "Entertainment", "film": "Entertainment",
    "concert": "Entertainment", "festival": "Entertainment", "party": "Entertainment",
    "game": "Entertainment", "show": "Entertainment", "dj": "Entertainment",
    "金融": "Finance", "finance": "Finance", "银行": "Finance",
    "理财": "Finance", "投资": "Finance", "保险": "Finance",
    "基金": "Finance", "股票": "Finance",
    "bank": "Finance", "invest": "Finance", "insurance": "Finance", "crypto": "Finance",
    "美妆": "Beauty", "beauty": "Beauty", "护肤": "Beauty", "化妆品": "Beauty",
    "个护": "Beauty", "skincare": "Beauty", "cosmetics": "Beauty", "makeup": "Beauty",
    "时尚": "Beauty", "fashion": "Beauty", "服装": "Beauty", "穿搭": "Beauty",
    "潮流": "Beauty", "服饰": "Beauty",
    "clothing": "Beauty", "style": "Beauty",
}

VIBE_KEYWORDS: Dict[str, str] = {
    "极简": "Minimalist", "minimalist": "Minimalist", "简约": "Minimalist",
    "简洁": "Minimalist", "留白": "Minimalist", "素雅": "Minimalist",
    "minimal": "Minimalist", "clean": "Minimalist", "simple": "Minimalist",
    "活力": "Energetic", "energetic": "Energetic", "动感": "Energetic",
    "活泼": "Energetic", "青春": "Energetic", "热情": "Energetic",
    "vibrant": "Energetic", "dynamic": "Energetic", "lively": "Energetic",
    "专业": "Professional", "professional": "Professional", "商务": "Professional",
    "正式": "Professional", "企业": "Professional", "严肃": "Professional",
    "corporate": "Professional", "business": "Professional", "formal": "Professional",
    "友好": "Friendly", "friendly": "Friendly", "亲切": "Friendly",
    "温馨": "Friendly", "可爱": "Friendly", "萌": "Friendly",
    "cute": "Friendly", "warm": "Friendly", "cozy": "Friendly",
    "大胆": "Bold", "bold": "Bold", "醒目": "Bold", "冲击": "Bold",
    "强烈": "Bold", "张扬": "Bold",
    "neon": "Bold", "loud": "Bold", "striking": "Bold", "punk": "Bold",
    "复古": "Retro", "vintage": "Retro", "怀旧": "Retro", "经典": "Retro",
    "老式": "Retro", "古典": "Retro",
    "retro": "Retro", "classic": "Retro", "nostalgic": "Retro",
    "现代": "Futuristic", "modern": "Futuristic", "当代": "Futuristic", "前卫": "Futuristic",
    "未来": "Futuristic", "科幻": "Futuristic",
    "futuristic": "Futuristic", "contemporary": "Futuristic", "sleek": "Futuristic",
    "cyberpunk": "Futuristic", "sci-fi": "Futuristic",
}

POSTER_TYPE_KEYWORDS: Dict[str, str] = {
    "促销": "promotion", "打折": "promotion", "优惠": "promotion",
    "特价": "promotion", "折扣": "promotion", "大促": "promotion",
    "宣传": "promotion", "推广": "promotion", "广告": "promotion",
    "sale": "promotion", "discount": "promotion", "promo": "promotion", "deal": "promotion",
    "邀请": "invitation", "请柬": "invitation", "邀请函": "invitation",
    "invite": "invitation", "invitation": "invitation", "rsvp": "invitation",
    "公告": "announcement", "通知": "announcement", "声明": "announcement",
    "告示": "announcement",
    "announcement": "announcement", "notice": "announcement",
    "活动": "event", "发布会": "event", "展会": "event", "峰会": "event",
    "论坛": "event", "晚会": "event", "年会": "event",
    "event": "event", "conference": "event", "summit": "event",
    "festival": "event", "launch": "event", "meetup": "event",
    "封面": "cover", "banner": "cover", "横幅": "cover",
    "cover": "cover", "header": "cover",
}

KNOWN_BRANDS: List[str] = [
    "苹果", "Apple", "华为", "Huawei", "小米", "Xiaomi", "OPPO", "vivo",
    "腾讯", "Tencent", "阿里", "阿里巴巴", "Alibaba", "百度", "Baidu",
    "京东", "JD", "美团", "Meituan", "字节跳动", "ByteDance", "抖音", "TikTok",
    "Nike", "耐克", "Adidas", "阿迪达斯", "星巴克", "Starbucks",
    "麦当劳", "McDonald", "肯德基", "KFC", "可口可乐", "Coca-Cola",
    "奔驰", "Mercedes", "宝马", "BMW", "奥迪", "Audi", "特斯拉", "Tesla",
]


class IntentParseSkill(BaseSkill[IntentParseInput, IntentParseOutput]):
    """
    意图解析技能

    使用规则匹配 + 启发式方法从用户输入中提取结构化意图。
    完整的关键词映射表和算法说明见 skill.md。
    """

    def __init__(self, use_llm: bool = False, llm_client=None):
        super().__init__()
        self._use_llm = use_llm
        self._llm_client = llm_client

    def run(self, input: IntentParseInput) -> SkillResult[IntentParseOutput]:
        user_prompt = input.user_prompt
        logger.info(f"🕵️ 解析用户意图: {user_prompt[:50]}...")

        industry, industry_conf = self._extract_industry(user_prompt)
        vibe, vibe_conf = self._extract_vibe(user_prompt)
        poster_type = self._extract_poster_type(user_prompt)
        brand_name = self._extract_brand(user_prompt)
        key_elements = self._extract_key_elements(user_prompt)

        extracted_keywords = []
        if industry:
            extracted_keywords.append(industry)
        if vibe:
            extracted_keywords.append(vibe)

        confidence = self._calculate_confidence(industry_conf, vibe_conf, bool(brand_name))

        output = IntentParseOutput(
            industry=industry,
            vibe=vibe,
            poster_type=poster_type,
            brand_name=brand_name,
            key_elements=key_elements,
            extracted_keywords=extracted_keywords,
            confidence=confidence,
        )

        logger.info(
            f"✅ 意图解析完成: industry={industry}, vibe={vibe}, "
            f"type={poster_type}, brand={brand_name}, confidence={confidence:.2f}"
        )
        return SkillResult.success(output, method="rule_based")

    # ------------------------------------------------------------------
    # 私有方法
    # ------------------------------------------------------------------

    def _extract_industry(self, text: str) -> Tuple[Optional[str], float]:
        text_lower = text.lower()
        for keyword, industry in INDUSTRY_KEYWORDS.items():
            if keyword.lower() in text_lower:
                confidence = 0.9 if keyword in text else 0.8
                return industry, confidence
        return None, 0.0

    def _extract_vibe(self, text: str) -> Tuple[Optional[str], float]:
        text_lower = text.lower()
        for keyword, vibe in VIBE_KEYWORDS.items():
            if keyword.lower() in text_lower:
                confidence = 0.9 if keyword in text else 0.8
                return vibe, confidence
        return None, 0.0

    def _extract_poster_type(self, text: str) -> str:
        text_lower = text.lower()
        for keyword, poster_type in POSTER_TYPE_KEYWORDS.items():
            if keyword.lower() in text_lower:
                return poster_type
        return "promotion"

    def _extract_brand(self, text: str) -> Optional[str]:
        for brand in KNOWN_BRANDS:
            if brand.lower() in text.lower():
                return brand
        quoted_pattern = r'[""「」『』【】]([^""「」『』【】]+)[""「」『』【】]'
        matches = re.findall(quoted_pattern, text)
        for match in matches:
            if len(match) <= 10 and not any(k in match for k in ["海报", "设计", "风格"]):
                return match
        return None

    def _extract_key_elements(self, text: str) -> List[str]:
        elements = []
        time_patterns = [
            r'\d{4}年', r'\d{1,2}月\d{1,2}[日号]', r'周[一二三四五六日末]',
            r'[上下]午', r'\d{1,2}[:\：]\d{2}',
        ]
        for pattern in time_patterns:
            elements.extend(re.findall(pattern, text))
        number_patterns = [r'\d+折', r'\d+%', r'[¥￥]\d+', r'\d+元']
        for pattern in number_patterns:
            elements.extend(re.findall(pattern, text))
        theme_keywords = ["发布会", "展览", "演唱会", "招聘", "开业", "周年"]
        for kw in theme_keywords:
            if kw in text:
                elements.append(kw)
        return list(set(elements))

    def _calculate_confidence(
        self, industry_conf: float, vibe_conf: float, has_brand: bool
    ) -> float:
        base = 0.5
        if industry_conf > 0:
            base += 0.2 * industry_conf
        if vibe_conf > 0:
            base += 0.2 * vibe_conf
        if has_brand:
            base += 0.1
        return min(base, 1.0)
