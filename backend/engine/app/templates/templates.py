"""
预定义的风格模板

包含5种主流海报风格：
1. Business（商务）
2. Campus（校园）
3. Event（活动）
4. Product（产品推广）
5. Festival（节日）
"""

from .models import (
    StyleTemplate,
    ColorScheme,
    FontRecommendation,
    LayoutRule,
    StylePreference,
)


# =============================================================================
# 1. Business（商务风格）
# =============================================================================

BUSINESS_TEMPLATE = StyleTemplate(
    id="business",
    name="business",
    display_name="商务风格",
    description="专业、简洁、现代的商务风格，适合企业宣传、会议、培训等商务场景",
    color_schemes=[
        ColorScheme(
            name="专业蓝",
            primary="#2C3E50",  # 深蓝灰
            secondary="#3498DB",  # 明亮蓝
            accent="#E74C3C",  # 红色强调
            background="#FFFFFF",  # 白色背景
            text_primary="#2C3E50",  # 深色文字
            text_secondary="#7F8C8D",  # 灰色文字
            description="专业、可信赖的蓝色系配色",
        ),
        ColorScheme(
            name="精英黑",
            primary="#1A1A1A",  # 深黑
            secondary="#FFD700",  # 金色
            accent="#C0C0C0",  # 银色
            background="#F5F5F5",  # 浅灰背景
            text_primary="#1A1A1A",  # 黑色文字
            text_secondary="#666666",  # 深灰文字
            description="高端、精英的黑金配色",
        ),
    ],
    font_recommendation=FontRecommendation(
        title_fonts=["Source Han Sans CN", "Microsoft YaHei", "Arial", "Helvetica"],
        body_fonts=["Source Han Sans CN", "Microsoft YaHei", "Arial"],
        font_size_range={
            "title": {"min": 48, "max": 72},
            "subtitle": {"min": 28, "max": 40},
            "body": {"min": 18, "max": 24},
        },
        font_weight={"title": "bold", "subtitle": "medium", "body": "normal"},
    ),
    layout_rule=LayoutRule(
        alignment="left",
        spacing={"title_to_subtitle": 24, "text_padding": 40, "line_height": 1.5},
        element_distribution="balanced",
        text_area_ratio=0.4,
        image_area_ratio=0.5,
        preferred_positions={
            "title": "top_left",
            "subtitle": "below_title",
            "image": "right",
            "logo": "top_right",
        },
    ),
    style_preference=StylePreference(
        keywords=["专业", "简洁", "现代", "可信赖", "高效"],
        mood="professional",
        target_audience="business professionals, corporate clients",
        design_principles=[
            "简洁明了，避免过多装饰",
            "使用网格系统确保对齐",
            "留白充足，信息层次清晰",
            "色彩克制，以蓝色、灰色为主",
            "字体规范，易于阅读",
        ],
        avoid_elements=["卡通元素", "过于鲜艳的颜色", "花哨的装饰", "非正式的字体"],
        recommended_elements=["几何图形", "图表", "数据可视化", "企业Logo", "专业摄影"],
    ),
    use_cases=[
        "企业宣传",
        "商务会议",
        "培训讲座",
        "招聘海报",
        "企业年报",
        "产品发布会",
        "B2B营销",
    ],
    example_prompts=[
        "2024年度企业峰会",
        "新产品发布会",
        "人才招聘季",
        "企业培训通知",
    ],
)


# =============================================================================
# 2. Campus（校园风格）
# =============================================================================

CAMPUS_TEMPLATE = StyleTemplate(
    id="campus",
    name="campus",
    display_name="校园风格",
    description="活泼、年轻、充满活力的校园风格，适合学生活动、社团招新、校园通知等场景",
    color_schemes=[
        ColorScheme(
            name="青春活力",
            primary="#FF6B9D",  # 粉红
            secondary="#4ECDC4",  # 青色
            accent="#FFE66D",  # 黄色
            background="#FFF8F0",  # 米白色背景
            text_primary="#2C3E50",  # 深色文字
            text_secondary="#95A5A6",  # 灰色文字
            description="活泼、充满活力的多彩配色",
        ),
        ColorScheme(
            name="清新校园",
            primary="#5DADE2",  # 天蓝
            secondary="#52BE80",  # 绿色
            accent="#F39C12",  # 橙色
            background="#FFFFFF",  # 白色背景
            text_primary="#34495E",  # 深灰文字
            text_secondary="#7F8C8D",  # 灰色文字
            description="清新、自然的校园配色",
        ),
    ],
    font_recommendation=FontRecommendation(
        title_fonts=["Source Han Sans CN", "Microsoft YaHei", "PingFang SC", "STHeiti"],
        body_fonts=["Source Han Sans CN", "Microsoft YaHei", "PingFang SC"],
        font_size_range={
            "title": {"min": 56, "max": 84},
            "subtitle": {"min": 32, "max": 48},
            "body": {"min": 20, "max": 28},
        },
        font_weight={"title": "heavy", "subtitle": "bold", "body": "normal"},
    ),
    layout_rule=LayoutRule(
        alignment="center",
        spacing={"title_to_subtitle": 20, "text_padding": 30, "line_height": 1.6},
        element_distribution="top_heavy",
        text_area_ratio=0.45,
        image_area_ratio=0.45,
        preferred_positions={
            "title": "top_center",
            "subtitle": "below_title",
            "image": "center_bottom",
            "decorative": "corners",
        },
    ),
    style_preference=StylePreference(
        keywords=["活泼", "年轻", "充满活力", "创意", "友好"],
        mood="energetic",
        target_audience="students, young people",
        design_principles=[
            "色彩鲜明，充满活力",
            "字体可适当夸张，增强表现力",
            "可使用插画、手绘元素",
            "布局灵活，不必过于拘泥",
            "突出活动亮点和趣味性",
        ],
        avoid_elements=["过于严肃的设计", "单调的配色", "过小的字体"],
        recommended_elements=["插画", "图标", "几何装饰", "手写字体", "贴纸元素", "波浪线"],
    ),
    use_cases=[
        "社团招新",
        "校园活动",
        "讲座通知",
        "运动会",
        "文艺演出",
        "学生会选举",
        "社团聚会",
    ],
    example_prompts=[
        "社团招新季来啦",
        "校园歌手大赛",
        "篮球赛总决赛",
        "社团迎新晚会",
    ],
)


# =============================================================================
# 3. Event（活动风格）
# =============================================================================

EVENT_TEMPLATE = StyleTemplate(
    id="event",
    name="event",
    display_name="活动风格",
    description="醒目、动感、吸引注意力的活动风格，适合音乐会、展览、派对、促销活动等",
    color_schemes=[
        ColorScheme(
            name="动感红",
            primary="#E74C3C",  # 鲜红
            secondary="#F39C12",  # 橙色
            accent="#FFFFFF",  # 白色强调
            background="#1A1A1A",  # 深色背景
            text_primary="#FFFFFF",  # 白色文字
            text_secondary="#ECF0F1",  # 浅灰文字
            description="充满激情和能量的红色系",
        ),
        ColorScheme(
            name="霓虹夜",
            primary="#9B59B6",  # 紫色
            secondary="#E91E63",  # 粉红
            accent="#00BCD4",  # 青色
            background="#000000",  # 黑色背景
            text_primary="#FFFFFF",  # 白色文字
            text_secondary="#BDBDBD",  # 灰色文字
            description="神秘、时尚的霓虹配色",
        ),
    ],
    font_recommendation=FontRecommendation(
        title_fonts=["Impact", "Source Han Sans CN", "Arial Black", "Microsoft YaHei"],
        body_fonts=["Source Han Sans CN", "Microsoft YaHei", "Arial"],
        font_size_range={
            "title": {"min": 64, "max": 96},
            "subtitle": {"min": 36, "max": 52},
            "body": {"min": 22, "max": 30},
        },
        font_weight={"title": "black", "subtitle": "bold", "body": "medium"},
    ),
    layout_rule=LayoutRule(
        alignment="center",
        spacing={"title_to_subtitle": 16, "text_padding": 25, "line_height": 1.4},
        element_distribution="balanced",
        text_area_ratio=0.35,
        image_area_ratio=0.55,
        preferred_positions={
            "title": "center",
            "subtitle": "below_title",
            "image": "full_background",
            "info": "bottom",
        },
    ),
    style_preference=StylePreference(
        keywords=["醒目", "动感", "激情", "吸引注意", "时尚"],
        mood="exciting",
        target_audience="event attendees, general public",
        design_principles=[
            "大胆使用对比色",
            "标题要够大够醒目",
            "可使用倾斜、错位等动感设计",
            "背景可使用大图或渐变",
            "突出时间、地点等关键信息",
        ],
        avoid_elements=["过于素雅的设计", "小字体", "过多文字"],
        recommended_elements=["大字体", "渐变", "光效", "几何图形", "动态线条", "大图背景"],
    ),
    use_cases=[
        "音乐会",
        "演唱会",
        "艺术展览",
        "派对活动",
        "促销活动",
        "新品发布",
        "体育赛事",
    ],
    example_prompts=[
        "摇滚音乐节",
        "年终大促销",
        "艺术展览开幕",
        "电音派对",
    ],
)


# =============================================================================
# 4. Product（产品推广风格）
# =============================================================================

PRODUCT_TEMPLATE = StyleTemplate(
    id="product",
    name="product",
    display_name="产品推广",
    description="突出产品、清晰、有说服力的推广风格，适合产品广告、电商促销、品牌宣传等",
    color_schemes=[
        ColorScheme(
            name="现代简约",
            primary="#000000",  # 黑色
            secondary="#FFFFFF",  # 白色
            accent="#FF4444",  # 红色强调
            background="#F8F8F8",  # 浅灰背景
            text_primary="#000000",  # 黑色文字
            text_secondary="#666666",  # 灰色文字
            description="简约、高端的黑白配色",
        ),
        ColorScheme(
            name="科技蓝",
            primary="#0066FF",  # 科技蓝
            secondary="#00CCFF",  # 浅蓝
            accent="#FFFFFF",  # 白色
            background="#FFFFFF",  # 白色背景
            text_primary="#1A1A1A",  # 深色文字
            text_secondary="#666666",  # 灰色文字
            description="科技感十足的蓝色系",
        ),
    ],
    font_recommendation=FontRecommendation(
        title_fonts=["Source Han Sans CN", "Microsoft YaHei", "Helvetica", "Arial"],
        body_fonts=["Source Han Sans CN", "Microsoft YaHei", "Arial"],
        font_size_range={
            "title": {"min": 52, "max": 80},
            "subtitle": {"min": 30, "max": 44},
            "body": {"min": 18, "max": 26},
        },
        font_weight={"title": "bold", "subtitle": "medium", "body": "normal"},
    ),
    layout_rule=LayoutRule(
        alignment="center",
        spacing={"title_to_subtitle": 20, "text_padding": 35, "line_height": 1.5},
        element_distribution="balanced",
        text_area_ratio=0.3,
        image_area_ratio=0.6,
        preferred_positions={
            "title": "top",
            "product": "center",
            "features": "bottom",
            "cta": "bottom_center",
        },
    ),
    style_preference=StylePreference(
        keywords=["突出产品", "清晰", "有说服力", "高端", "吸引购买"],
        mood="persuasive",
        target_audience="consumers, potential buyers",
        design_principles=[
            "产品图片要清晰、高质量",
            "突出产品特点和卖点",
            "使用简洁有力的文案",
            "留白充足，聚焦产品",
            "包含明确的行动号召（CTA）",
        ],
        avoid_elements=["杂乱的背景", "过多文字", "低质量图片", "不相关的装饰"],
        recommended_elements=["产品高清图", "特性图标", "价格标签", "促销徽章", "简洁背景"],
    ),
    use_cases=[
        "产品广告",
        "电商促销",
        "新品发布",
        "品牌宣传",
        "产品介绍",
        "限时优惠",
        "特价促销",
    ],
    example_prompts=[
        "新款手机震撼上市",
        "618年中大促",
        "限时特价优惠",
        "旗舰产品发布",
    ],
)


# =============================================================================
# 5. Festival（节日风格）
# =============================================================================

FESTIVAL_TEMPLATE = StyleTemplate(
    id="festival",
    name="festival",
    display_name="节日风格",
    description="喜庆、温馨、充满节日氛围的风格，适合春节、中秋、圣诞等节日宣传",
    color_schemes=[
        ColorScheme(
            name="中国红",
            primary="#DC143C",  # 中国红
            secondary="#FFD700",  # 金色
            accent="#FFEB3B",  # 黄色
            background="#FFF8E1",  # 米黄背景
            text_primary="#8B0000",  # 深红文字
            text_secondary="#D32F2F",  # 红色文字
            description="喜庆、热闹的中国传统配色",
        ),
        ColorScheme(
            name="圣诞绿",
            primary="#165E3F",  # 深绿
            secondary="#C41E3A",  # 圣诞红
            accent="#FFD700",  # 金色
            background="#F5F5DC",  # 米色背景
            text_primary="#1A1A1A",  # 深色文字
            text_secondary="#4A4A4A",  # 灰色文字
            description="温馨、节日感的圣诞配色",
        ),
    ],
    font_recommendation=FontRecommendation(
        title_fonts=["Source Han Serif CN", "STKaiti", "Microsoft YaHei", "SimSun"],
        body_fonts=["Source Han Sans CN", "Microsoft YaHei", "SimHei"],
        font_size_range={
            "title": {"min": 60, "max": 90},
            "subtitle": {"min": 34, "max": 50},
            "body": {"min": 20, "max": 28},
        },
        font_weight={"title": "heavy", "subtitle": "bold", "body": "normal"},
    ),
    layout_rule=LayoutRule(
        alignment="center",
        spacing={"title_to_subtitle": 18, "text_padding": 28, "line_height": 1.6},
        element_distribution="balanced",
        text_area_ratio=0.4,
        image_area_ratio=0.5,
        preferred_positions={
            "title": "center",
            "subtitle": "below_title",
            "image": "background",
            "decorative": "all_around",
        },
    ),
    style_preference=StylePreference(
        keywords=["喜庆", "温馨", "节日氛围", "团圆", "祝福"],
        mood="festive",
        target_audience="general public, families",
        design_principles=[
            "使用节日相关的配色和元素",
            "营造温馨、喜庆的氛围",
            "可使用传统纹样和装饰",
            "文字表达祝福和节日主题",
            "整体设计要有节日感",
        ],
        avoid_elements=["冷色调", "严肃的设计", "商务化元素"],
        recommended_elements=[
            "节日元素（灯笼、烟花、雪花等）",
            "传统纹样",
            "祝福语",
            "节日食品",
            "装饰边框",
        ],
    ),
    use_cases=[
        "春节祝福",
        "中秋节",
        "圣诞节",
        "元旦",
        "国庆节",
        "情人节",
        "端午节",
    ],
    example_prompts=[
        "春节快乐，龙年大吉",
        "中秋团圆，月满人圆",
        "圣诞狂欢夜",
        "元旦新年快乐",
    ],
)


# =============================================================================
# 模板集合
# =============================================================================

STYLE_TEMPLATES = {
    "business": BUSINESS_TEMPLATE,
    "campus": CAMPUS_TEMPLATE,
    "event": EVENT_TEMPLATE,
    "product": PRODUCT_TEMPLATE,
    "festival": FESTIVAL_TEMPLATE,
}

# 默认模板
DEFAULT_TEMPLATE_ID = "business"

