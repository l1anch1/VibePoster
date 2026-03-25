# Knowledge Module v2 - 语义化设计知识推理

## 📚 模块说明

本模块提供两个核心功能：

```
knowledge/
├── __init__.py
├── README.md
├── kg/                      # Knowledge Graph v2
│   ├── __init__.py
│   ├── types.py             # Pydantic 类型定义
│   ├── loader.py            # 规则数据加载
│   ├── graph.py             # 图结构管理
│   ├── inference.py         # 推理引擎
│   ├── knowledge_graph.py   # 组合入口
│   └── data/
│       └── kg_rules.json    # 语义化设计规则
│
└── rag/                     # RAG 品牌知识检索
    ├── __init__.py
    ├── types.py             # Pydantic 类型定义
    ├── embedder.py          # 嵌入计算
    ├── retriever.py         # 检索策略
    ├── loader.py            # 数据加载
    ├── knowledge_base.py    # 组合入口
    └── data/
        └── default_brand_knowledge.json
```

---

## 1. Knowledge Graph v2 - 语义化推理链

**核心创新：Industry/Vibe → Emotion → Visual Elements**

不再简单地从行业映射到颜色，而是通过情绪层进行语义推理：

```
Tech ──embodies──► Trust ──► 配色策略、排版、布局
     ──embodies──► Innovation
```

### 使用示例

```python
from app.knowledge import DesignKnowledgeGraph

kg = DesignKnowledgeGraph()
result = kg.infer_rules(["Tech", "Minimalist"])

# 结果结构：
{
    "emotions": ["Trust", "Innovation", "Premium"],
    
    "color_strategies": ["Monochromatic", "Triadic", "Split-Complementary"],
    "color_palettes": {
        "primary": ["#0066CC", "#6366F1", "#1A1A1A"],
        "accent": ["#D4AF37", "#22D3EE"],
        "gradient": ["linear-gradient(135deg, #667eea 0%, #764ba2 100%)"]
    },
    
    "typography_styles": ["Sans-Serif", "Serif"],
    "typography_weights": ["Medium", "Bold", "Light"],
    "typography_characteristics": ["Clean", "Modern", "Elegant"],
    
    "layout_strategies": ["Structured", "Dynamic", "Minimal"],
    "layout_intents": ["Stability", "Forward-thinking", "Sophistication"],
    "layout_patterns": ["Grid", "Diagonal", "Golden-ratio"],
    
    "design_principles": ["Clean interfaces", "Scalable design system"],
    "avoid": ["Warm earth tones", "Script fonts", "Overly decorative"]
}
```

### 情绪语义层

| Emotion | 描述 | 典型配色策略 | 典型布局意图 |
|---------|------|-------------|-------------|
| Trust | 可靠、稳定 | Monochromatic | Stability |
| Innovation | 前沿、科技感 | Triadic | Forward-thinking |
| Premium | 奢华、高端 | Neutral-with-Accent | Sophistication |
| Excitement | 活力、热情 | Complementary | Dynamism |
| Warmth | 温暖、亲切 | Earth-tones | Comfort |
| Freshness | 新鲜、健康 | Nature-inspired | Clarity |
| Playfulness | 趣味、创意 | Multi-color | Engagement |

### 支持的关键词

```python
kg.get_supported_keywords()
# {
#     "industries": ["Tech", "Food", "Luxury", "Healthcare", "Education", "Entertainment"],
#     "vibes": ["Minimalist", "Energetic", "Professional", "Friendly", "Bold"],
#     "emotions": ["Trust", "Innovation", "Premium", "Excitement", "Warmth", "Freshness", "Playfulness"]
# }
```

---

## 2. RAG 品牌知识检索

### 使用示例

```python
from app.knowledge import BrandKnowledgeBase

kb = BrandKnowledgeBase()
results = kb.search("华为的配色", top_k=2)
# [
#     {
#         "text": "华为 Mate 60 的品牌主色调是昆仑红 (#C32228)...",
#         "metadata": {"brand": "华为", "category": "配色方案"},
#         "score": 0.95
#     }
# ]
```

### 检索后端

| 后端 | 准确率 | 速度 | 依赖 |
|-----|--------|------|------|
| sentence-transformers | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 轻量 |
| chromadb | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 中等 |
| keyword | ⭐⭐⭐ | ⭐⭐⭐ | 无 |

---

## 🎯 集成方式

通过 Skills 模块访问知识：

```python
from app.skills import DesignRuleSkill, DesignRuleInput
from app.skills import BrandContextSkill, BrandContextInput

# KG 语义化推理（通过 DesignRuleSkill）
skill = DesignRuleSkill()
result = skill(DesignRuleInput(industry="Tech", vibe="Minimalist"))
print(result.output.emotions)        # ["Trust", "Innovation", "Premium"]
print(result.output.color_palettes)  # {"primary": [...], "accent": [...]}

# RAG 检索（通过 BrandContextSkill）
brand_skill = BrandContextSkill()
brand_result = brand_skill(BrandContextInput(brand_name="华为", query="配色"))
```

---

## 📝 扩展知识库

### 添加新情绪

编辑 `kg/data/kg_rules.json`：
```json
{
  "emotions": {
    "Nostalgia": {
      "description": "怀旧、复古",
      "color_strategies": ["Sepia", "Muted"],
      "color_palettes": {
        "primary": ["#8B4513", "#D2691E"],
        "accent": ["#F5DEB3"]
      },
      "typography": {
        "style": "Serif",
        "weight": "Regular",
        "characteristics": ["Classic", "Timeless"]
      },
      "layout": {
        "strategy": "Classic",
        "intent": "Heritage",
        "patterns": ["Centered", "Border-framed"]
      }
    }
  }
}
```

### 添加新行业

```json
{
  "industries": {
    "Gaming": {
      "description": "游戏行业",
      "embodies": ["Excitement", "Playfulness", "Innovation"],
      "design_principles": ["High visual impact", "Immersive"],
      "avoid": ["Conservative colors", "Static layouts"]
    }
  }
}
```

---

## 📄 License
© 2025 VibePoster Team
