# 依赖注入说明

## 什么是依赖注入？

依赖注入（Dependency Injection, DI）是一种设计模式，核心思想是：

**不要自己创建依赖，而是从外部注入依赖**

---

## 项目中的依赖注入实现

### ServiceContainer 模式

项目使用 `ServiceContainer` 统一管理所有服务单例：

```python
# core/dependencies.py

class ServiceContainer:
    """服务容器 - 统一管理所有服务实例"""
    
    _poster_service = None
    _knowledge_service = None
    _knowledge_graph = None
    _knowledge_base = None
    _renderer_service = None
    
    @classmethod
    def reset_all(cls):
        """重置所有服务实例（用于测试）"""
        cls._poster_service = None
        cls._knowledge_service = None
        cls._knowledge_graph = None
        cls._knowledge_base = None
        cls._renderer_service = None
```

### 获取服务的函数

```python
def get_knowledge_graph():
    """获取知识图谱实例（单例）"""
    if ServiceContainer._knowledge_graph is None:
        from ..knowledge import DesignKnowledgeGraph
        ServiceContainer._knowledge_graph = DesignKnowledgeGraph()
    return ServiceContainer._knowledge_graph

def get_knowledge_base():
    """获取品牌知识库实例（单例）"""
    if ServiceContainer._knowledge_base is None:
        from ..knowledge import BrandKnowledgeBase
        ServiceContainer._knowledge_base = BrandKnowledgeBase()
    return ServiceContainer._knowledge_base

def get_knowledge_service():
    """获取知识服务实例（单例）"""
    if ServiceContainer._knowledge_service is None:
        from ..services.knowledge_service import KnowledgeService
        ServiceContainer._knowledge_service = KnowledgeService(
            knowledge_graph=get_knowledge_graph(),
            knowledge_base=get_knowledge_base()
        )
    return ServiceContainer._knowledge_service

def get_poster_service():
    """获取海报服务实例（单例）"""
    if ServiceContainer._poster_service is None:
        from ..services import PosterService
        ServiceContainer._poster_service = PosterService()
    return ServiceContainer._poster_service
```

---

## 在路由中使用

### 使用 FastAPI 的 Depends

```python
from fastapi import Depends
from ...core.dependencies import get_knowledge_service, get_poster_service
from ...services.knowledge_service import KnowledgeService
from ...services import PosterService

@router.post("/api/generate_multimodal")
async def generate_multimodal(
    ...,
    poster_service: PosterService = Depends(get_poster_service),
):
    """FastAPI 自动调用 get_poster_service() 并注入"""
    return poster_service.generate_poster(...)

@router.get("/api/kg/infer")
async def infer_design_rules(
    keywords: str,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
):
    """注入知识服务"""
    rules = knowledge_service.infer_design_rules(keywords.split(","))
    return {"rules": rules}
```

---

## 在 Agent 中使用

### 支持依赖注入的 Agent 函数

```python
# agents/planner.py

def run_planner_agent(
    user_prompt: str,
    ...,
    knowledge_service=None  # 支持注入，便于测试
) -> Dict[str, Any]:
    """
    运行 Planner Agent
    
    Args:
        knowledge_service: 知识服务实例（可选，用于依赖注入）
    """
    # 获取知识服务（支持依赖注入）
    ks = knowledge_service or get_knowledge_service()
    
    # 使用 KnowledgeService 获取设计上下文
    design_context = ks.get_design_context(user_prompt, brand_name)
    ...
```

---

## 依赖链

依赖可以嵌套，形成依赖链：

```
get_poster_service
    └── get_knowledge_service
            ├── get_knowledge_graph
            │       └── DesignKnowledgeGraph
            └── get_knowledge_base
                    └── BrandKnowledgeBase
```

---

## 测试中的依赖注入

### 方式 1：重置 ServiceContainer

```python
# tests/conftest.py

@pytest.fixture(autouse=True)
def reset_services():
    """每个测试前重置所有服务"""
    from app.core.dependencies import reset_all_services
    reset_all_services()
    yield
    reset_all_services()
```

### 方式 2：使用 dependency_overrides

```python
# tests/test_api.py

from fastapi.testclient import TestClient
from unittest.mock import Mock

def test_generate_poster():
    # 创建 Mock 服务
    mock_service = Mock(spec=PosterService)
    mock_service.generate_poster.return_value = {"canvas": {}, "layers": []}
    
    # 覆盖依赖
    app.dependency_overrides[get_poster_service] = lambda: mock_service
    
    # 测试
    client = TestClient(app)
    response = client.post("/api/generate_multimodal", ...)
    
    # 清理
    app.dependency_overrides.clear()
    
    assert response.status_code == 200
```

### 方式 3：直接注入 Mock

```python
def test_planner_with_mock_knowledge():
    # 创建 Mock KnowledgeService
    mock_ks = Mock()
    mock_ks.get_design_context.return_value = {
        "kg_keywords": ["Tech"],
        "kg_rules": {"recommended_colors": ["#0066FF"]},
        "brand_knowledge": []
    }
    
    # 直接注入到函数
    result = run_planner_agent(
        user_prompt="设计海报",
        knowledge_service=mock_ks  # 注入 Mock
    )
    
    # 验证调用
    mock_ks.get_design_context.assert_called_once()
```

---

## 延迟初始化

所有服务使用延迟初始化，避免启动时加载全部依赖：

```python
class KnowledgeService:
    def __init__(self, knowledge_graph=None, knowledge_base=None):
        self._knowledge_graph = knowledge_graph
        self._knowledge_base = knowledge_base
        self._kg_initialized = knowledge_graph is not None
        self._kb_initialized = knowledge_base is not None
    
    @property
    def knowledge_graph(self):
        """延迟初始化知识图谱"""
        if not self._kg_initialized:
            from ..knowledge import DesignKnowledgeGraph
            self._knowledge_graph = DesignKnowledgeGraph()
            self._kg_initialized = True
        return self._knowledge_graph
```

---

## 最佳实践

### 1. 使用 ServiceContainer 管理单例

```python
# ✅ 好的做法
class ServiceContainer:
    _service = None
    
    @classmethod
    def get_service(cls):
        if cls._service is None:
            cls._service = Service()
        return cls._service
```

### 2. 分离依赖定义

将依赖函数放在 `core/dependencies.py` 中，而不是路由文件中。

### 3. 支持测试覆盖

确保所有依赖都可以被 Mock 或替换：

```python
def run_agent(
    ...,
    knowledge_service=None  # 支持注入
):
    ks = knowledge_service or get_knowledge_service()
```

### 4. 使用类型提示

```python
def get_knowledge_service() -> KnowledgeService:
    """获取知识服务（单例）"""
    ...
```

---

## 依赖图

```
┌────────────────────────────────────────────────────────────┐
│                      API Routes                             │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ Depends(get_xxx) │  │ Depends(get_xxx) │                │
│  └────────┬─────────┘  └────────┬─────────┘                │
└───────────│─────────────────────│──────────────────────────┘
            │                     │
            ▼                     ▼
┌───────────────────────────────────────────────────────────┐
│                   ServiceContainer                         │
│  ┌─────────────────┐  ┌─────────────────┐                 │
│  │ _poster_service │  │_knowledge_service│                 │
│  │ _renderer_serv. │  │ _knowledge_graph │                 │
│  │                 │  │ _knowledge_base  │                 │
│  └─────────────────┘  └─────────────────┘                 │
└───────────────────────────────────────────────────────────┘
            │                     │
            ▼                     ▼
┌───────────────────────────────────────────────────────────┐
│                   Actual Services                          │
│  ┌─────────────────┐  ┌─────────────────┐                 │
│  │  PosterService  │  │KnowledgeService │                 │
│  │ RendererService │  │DesignKnowledgeG.│                 │
│  │                 │  │BrandKnowledgeB. │                 │
│  └─────────────────┘  └─────────────────┘                 │
└───────────────────────────────────────────────────────────┘
```

---

## 总结

| 概念 | 实现 |
|------|------|
| 服务容器 | `ServiceContainer` 类 |
| 获取服务 | `get_xxx_service()` 函数 |
| 路由注入 | `Depends(get_xxx_service)` |
| Agent 注入 | 可选参数 + `or get_xxx_service()` |
| 测试重置 | `reset_all_services()` |
| 延迟初始化 | `@property` + 标志位 |

**主要好处**：
- ✅ 代码更清晰
- ✅ 更容易测试（可 Mock）
- ✅ 降低耦合度
- ✅ 支持单例模式
- ✅ 延迟初始化节省资源

---

**最后更新**: 2025-01-08
