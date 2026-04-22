# 测试文档

## 测试结构

```
tests/
├── __init__.py              # 测试模块初始化
├── conftest.py              # Pytest 配置和 fixtures
├── README.md                # 本文件
├── test_api_routes.py       # API 路由测试
├── test_api_schemas.py      # API Schema 测试
├── test_core_schemas.py     # Core Schema 测试
├── test_services.py         # Service 层测试
├── test_knowledge_graph.py  # Knowledge Graph 设计规则推理测试
├── test_rag_engine.py       # RAG 品牌知识检索测试
├── test_layout_engine.py    # OOP 动态布局引擎测试
├── test_renderer_service.py # 渲染服务测试
└── test_integration.py      # 集成测试（完整数据流）
```

## 测试覆盖范围

### 核心模块测试

| 模块 | 测试文件 | 测试内容 |
|------|----------|----------|
| Knowledge Graph | `test_knowledge_graph.py` | 设计规则推理、关键词匹配、图谱统计 |
| RAG Engine | `test_rag_engine.py` | 文档存储、向量/关键词检索、品牌知识 |
| Layout Engine | `test_layout_engine.py` | 文本块、图片块、容器布局、嵌套 |
| Renderer Service | `test_renderer_service.py` | DSL 解析、Schema 转换、海报渲染 |

### 集成测试

| 测试类 | 测试内容 |
|--------|----------|
| `TestKGAndRAGIntegration` | KG + RAG 协作 |
| `TestLayoutEngineIntegration` | 布局引擎完整流程 |
| `TestDesignBriefIntegration` | 设计简报构建 |
| `TestEndToEndWorkflow` | 端到端海报生成 |
| `TestErrorHandling` | 错误处理 |

## 运行测试

### 安装测试依赖

```bash
pip install pytest pytest-asyncio httpx
```

### 运行所有测试

```bash
pytest
```

### 运行特定测试文件

```bash
pytest tests/test_api_routes.py
```

### 运行特定测试类

```bash
pytest tests/test_api_routes.py::TestStepRoutes
```

### 运行特定测试方法

```bash
pytest tests/test_api_routes.py::TestStepRoutes::test_plan_success
```

### 运行带标记的测试

```bash
# 运行单元测试
pytest -m unit

# 运行 API 测试
pytest -m api

# 跳过慢速测试
pytest -m "not slow"
```

### 查看测试覆盖率

```bash
pip install pytest-cov
pytest --cov=app --cov-report=html
```

## 论文第五章实验

### 前提条件

1. 激活虚拟环境：`source .venv/bin/activate`
2. 确认 `.env` 中配好 API Key（PLANNER/LAYOUT/CRITIC 三个 Agent + CRITIC_VISION）
3. 确认单元测试通过：`python -m pytest tests/ -m "not slow" -q`

### 实验 1：消融实验（论文 5.3 节）

五组配置 × 30 条 prompt = 150 次 LLM 调用。

| 配置 | 说明 |
|------|------|
| Baseline | 纯 LLM 直接输出坐标（无 DSL、无 KG、无 RAG） |
| +DSL | 加入语义 DSL + 布局引擎 |
| +DSL+KG | 再加入 KG 知识图谱推理 |
| +DSL+RAG | DSL + RAG 品牌知识（无 KG） |
| Full | 完整系统（DSL + KG + RAG） |

```bash
python -m pytest tests/test_ablation.py -v -s -m slow
```

- 预计耗时：40–75 分钟
- 输出：`tests/results/ablation_results.json`
- 终端打印各配置的 PASS 率、可读性、布局得分和平均耗时

### 实验 2：端到端成功率（论文 5.2 + 5.4 节）

完整系统配置跑 30 条 prompt，含 Critic 重试。

```bash
python -m pytest tests/test_e2e_benchmark.py -v -s -m slow
```

- 预计耗时：15–30 分钟
- 输出：`tests/results/e2e_results.json`
- 终端打印 Plan/Layout/Critic 成功率、重试次数和平均耗时

### 实验 3：单元测试覆盖率（论文 5.2 节）

```bash
python -m pytest tests/ -m "not slow" --cov=app --cov-report=term-missing
```

### 实验相关文件

| 文件 | 用途 |
|------|------|
| `tests/data/test_prompts.json` | 30 条测试 prompt（6 行业 × 5 风格） |
| `tests/test_ablation.py` | 消融实验运行器（4 配置 × 30 prompt） |
| `tests/test_e2e_benchmark.py` | 端到端全流程测试 |
| `app/utils/metrics.py` | 自动化质量指标（可读性/布局/风格一致性） |
| `tests/results/` | 实验结果输出目录（运行后生成） |

### 从结果中提取论文数据

```python
import json
with open("tests/results/ablation_results.json") as f:
    data = json.load(f)
for name in ["Baseline", "+DSL", "+DSL+RAG", "Full"]:
    rows = [r for r in data if r["config"] == name]
    pass_n = sum(1 for r in rows if r.get("critic_status") == "PASS")
    print(f"{name:12s}  PASS={pass_n}/{len(rows)}")
```

### 注意事项

- 素材搜索（Pexels/Flux）在实验中跳过，使用占位图
- LLM 调用真实，结果有随机性，建议多次运行取均值
- `@pytest.mark.slow` 确保日常 `pytest` 不会意外执行这些实验

