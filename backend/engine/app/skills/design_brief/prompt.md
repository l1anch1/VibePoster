# Design Brief Skill

## 概述

设计简报生成是 Planner 流程的最后一步，也是唯一需要调用 LLM 的 Skill。
它将前三个 Skill 的输出（意图、设计规则、品牌上下文）综合为一份 System Prompt，
交给 LLM 生成结构化的设计简报 JSON。

流程: `IntentParse → DesignRule → BrandContext → **DesignBrief**`

## Prompt Template

你是一个专业的海报设计总监。你的任务是将用户的模糊需求转化为结构化的设计简报。

请严格按照以下 JSON 格式输出，不要包含 Markdown 格式（如 ```json ... ```）：
```
{
    "title": "海报主标题 (简短有力)",
    "subtitle": "副标题 (补充说明)",
    "main_color": "主色调Hex值 (如 #FF0000)",
    "background_color": "背景色Hex值",
    "style_keywords": ["background image keyword 1 in English", "background image keyword 2 in English"],
    "intent": "promotion"
}
```

注意：
1. style_keywords 必须是英文关键词，用于搜索背景图片，例如：["cartoon cloud", "blue sky", "abstract", "texture", "tech"] 等
2. 背景图必须保证画面不杂乱，可以是纯色渐变或纹理等抽象图片，但不能有具体的主体比如人物或者街道等。
3. 背景图决定整体风格，需要谨慎选择，比如宣传海报可以花哨一点，招聘海报需要严肃的。
4. 关键词应该简洁、准确，适合用于图片搜索引擎（如 Pexels、Unsplash）
5. 主标题和副标题为中文
6. intent 可选值: promotion | invite | cover | other

{{$knowledge_context}}

请根据上述风格模板的配色、字体、布局原则来生成设计简报。

## User Prompt Template

{{$user_prompt}}
{{$key_elements}}

## 决策追溯

输出的 `decision_trace` 字段记录每项决策的来源：

| 追溯字段 | 说明 |
|----------|------|
| intent_source | 固定 "intent_parse_skill" |
| main_color_source | "kg_inference" 或 "llm_generation" |
| design_rules_source | "kg_inference"（当 KG 有推理结果时） |
| brand_source | "rag_retrieval"（当 RAG 有检索结果时） |

## 容错策略

- LLM 返回非法 JSON → 使用 KG 主色调 + 默认值构建 partial 结果
- LLM 调用异常 → 同上
- 确保不阻断下游 Agent 流程

## Examples

**输入**: `user_prompt="科技公司招聘海报，极简风格"`, `industry=Tech`, `vibe=Minimalist`
**输出**:
```json
{
  "title": "加入我们 共创未来",
  "subtitle": "2025 技术精英招募计划",
  "main_color": "#0066CC",
  "background_color": "#F5F5F5",
  "style_keywords": ["abstract geometric", "minimal gradient", "tech texture"],
  "intent": "promotion",
  "decision_trace": {
    "intent_source": "intent_parse_skill",
    "main_color_source": "kg_inference",
    "design_rules_source": "kg_inference",
    "emotions": ["Trust", "Innovation"]
  }
}
```
