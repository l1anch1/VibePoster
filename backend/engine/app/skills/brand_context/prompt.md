# Brand Context Skill

## 概述

品牌上下文获取是 Planner 流程的第三步（可选）。当 IntentParseSkill 识别到品牌名称时触发，从 RAG 知识库中检索该品牌的设计规范信息。

数据源：BrandKnowledgeBase (基于向量检索的 RAG 系统)

## 检索策略

按三个方面分别检索，每个方面使用不同的查询模板：

| Aspect | 查询模板 | 用途 |
|--------|----------|------|
| color | `{{$brand_name}}的配色` | 提取品牌配色方案 |
| style | `{{$brand_name}}设计风格` | 提取品牌设计风格描述 |
| guideline | `{{$brand_name}}设计规范` | 提取品牌设计规范和约束 |

每个查询带有 `filter_metadata={"brand": brand_name}`，确保只检索该品牌的知识。

## 输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| brand_name | str | 品牌名称 |
| brand_colors | Dict | 品牌配色 {description: "..."} |
| brand_style | str? | 品牌风格描述文本 |
| guidelines | List[str] | 设计规范列表 |
| source_documents | List[Dict] | RAG 检索到的原文（用于追溯） |

## 容错策略

- 如果 RAG 检索失败，返回 partial 结果（只有 brand_name 字段）
- 不会阻断下游流程

## Examples

**输入**: `brand_name="华为", aspects=["color", "style", "guideline"]`
**输出**:
```json
{
  "brand_name": "华为",
  "brand_colors": {"description": "华为品牌主色为红色(#CF0A2C)，科技蓝为辅色..."},
  "brand_style": "华为设计风格注重科技感和未来感，线条简洁利落...",
  "guidelines": [
    "华为品牌主色为红色(#CF0A2C)，科技蓝为辅色...",
    "华为设计风格注重科技感和未来感...",
    "品牌标志需保持安全距离，不得变形..."
  ],
  "source_documents": [...]
}
```
