# 全局异常处理

> **统一文档** - 简单说明 + 详细文档

---

## 📋 快速理解

### 什么是全局异常处理？

全局异常处理中间件是一个**统一的错误处理机制**，它会自动捕获所有异常，并返回统一的错误响应格式。

### 为什么需要它？

**之前的问题**：
- ❌ 每个路由都要写 try-except
- ❌ 错误响应格式不统一
- ❌ 需要手动记录日志
- ❌ 代码重复

**现在的优势**：
- ✅ 路由代码更简洁
- ✅ 所有错误响应格式统一
- ✅ 自动记录日志
- ✅ 集中管理错误处理逻辑

### 工作原理（简单理解）

想象一下，你的应用是一个**工厂**：

1. **路由层**（工人）：处理请求，可能会出错
2. **异常处理器**（质检员）：自动捕获所有错误
3. **统一包装**：将错误包装成统一格式返回

```
请求 → 路由处理 → 如果出错 → 异常处理器捕获 → 统一格式返回
```

---

## 📚 详细说明

### 概述

全局异常处理中间件统一处理所有异常，确保：
1. **统一的错误响应格式**：所有错误都返回 `ErrorResponse` 格式
2. **自动日志记录**：所有异常自动记录到日志
3. **减少重复代码**：路由中不需要重复的 try-except 块
4. **更好的错误追踪**：记录请求路径、方法等上下文信息

## 工作原理

### 1. 异常处理优先级

FastAPI 按以下优先级处理异常（从高到低）：

1. **自定义业务异常** (`VibePosterException`)
   - 由 `vibe_poster_exception_handler` 处理
   - 用于业务逻辑层的预期错误

2. **HTTP 异常** (`StarletteHTTPException`)
   - 由 `http_exception_handler` 处理
   - 用于 FastAPI 的 HTTPException

3. **请求验证异常** (`RequestValidationError`)
   - 由 `validation_exception_handler` 处理
   - 用于 Pydantic 验证错误

4. **通用异常** (`Exception`)
   - 由 `exception_handler` 处理
   - 捕获所有未处理的异常（兜底）

### 2. 异常类层次结构

```
VibePosterException (基础异常)
├── ValidationException (400) - 参数验证错误
├── NotFoundException (404) - 资源未找到
├── ServiceException (500) - 服务层错误
└── WorkflowException (500) - 工作流错误
```

### 3. 使用示例

#### 在路由中使用自定义异常

```python
from ...core.exceptions import ValidationException, ServiceException

@router.post("/api/endpoint")
async def endpoint():
    try:
        # 业务逻辑
        result = service.do_something()
        return result
    except ValueError as e:
        # 转换为自定义异常，由全局处理器统一处理
        raise ValidationException(
            message="参数错误",
            detail={"field": "prompt", "reason": str(e)}
        )
    except Exception as e:
        # 转换为自定义异常
        raise ServiceException(
            message="处理失败",
            detail={"error": str(e)}
        )
```

#### 在服务层使用自定义异常

```python
from ..core.exceptions import ServiceException, WorkflowException

def process_data(data):
    if not data:
        raise ValidationException("数据不能为空")
    
    try:
        result = workflow.invoke(data)
        return result
    except Exception as e:
        raise WorkflowException(
            message="工作流执行失败",
            detail={"error": str(e)}
        )
```

## 错误响应格式

所有错误都返回统一的 `ErrorResponse` 格式：

```json
{
  "success": false,
  "error": "错误消息",
  "detail": {
    "field": "prompt",
    "reason": "不能为空"
  }
}
```

## 日志记录

不同类型的异常有不同的日志级别：

- **业务异常** (`VibePosterException`): `WARNING` 级别，不记录堆栈
- **HTTP 异常**: `WARNING` 级别
- **验证异常**: `WARNING` 级别
- **未处理异常**: `ERROR` 级别，记录完整堆栈

所有日志都包含：
- 请求路径 (`path`)
- 请求方法 (`method`)
- 状态码 (`status_code`)
- 错误详情 (`detail`)

## 优势

1. **统一格式**：所有错误响应格式一致，前端更容易处理
2. **自动日志**：无需在每个路由中手动记录日志
3. **减少代码**：路由代码更简洁，不需要大量 try-except
4. **易于维护**：错误处理逻辑集中管理
5. **更好的调试**：记录完整的上下文信息

## 注意事项

1. **不要捕获所有异常**：只在需要的地方捕获特定异常
2. **使用合适的异常类型**：根据错误类型选择合适的异常类
3. **提供有意义的错误消息**：帮助用户理解问题
4. **不要泄露敏感信息**：生产环境不要返回详细的堆栈信息

