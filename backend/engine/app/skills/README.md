# Skills 模块（Semantic Kernel 风格）

模块化能力封装，将 Planner Agent 的意图理解能力拆分为独立的 Skill。

## 目录结构

```
skills/
├── base.py              ← BaseSkill 基类 + config/prompt 加载器 + render_template
├── types.py             ← Pydantic 输入/输出 Schema
├── orchestrator.py      ← Skill 调度器
│
├── intent_parse/
│   ├── config.json      ← 机器可读：name, tags, input_variables
│   ├── prompt.md        ← 人类可读：关键词映射表、置信度公式、示例
│   └── run.py           ← 执行逻辑
│
├── design_rule/
│   ├── config.json
│   ├── prompt.md        ← KG 结构说明、推理链路、输出字段
│   └── run.py           ← 执行：调用 KnowledgeGraph
│
├── brand_context/
│   ├── config.json
│   ├── prompt.md        ← RAG 检索策略、查询模板
│   └── run.py           ← 执行：调用 KnowledgeBase
│
└── design_brief/
    ├── config.json      ← input_variables: knowledge_context, user_prompt, key_elements
    ├── prompt.md        ← **LLM Prompt 模板**（含 {{$变量}} 占位符）
    └── run.py           ← 执行：render_prompt → 调用 LLM
```

## 设计理念（对齐 Semantic Kernel）

每个 Skill 由三个文件组成：

| 文件 | 角色 | 类比 Semantic Kernel |
|------|------|---------------------|
| `config.json` | 机器可读元数据：name, description, version, tags, input_variables | `config.json` |
| `prompt.md` | 人类可读文档：Prompt 模板（支持 `{{$变量}}`）、示例、约束 | `skprompt.txt` |
| `run.py` | 执行逻辑：继承 BaseSkill，实现 run() | Native Function |

### Prompt 模板占位符

`prompt.md` 中使用 Semantic Kernel 风格的 `{{$variable}}` 占位符：

```markdown
## Prompt Template

你是一个专业的海报设计总监。
...
{{$knowledge_context}}
请根据上述信息生成设计简报。

## User Prompt Template

{{$user_prompt}}
{{$key_elements}}
```

`run.py` 通过 `self.render_prompt(variables)` 自动替换：

```python
system_prompt = self.render_prompt({
    "knowledge_context": knowledge_context_string,
})
```

## 执行流程

```
用户输入 → IntentParseSkill → DesignRuleSkill → (BrandContextSkill) → DesignBriefSkill
              意图解析           设计规则推理        品牌上下文            设计简报生成
```

## 快速使用

```python
from app.skills import IntentParseSkill, IntentParseInput

skill = IntentParseSkill()
# config.json + prompt.md 已自动加载
print(skill.config.name)              # "intent_parse"
print(skill.config.tags)              # ["nlp", "intent", "rule-based"]
print(skill.config.input_variables)   # [InputVariable(name="user_prompt", ...)]

result = skill(IntentParseInput(user_prompt="苹果发布会科技风海报"))
print(result.output.industry)   # "Tech"
print(result.output.brand_name) # "苹果"
```

## 扩展新 Skill

1. 创建目录 `skills/my_skill/`
2. 编写 `config.json`（name, description, input_variables）
3. 编写 `prompt.md`（说明 + Prompt 模板，用 `{{$var}}` 占位符）
4. 编写 `run.py`（继承 BaseSkill，调用 `self.render_prompt(vars)`）

## 测试

```bash
cd backend/engine
pytest tests/test_skills.py -v
```
