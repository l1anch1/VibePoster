# Design Rule Skill

## 概述

设计规则推理是 Planner 流程的第二步。接收 IntentParseSkill 输出的 `industry` 和 `vibe` 关键词，查询手工构建的知识图谱（KG），推理出一套完整的设计规则建议。

知识图谱数据来源：
- 《创意海报版式设计》
- 《Photoshop 海报设计》

推理链路：`Industry / Vibe → Emotion → Visual Elements`

## 知识图谱结构

KG 由三层节点组成：

```
Layer 1: Entry Nodes
  ├── Industry: Tech, Food, Luxury, Healthcare, Education, Entertainment, Finance, Travel, Fashion, Real Estate
  └── Vibe: Minimalist, Energetic, Professional, Friendly, Bold, Vintage, Modern, Natural

Layer 2: Emotion Nodes
  Trust, Innovation, Premium, Excitement, Warmth, Freshness, Playfulness,
  Elegance, Calm, Urgency, Authority, Joy, Sophistication ...

Layer 3: Visual Element Nodes
  ├── Color: strategies, palettes (primary / accent)
  ├── Typography: styles, weights, characteristics
  ├── Layout: strategies, intents, patterns
  └── Principles: design_principles, avoid
```

## 输出字段说明

| 字段 | 含义 | 示例 |
|------|------|------|
| emotions | 推理出的情绪基调 | ["Trust", "Innovation"] |
| color_strategies | 配色策略 | ["Monochromatic", "Triadic"] |
| color_palettes | 具体色板 {primary, accent} | {"primary": ["#0066CC"], "accent": ["#48BB78"]} |
| typography_styles | 字体风格 | ["Sans-Serif"] |
| typography_weights | 字重 | ["Medium", "Bold"] |
| typography_characteristics | 排版特征 | ["Clean", "Modern"] |
| layout_strategies | 布局策略 | ["Structured", "Dynamic"] |
| layout_intents | 布局意图 | ["Stability", "Forward-thinking"] |
| layout_patterns | 布局模式 | ["Grid", "Diagonal"] |
| design_principles | 设计原则 | ["Clean interfaces", "Scalable design"] |
| avoid | 应避免的元素 | ["Warm earth tones", "Script fonts"] |

## 容错策略

- 如果没有提供任何关键词，返回空规则 (status=success)
- 如果 KG 查询异常，返回部分结果 (status=partial) 并记录错误
- 不会阻断下游流程

## Examples

**输入**: `industry="Tech", vibe="Minimalist"`
**输出**:
```json
{
  "emotions": ["Trust", "Innovation", "Premium"],
  "color_strategies": ["Monochromatic", "Triadic"],
  "color_palettes": {
    "primary": ["#0066CC", "#6366F1"],
    "accent": ["#48BB78", "#22D3EE"]
  },
  "typography_styles": ["Sans-Serif"],
  "typography_weights": ["Medium", "Bold"],
  "layout_patterns": ["Grid", "Diagonal"],
  "design_principles": ["Clean interfaces", "Scalable design system"],
  "avoid": ["Warm earth tones", "Script fonts"]
}
```
