# 依赖注入说明

## 什么是依赖注入？

依赖注入（Dependency Injection, DI）是一种设计模式，它的核心思想是：

**不要自己创建依赖，而是从外部注入依赖**

### 简单理解

想象你要做咖啡：

**不好的方式（紧耦合）**：
```python
class CoffeeMaker:
    def __init__(self):
        self.water = Water()  # 自己创建依赖
        self.coffee = Coffee()  # 自己创建依赖
    
    def make_coffee(self):
        return self.water + self.coffee
```

**好的方式（依赖注入）**：
```python
class CoffeeMaker:
    def __init__(self, water, coffee):  # 从外部注入依赖
        self.water = water
        self.coffee = coffee
    
    def make_coffee(self):
        return self.water + self.coffee

# 使用时
water = Water()
coffee = Coffee()
maker = CoffeeMaker(water, coffee)  # 注入依赖
```

## 为什么需要依赖注入？

### 1. 提高可测试性

**没有依赖注入**：
```python
class PosterService:
    def __init__(self):
        self.workflow = app_workflow  # 硬编码，无法替换
    
    def generate(self):
        return self.workflow.invoke(...)

# 测试时无法 mock workflow
```

**有依赖注入**：
```python
class PosterService:
    def __init__(self, workflow=None):
        self.workflow = workflow or app_workflow  # 可以注入
    
    def generate(self):
        return self.workflow.invoke(...)

# 测试时可以注入 mock workflow
mock_workflow = Mock()
service = PosterService(workflow=mock_workflow)
```

### 2. 降低耦合度

依赖注入让组件之间更独立，更容易替换和维护。

### 3. 支持单例模式

可以确保整个应用只有一个服务实例，避免重复创建。

## FastAPI 中的依赖注入

FastAPI 内置了强大的依赖注入系统，使用 `Depends()` 实现。

### 基本用法

```python
from fastapi import Depends

def get_service():
    return Service()

@router.post("/api/endpoint")
async def endpoint(service: Service = Depends(get_service)):
    # FastAPI 会自动调用 get_service() 并注入结果
    return service.do_something()
```

### 依赖链

依赖可以嵌套，形成依赖链：

```python
def get_db():
    return Database()

def get_user_service(db = Depends(get_db)):
    return UserService(db)

@router.get("/users")
async def get_users(service = Depends(get_user_service)):
    return service.get_all()
```

## 项目中的依赖注入实现

### 1. 服务依赖 (`core/dependencies.py`)

```python
# 单例模式的服务实例
_poster_service_instance = None

def get_poster_service() -> PosterService:
    """获取海报服务实例（单例）"""
    global _poster_service_instance
    if _poster_service_instance is None:
        _poster_service_instance = PosterService()
    return _poster_service_instance
```

### 2. 在路由中使用

```python
@router.post("/api/generate")
async def generate(
    poster_service: PosterService = Depends(get_poster_service)
):
    # FastAPI 自动注入服务实例
    return poster_service.generate_poster(...)
```

### 3. 请求验证依赖

```python
async def validate_request(
    prompt: str = Form(...)
) -> PosterGenerateRequest:
    """验证请求参数"""
    return PosterGenerateRequest(prompt=prompt)

@router.post("/api/generate")
async def generate(
    request: PosterGenerateRequest = Depends(validate_request)
):
    # FastAPI 自动验证并注入请求对象
    return process(request)
```

## 依赖注入的优势

### 1. 可测试性

```python
# 测试时可以轻松替换依赖
def test_endpoint():
    mock_service = Mock(spec=PosterService)
    mock_service.generate_poster.return_value = {"result": "success"}
    
    # 使用 override 替换依赖
    app.dependency_overrides[get_poster_service] = lambda: mock_service
    
    response = client.post("/api/generate")
    assert response.status_code == 200
```

### 2. 生命周期管理

- **请求级别**：每个请求创建新实例
- **应用级别**：整个应用共享一个实例（单例）

### 3. 配置管理

```python
def get_settings():
    return settings  # 从配置模块获取

@router.get("/config")
async def get_config(settings = Depends(get_settings)):
    return settings
```

## 最佳实践

### 1. 使用单例模式管理服务

```python
# ✅ 好的做法
_service_instance = None

def get_service():
    global _service_instance
    if _service_instance is None:
        _service_instance = Service()
    return _service_instance
```

### 2. 分离依赖定义

将依赖函数放在 `core/dependencies.py` 中，而不是路由文件中。

### 3. 使用类型提示

```python
# ✅ 好的做法
def get_service() -> PosterService:
    return PosterService()

# 路由中使用类型提示
async def endpoint(service: PosterService = Depends(get_service)):
    pass
```

### 4. 支持测试覆盖

```python
# 在测试中覆盖依赖
app.dependency_overrides[get_poster_service] = lambda: mock_service
```

## 示例：完整的依赖注入流程

```python
# 1. 定义依赖（core/dependencies.py）
def get_poster_service() -> PosterService:
    return PosterService()

# 2. 在路由中使用（api/routes/poster.py）
@router.post("/api/generate")
async def generate(
    service: PosterService = Depends(get_poster_service)
):
    return service.generate_poster(...)

# 3. FastAPI 自动处理
# - 调用 get_poster_service()
# - 将结果注入到 service 参数
# - 如果出错，自动处理异常
```

## 总结

依赖注入 = **外部提供依赖 + 自动注入 + 易于测试**

主要好处：
- ✅ 代码更清晰
- ✅ 更容易测试
- ✅ 降低耦合度
- ✅ 支持单例模式

