# Intent Parse Skill

## 概述

意图解析是 Planner 流程的第一步。接收用户的自然语言描述，通过**关键词规则匹配 + 启发式方法**提取结构化意图。

输出字段：
- `industry`: 行业领域（与 KG 节点对齐，如 Tech, Food, Luxury）
- `vibe`: 设计风格（与 KG 节点对齐，如 Minimalist, Energetic）
- `poster_type`: 海报类型（promotion, invitation, announcement, cover, event, other）
- `brand_name`: 品牌名称（从已知品牌表或引号中识别）
- `key_elements`: 关键元素（时间、价格、主题词等）
- `extracted_keywords`: 供 KG 推理使用的关键词集合
- `confidence`: 综合置信度 (0.0 ~ 1.0)

## Industry Keywords

中文关键词 → KG Industry 节点的映射：

| 关键词 | Industry |
|--------|----------|
| 科技, tech, 数码, 互联网, ai, 人工智能, 软件, it, 电子, 智能, 云, 大数据 | Tech |
| 食品, food, 美食, 餐饮, 餐厅, 饮料, 咖啡, 茶, 烘焙, 甜品 | Food |
| 奢侈, luxury, 高端, 豪华, 尊贵, 顶级, 奢华 | Luxury |
| 医疗, healthcare, 健康, 医院, 诊所, 养生, 保健, 医药 | Healthcare |
| 教育, education, 培训, 学校, 课程, 学习, 考试, 留学 | Education |
| 娱乐, entertainment, 游戏, 电影, 音乐, 演出, 演唱会, 综艺 | Entertainment |
| 金融, finance, 银行, 理财, 投资, 保险, 基金, 股票 | Finance |
| 旅游, travel, 旅行, 景点, 酒店, 民宿, 度假 | Travel |
| 时尚, fashion, 服装, 穿搭, 潮流, 服饰, 美妆 | Fashion |
| 房地产, 地产, 楼盘, 房产, 置业, 公寓 | Real Estate |

## Vibe Keywords

| 关键词 | Vibe |
|--------|------|
| 极简, minimalist, 简约, 简洁, 留白, 素雅 | Minimalist |
| 活力, energetic, 动感, 活泼, 青春, 热情 | Energetic |
| 专业, professional, 商务, 正式, 企业, 严肃 | Professional |
| 友好, friendly, 亲切, 温馨, 可爱, 萌 | Friendly |
| 大胆, bold, 醒目, 冲击, 强烈, 张扬 | Bold |
| 复古, vintage, 怀旧, 经典, 老式, 古典 | Vintage |
| 现代, modern, 当代, 前卫, 未来, 科幻 | Modern |
| 自然, natural, 环保, 绿色, 有机, 生态 | Natural |

## Poster Type Keywords

| 关键词 | PosterType |
|--------|------------|
| 促销, 打折, 优惠, 特价, 折扣, 大促, 宣传, 推广, 广告 | promotion |
| 邀请, 请柬, 邀请函 | invitation |
| 公告, 通知, 声明, 告示 | announcement |
| 活动, 发布会, 展会, 峰会, 论坛, 晚会, 年会 | event |
| 封面, banner, 横幅 | cover |

## Known Brands

苹果, Apple, 华为, Huawei, 小米, Xiaomi, OPPO, vivo,
腾讯, Tencent, 阿里, 阿里巴巴, Alibaba, 百度, Baidu,
京东, JD, 美团, Meituan, 字节跳动, ByteDance, 抖音, TikTok,
Nike, 耐克, Adidas, 阿迪达斯, 星巴克, Starbucks,
麦当劳, McDonald, 肯德基, KFC, 可口可乐, Coca-Cola,
奔驰, Mercedes, 宝马, BMW, 奥迪, Audi, 特斯拉, Tesla

## 置信度计算

```
base_score = 0.5
if industry_matched:  base_score += 0.2 × confidence
if vibe_matched:      base_score += 0.2 × confidence
if brand_found:       base_score += 0.1
final = min(base_score, 1.0)
```

## Examples

**输入**: "帮我做一个苹果发布会的科技风海报"
**输出**:
```json
{
  "industry": "Tech",
  "vibe": "Minimalist",
  "poster_type": "event",
  "brand_name": "苹果",
  "key_elements": ["发布会"],
  "extracted_keywords": ["Tech", "Minimalist"],
  "confidence": 0.95
}
```

**输入**: "圣诞节餐厅促销海报，温馨风格"
**输出**:
```json
{
  "industry": "Food",
  "vibe": "Friendly",
  "poster_type": "promotion",
  "brand_name": null,
  "key_elements": [],
  "extracted_keywords": ["Food", "Friendly"],
  "confidence": 0.86
}
```
