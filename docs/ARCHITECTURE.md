# 系统架构与实现

> **统一文档** - 架构设计 + 实现状态 + 技术栈说明

---

## 📋 目录

1. [架构概览](#架构概览)
2. [目录结构](#目录结构)
3. [分层设计](#分层设计)
4. [核心模块](#核心模块)
5. [实现状态](#实现状态)
6. [技术栈](#技术栈)

---

## 架构概览

### 整体架构

```plaintext
┌─────────────────────────────────────────────────┐
│                   Frontend                       │
│              (React + TypeScript)                │
└───────────────────┬─────────────────────────────┘
                    │ HTTP/REST API
┌───────────────────▼─────────────────────────────┐
│              Backend (FastAPI)                   │
│  ┌──────────────────────────────────────────┐   │
│  │         API Layer (routes/)              │   │
│  └────────────────┬─────────────────────────┘   │
│  ┌────────────────▼─────────────────────────┐   │
│  │       Service Layer (services/)          │   │
│  └────────────────┬─────────────────────────┘   │
│  ┌────────────────▼─────────────────────────┐   │
│  │    Workflow (LangGraph Orchestration)    │   │
│  │   ┌─────────┬─────────┬─────────────┐    │   │
│  │   │ Planner │ Visual  │   Layout    │    │   │
│  │   │  Agent  │ Agent   │   Agent     │    │   │
│  │   └─────────┴─────────┴─────────────┘    │   │
│  │   ┌─────────────────────────────────┐    │   │
│  │   │         Critic Agent            │    │   │
│  │   └─────────────────────────────────┘    │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │         Tools Layer (tools/)             │   │
│  │  • OCR + 图像理解 • 抠图 • 素材搜索      │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │         Core Layer (core/)               │   │
│  │  • Config • LLM • Logger • Middleware    │   │
│  └──────────────────────────────────────────┘   │
└──────────────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────┐
│          Render Service (Node.js)                │
│              PSD 生成与下载                       │
└──────────────────────────────────────────────────┘
```

---

## 目录结构

```plaintext
VibePoster/
├── frontend/                    # 前端 (React)
│   ├── src/
│   │   ├── components/         # React 组件
│   │   ├── types/              # TypeScript 类型定义
│   │   └── App.tsx             # 主应用
│   └── README.md
│
├── backend/
│   ├── engine/                  # 海报生成引擎 (Python/FastAPI)
│   │   ├── app/
│   │   │   ├── core/           # 核心基础设施
│   │   │   │   ├── config.py          # 配置管理
│   │   │   │   ├── llm.py             # LLM 客户端工厂
│   │   │   │   ├── logger.py          # 日志系统
│   │   │   │   ├── exceptions.py      # 异常定义
│   │   │   │   ├── middleware.py      # 全局中间件
│   │   │   │   ├── dependencies.py    # 依赖注入
│   │   │   │   ├── schemas.py         # 数据模型
│   │   │   │   └── state.py           # 工作流状态
│   │   │   │
│   │   │   ├── tools/          # 工具层（具体实现）
│   │   │   │   ├── vision.py          # 抠图、图像合成
│   │   │   │   ├── ocr.py             # OCR（已废弃）
│   │   │   │   ├── image_understanding.py  # OCR + 图像理解
│   │   │   │   └── asset_db.py        # 素材搜索
│   │   │   │
│   │   │   ├── agents/         # Agent 层（AI 决策）
│   │   │   │   ├── base.py            # Agent 基类
│   │   │   │   ├── planner.py         # Planner Agent
│   │   │   │   ├── visual.py          # Visual Agent
│   │   │   │   ├── layout.py          # Layout Agent
│   │   │   │   └── critic.py          # Critic Agent
│   │   │   │
│   │   │   ├── prompts/        # Prompt 管理
│   │   │   │   ├── templates.py       # Prompt 模板
│   │   │   │   └── manager.py         # Prompt 组装
│   │   │   │
│   │   │   ├── services/       # 业务逻辑层
│   │   │   │   └── poster_service.py  # 海报生成服务
│   │   │   │
│   │   │   ├── api/            # API 路由层
│   │   │   │   ├── schemas.py         # API 响应模型
│   │   │   │   └── routes/
│   │   │   │       └── poster.py      # 海报路由
│   │   │   │
│   │   │   ├── utils/          # 工具函数
│   │   │   │   └── json_parser.py     # JSON 解析
│   │   │   │
│   │   │   ├── workflow.py     # LangGraph 工作流编排
│   │   │   └── main.py         # FastAPI 入口
│   │   │
│   │   ├── tests/              # 测试目录
│   │   │   ├── conftest.py            # Pytest 配置
│   │   │   ├── test_api_routes.py     # API 测试
│   │   │   ├── test_services.py       # Service 测试
│   │   │   └── test_core_schemas.py   # Schema 测试
│   │   │
│   │   └── pytest.ini          # Pytest 配置
│   │
│   └── render/                  # PSD 渲染服务 (Node.js)
│       ├── src/
│       │   ├── server.js               # Express 服务器
│       │   ├── routes/                 # 路由
│       │   │   └── psd.js
│       │   ├── services/               # 服务
│       │   │   └── psdGenerator.js
│       │   └── utils/                  # 工具
│       │       └── helpers.js
│       └── package.json
│
├── docs/                        # 文档目录
│   ├── README.md                       # 文档索引
│   ├── ARCHITECTURE.md                 # 架构说明（本文件）
│   ├── VISUAL_AGENT_ARCHITECTURE_ANALYSIS.md  # Visual Agent 专题
│   ├── OCR_AND_IMAGE_UNDERSTANDING.md  # OCR + 图像理解
│   ├── CONFIGURATION.md                # 配置说明
│   ├── DEPENDENCY_INJECTION.md         # 依赖注入
│   └── EXCEPTION_HANDLING.md           # 异常处理
│
├── TASK_REQUIREMENTS_ANALYSIS.md       # 任务需求分析
└── README.md                            # 项目主 README
```

---

## 分层设计

### 1. API 层 (`api/routes/`)

**职责**：

- 接收 HTTP 请求
- 参数验证（Pydantic）
- 调用服务层
- 返回统一格式的响应

**示例**：

```python
# api/routes/poster.py

@router.post("/generate", response_model=PosterResponse)
async def generate_poster(
    request: PosterRequest,
    poster_service: PosterService = Depends(get_poster_service)
):
    """生成海报 API"""
    result = poster_service.generate_poster(
        prompt=request.prompt,
        canvas_width=request.canvas_width,
        canvas_height=request.canvas_height,
        image_person=request.image_person,
        image_bg=request.image_bg,
        chat_history=request.chat_history
    )
    return PosterResponse(success=True, data=result, message="海报生成成功")
```

### 2. 服务层 (`services/`)

**职责**：

- 封装业务逻辑
- 处理用户上传的图片
- 构建工作流初始状态
- 调用工作流
- 返回处理结果

**示例**：

```python
# services/poster_service.py

class PosterService:
    def generate_poster(self, prompt, canvas_width, canvas_height, ...):
        # 1. 处理用户上传的图片
        user_images = self.process_user_images(image_person, image_bg)
        
        # 2. 构建初始状态
        initial_state = self.build_initial_state(...)
        
        # 3. 启动工作流
        final_state = self.workflow.invoke(initial_state)
        
        # 4. 返回结果
        return final_state["final_poster"]
```

### 3. Agent 层 (`agents/`)

**职责**：

- AI 决策和规划
- 调用 LLM
- 协调工具层

**四大 Agent**：

- **Planner**: 将用户需求转化为设计简报
- **Visual**: 处理图片（抠图、OCR、图像理解、素材搜索）
- **Layout**: 生成海报布局和图层坐标
- **Critic**: 审核海报质量，提供反馈

### 4. 工具层 (`tools/`)

**职责**：

- 具体的技术实现
- 图像处理（抠图、合成）
- OCR + 图像理解
- 素材搜索

### 5. 核心层 (`core/`)

**职责**：

- 配置管理
- LLM 客户端工厂
- 日志系统
- 异常处理
- 依赖注入

---

## 核心模块

### 1. LLM 客户端工厂 (`core/llm.py`)

**职责**：统一管理多个 LLM 提供商的客户端

```python
class LLMClientFactory:
    @staticmethod
    def get_client(provider: str, api_key: str, base_url: str):
        """获取 LLM 客户端"""
        if provider == "deepseek":
            return OpenAI(api_key=api_key, base_url=base_url)
        elif provider == "gemini":
            return genai.GenerativeModel(...)
        # ... 其他提供商
```

**支持的 LLM**：

- DeepSeek (Planner, Visual, Critic)
- Google Gemini (Layout)
- OpenAI（可选）
- Moonshot（可选）

### 2. 配置管理 (`core/config.py`)

**职责**：集中管理所有配置

```python
class Settings(BaseSettings):
    # LLM 配置
    planner: PlannerConfig
    visual: VisualConfig
    layout: LayoutConfig
    critic: CriticConfig
    
    # 工作流配置
    MAX_RETRY_TIMES: int = 3
    
    # 画布配置
    DEFAULT_CANVAS_WIDTH: int = 800
    DEFAULT_CANVAS_HEIGHT: int = 1200
    
    # CORS 配置
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173"]
```

### 3. 工作流编排 (`workflow.py`)

**职责**：使用 LangGraph 编排 Agent 流程

```python
# 定义工作流图
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("planner", planner_node)
workflow.add_node("visual", visual_node)
workflow.add_node("layout", layout_node)
workflow.add_node("critic", critic_node)

# 连接节点
workflow.add_edge("planner", "visual")
workflow.add_edge("visual", "layout")
workflow.add_edge("layout", "critic")
workflow.add_conditional_edges(
    "critic",
    should_retry,
    {
        "retry": "layout",
        "end": END
    }
)

# 设置入口
workflow.set_entry_point("planner")
```

### 4. 全局异常处理 (`core/middleware.py`)

**职责**：统一处理所有异常

```python
@app.exception_handler(VibePosterException)
async def vibe_poster_exception_handler(request, exc):
    """处理业务异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            error=exc.message,
            detail=exc.detail
        ).dict()
    )
```

### 5. 依赖注入 (`core/dependencies.py`)

**职责**：管理依赖的生命周期

```python
_poster_service_instance = None

def get_poster_service() -> PosterService:
    """获取 PosterService 单例"""
    global _poster_service_instance
    if _poster_service_instance is None:
        workflow = get_workflow()
        _poster_service_instance = PosterService(workflow)
    return _poster_service_instance
```

---

## 实现状态

### ✅ 已完成

#### 1. 核心基础设施 (core/)

- ✅ 配置管理系统（Pydantic Settings V2）
- ✅ LLM 客户端工厂（支持 DeepSeek、Gemini）
- ✅ 统一日志系统
- ✅ 全局异常处理
- ✅ 依赖注入系统
- ✅ 数据模型定义（Pydantic Schema）

#### 2. Agent 层 (agents/)

- ✅ Planner Agent - 需求转化为设计简报
- ✅ Visual Agent - 图像处理和分析
- ✅ Layout Agent - 布局生成
- ✅ Critic Agent - 质量审核

#### 3. 工具层 (tools/)

- ✅ 抠图功能（rembg）
- ✅ 图像合成（Pillow）
- ✅ OCR + 图像理解（DeepSeek Vision，一次调用完成）
- ✅ 素材搜索（Pexels API）

#### 4. 业务逻辑层 (services/)

- ✅ PosterService - 海报生成服务
- ✅ 图片预处理
- ✅ 工作流调度

#### 5. API 层 (api/)

- ✅ 海报生成 API
- ✅ API 响应模型
- ✅ 统一错误响应格式

#### 6. 工作流 (workflow.py)

- ✅ LangGraph 工作流编排
- ✅ 重试机制
- ✅ 状态管理

#### 7. 渲染服务 (backend/render/)

- ✅ PSD 文件生成
- ✅ 图层处理（背景、前景、文字）
- ✅ ZIP 打包下载

#### 8. 前端 (frontend/)

- ✅ React + TypeScript
- ✅ 用户输入界面
- ✅ 图片上传
- ✅ 画布尺寸选择
- ✅ 海报预览
- ✅ PSD 下载

#### 9. 测试 (tests/)

- ✅ API 路由测试
- ✅ Service 层测试
- ✅ Schema 测试
- ✅ Pytest 配置

---

### 🚧 待优化

#### 1. 服务层扩展

- 🔲 ImageAnalysisService - 统一管理图像分析
- 🔲 AssetManagementService - 统一管理素材
- 🔲 CacheService - 缓存图像分析结果

#### 2. 性能优化

- 🔲 图像分析结果缓存
- 🔲 素材搜索结果缓存
- 🔲 异步处理优化

#### 3. 功能增强

- 🔲 更多风格模板（目前支持 5 种）
- 🔲 在线编辑功能
- 🔲 RAG 知识库集成
- 🔲 更多 LLM 支持

#### 4. 文档完善

- 🔲 API 文档（Swagger/OpenAPI）
- 🔲 用户手册
- 🔲 开发者指南

---

## 技术栈

### 后端 (Python/FastAPI)

| 类别 | 技术 | 用途 |
| ------ | ------ | ------ |
| **Web 框架** | FastAPI | RESTful API 服务 |
| **AI 编排** | LangGraph | Agent 工作流编排 |
| **LLM** | DeepSeek, Gemini | 大语言模型 |
| **图像处理** | Pillow, rembg | 图像合成、抠图 |
| **数据验证** | Pydantic V2 | 数据模型和配置管理 |
| **日志** | Python logging | 日志系统 |
| **测试** | Pytest | 单元测试和集成测试 |
| **API 调用** | Pexels API | 素材搜索 |

### 渲染服务 (Node.js)

| 类别 | 技术 | 用途 |
| ------ | ------ | ------ |
| **Web 框架** | Express.js | HTTP 服务 |
| **PSD 生成** | ag-psd | PSD 文件生成 |
| **图像处理** | sharp | 图像调整和转换 |
| **压缩** | archiver | ZIP 文件打包 |

### 前端 (React)

| 类别 | 技术 | 用途 |
| ------ | ------ | ------ |
| **框架** | React 18 | UI 框架 |
| **语言** | TypeScript | 类型安全 |
| **构建工具** | Vite | 开发和构建 |
| **HTTP 客户端** | Axios | API 调用 |
| **样式** | CSS-in-JS | 组件样式 |

---

## 设计原则

### 1. 分层架构

- 清晰的层次划分（API → Service → Agent → Tools → Core）
- 单向依赖（上层依赖下层，下层不依赖上层）

### 2. 单一职责

- 每个模块只负责一件事
- Agent 只做决策，不做具体实现
- Tools 只做实现，不做决策

### 3. 依赖注入

- 服务单例管理
- 便于测试和替换

### 4. 统一规范

- 统一的错误处理
- 统一的日志格式
- 统一的响应格式

### 5. 可扩展性

- 易于添加新的 Agent
- 易于添加新的 LLM 提供商
- 易于添加新的工具

---

## 数据流

### 海报生成流程

```plaintext
1. 用户输入
   ├─ 文字需求："设计一张招聘海报"
   ├─ 画布尺寸：800x1200
   └─ 图片（可选）：背景图、人物图

2. API 层 (routes/poster.py)
   └─ 接收请求，验证参数

3. 服务层 (services/poster_service.py)
   ├─ 处理图片（转换为 bytes）
   └─ 构建初始状态

4. 工作流编排 (workflow.py)
   └─ 启动 LangGraph 工作流

5. Planner Agent
   └─ 输出：design_brief
       ├─ title: "诚聘英才"
       ├─ subtitle: "共创未来"
       ├─ main_color: "#1E3A8A"
       └─ style_keywords: ["business", "professional"]

6. Visual Agent
   ├─ OCR + 图像理解（一次调用完成）
   ├─ 抠图处理
   ├─ 素材搜索
   └─ 输出：asset_list
       ├─ background_layer: {src: "...", type: "image"}
       ├─ foreground_layer: {src: "...", type: "image"}
       └─ image_analyses: [...]

7. Layout Agent
   └─ 输出：final_poster
       ├─ canvas: {width: 800, height: 1200, backgroundColor: "#FFFFFF"}
       └─ layers: [
           {id: "bg", type: "image", ...},
           {id: "person", type: "image", ...},
           {id: "title", type: "text", content: "诚聘英才", ...},
           {id: "subtitle", type: "text", content: "共创未来", ...}
       ]

8. Critic Agent
   ├─ 审核海报质量
   └─ 如果不通过 → 返回 Layout Agent 重新生成（最多 3 次）

9. 返回结果
   └─ API 返回海报数据给前端

10. 前端渲染
    ├─ 显示海报预览
    └─ 提供 PSD 下载按钮

11. PSD 下载（可选）
    └─ 调用 Render Service 生成 PSD + ZIP
```

---

## 总结

### 核心优势

1. **✅ 模块化设计**：清晰的分层和职责划分
2. **✅ 可扩展性强**：易于添加新功能和新 Agent
3. **✅ 性能优化**：OCR + 图像理解一次调用，节省 50% token
4. **✅ 代码规范**：统一的异常处理、日志系统、依赖注入
5. **✅ 易于测试**：完整的测试覆盖
6. **✅ 易于维护**：清晰的文档和代码结构

### 技术亮点

- LangGraph 工作流编排
- 多 LLM 支持（DeepSeek、Gemini）
- Vision LLM 多任务优化
- 依赖注入和单例模式
- 全局异常处理中间件

---

**最后更新**: 2025-01-01
