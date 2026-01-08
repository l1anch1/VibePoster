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
pytest tests/test_api_routes.py::TestPosterRoutes
```

### 运行特定测试方法

```bash
pytest tests/test_api_routes.py::TestPosterRoutes::test_generate_simple_success
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

## 测试分类

### 单元测试 (unit)
- 测试单个函数或方法
- 使用 mock 隔离依赖
- 快速执行

### 集成测试 (integration)
- 测试多个组件协作
- 可能需要真实依赖（如数据库）
- 执行时间较长

### API 测试 (api)
- 测试 HTTP 接口
- 使用 TestClient
- 验证请求/响应格式

## 编写测试指南

1. **测试命名**: 使用 `test_` 前缀
2. **测试类命名**: 使用 `Test` 前缀
3. **使用 fixtures**: 在 `conftest.py` 中定义共享 fixtures
4. **使用 mock**: 隔离外部依赖（如 LLM API、文件系统）
5. **测试边界**: 测试正常情况、边界情况和错误情况
6. **保持独立**: 每个测试应该独立运行，不依赖其他测试

## 示例

### 基本测试

```python
def test_example():
    """测试示例"""
    result = function_under_test()
    assert result == expected_value
```

### 使用 fixtures

```python
def test_with_fixture(client):
    """使用 fixture 的测试"""
    response = client.get("/api/endpoint")
    assert response.status_code == 200
```

### 使用 mock

```python
@patch('app.services.poster_service.app_workflow')
def test_with_mock(mock_workflow):
    """使用 mock 的测试"""
    mock_workflow.invoke.return_value = {"result": "success"}
    result = service.method()
    assert result == expected
```

