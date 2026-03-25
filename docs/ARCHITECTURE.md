# 系统架构与实现

> **统一文档** - 架构设计 + 实现状态 + 技术栈说明

---

## 📋 目录

1. [架构概览](#架构概览)
2. [目录结构](#目录结构)
3. [分层设计](#分层设计)
4. [核心模块](#核心模块)
5. [知识模块](#知识模块)
6. [实现状态](#实现状态)
7. [技术栈](#技术栈)

---

## 架构概览

### 整体架构

```plaintext
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend                                  │
│              (React + TypeScript + Tailwind CSS)                │
│                    iOS Liquid Glass Style                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP/REST API
┌───────────────────────────▼─────────────────────────────────────┐
│                    Backend (FastAPI)                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              API Layer (routes/)                            │ │
│  │       统一响应格式 + 依赖注入 + 参数验证                      │ │
│  └──────────────────────────┬─────────────────────────────────┘ │
│  ┌──────────────────────────▼─────────────────────────────────┐ │
│  │            Service Layer (services/)                        │ │
│  │  ┌─────────────────┐ ┌─────────────────┐ ┌───────────────┐ │ │
│  │  │  PosterService  │ │KnowledgeService │ │RendererService│ │ │
│  │  └─────────────────┘ └─────────────────┘ └───────────────┘ │ │
│  └──────────────────────────┬─────────────────────────────────┘ │
│  ┌──────────────────────────▼─────────────────────────────────┐ │
│  │         Workflow (LangGraph Orchestration)                  │ │
│  │   ┌─────────┬─────────┬─────────────┬─────────────────┐    │ │
│  │   │ Planner │ Visual  │   Layout    │     Critic      │    │ │
│  │   │  Agent  │ Agent   │   Agent     │     Agent       │    │ │
│  │   │  (KG+RAG)│        │  (DSL/OOP)  │                 │    │ │
│  │   └─────────┴─────────┴─────────────┴─────────────────┘    │ │
│  └──────────────────────────┬─────────────────────────────────┘ │
│  ┌──────────────────────────▼─────────────────────────────────┐ │
│  │              Knowledge Layer (knowledge/)                   │ │
│  │  ┌─────────────────────┐  ┌─────────────────────────────┐  │ │
│  │  │DesignKnowledgeGraph │  │   BrandKnowledgeBase (RAG)  │  │ │
│  │  │    (networkx)       │  │  (sentence-transformers)    │  │ │
│  │  └─────────────────────┘  └─────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Tools Layer (tools/)                           │ │
│  │  • OCR + 图像理解 • 抠图 • 素材搜索                          │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Core Layer (core/)                             │ │
│  │  • Config • LLM • Logger • Interfaces • Dependencies        │ │
│  │  • OOP Layout Engine • Exceptions                           │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│               Render Service (Node.js)                           │
│                   PSD 生成与下载                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 目录结构

```plaintext
VibePoster/
├── frontend/                    # 前端 (React + Tailwind CSS)
│   ├── src/
│   │   ├── components/         # React 组件
│   │   │   ├── editor/         # 编辑器组件
│   │   │   ├── landing/        # 落地页组件
│   │   │   └── poster/         # 海报展示组件
│   │   ├── config/             # 配置常量
│   │   ├── services/           # API 服务
│   │   ├── hooks/              # 自定义 Hooks
│   │   ├── utils/              # 工具函数
│   │   ├── types/              # TypeScript 类型定义
│   │   └── App.tsx             # 主应用
│   └── README.md
│
├── backend/
│   ├── engine/                  # 海报生成引擎 (Python/FastAPI)
│   │   ├── app/
│   │   │   ├── api/            # API 路由层
│   │   │   │   ├── middleware.py      # 中间件
│   │   │   │   └── routes/
│   │   │   │       ├── steps.py       # 分步生成路由 /api/step/*
│   │   │   │       └── knowledge.py   # 知识模块路由 (KG + RAG)
│   │   │   │
│   │   │   ├── workflow/       # 工作流模块（LangGraph 编排）
│   │   │   │   ├── orchestrator.py    # 工作流编排（节点连接）
│   │   │   │   └── state.py           # AgentState 定义
│   │   │   │
│   │   │   ├── core/           # 核心基础设施
│   │   │   │   ├── config.py          # 配置管理
│   │   │   │   ├── llm.py             # LLM 客户端工厂
│   │   │   │   ├── logger.py          # 日志系统
│   │   │   │   ├── exceptions.py      # 异常定义
│   │   │   │   ├── interfaces.py      # 接口抽象
│   │   │   │   ├── dependencies.py    # 依赖注入
│   │   │   │   ├── utils.py           # 工具函数
│   │   │   │   └── layout/            # OOP 布局引擎
│   │   │   │       ├── styles.py      # 样式定义
│   │   │   │       ├── elements.py    # 元素定义
│   │   │   │       └── containers.py  # 容器定义
│   │   │   │
│   │   │   ├── models/         # 领域数据模型
│   │   │   │   ├── poster.py         # 海报数据模型
│   │   │   │   └── response.py       # 统一 API 响应模型
│   │   │   │
│   │   │   ├── knowledge/      # 知识模块
│   │   │   │   ├── kg/               # Knowledge Graph 子模块
│   │   │   │   │   ├── data/
│   │   │   │   │   │   └── kg_rules.json
│   │   │   │   │   └── design_rules.py
│   │   │   │   └── rag/              # RAG 子模块
│   │   │   │       ├── data/
│   │   │   │       │   └── default_brand_knowledge.json
│   │   │   │       └── rag_engine.py
│   │   │   │
│   │   │   ├── agents/         # Agent 层（AI 决策）
│   │   │   │   ├── base.py            # Agent 基类
│   │   │   │   ├── planner.py         # Planner Agent (集成KG+RAG)
│   │   │   │   ├── visual.py          # Visual Agent
│   │   │   │   ├── layout.py          # Layout Agent (支持DSL)
│   │   │   │   └── critic.py          # Critic Agent
│   │   │   │
│   │   │   ├── services/       # 业务逻辑层
│   │   │   │   ├── poster_service.py  # 海报生成服务
│   │   │   │   ├── knowledge_service.py # 知识服务
│   │   │   │   └── renderer/          # 渲染服务
│   │   │   │       ├── dsl_parser.py
│   │   │   │       ├── schema_converter.py
│   │   │   │       └── service.py
│   │   │   │
│   │   │   ├── tools/          # 工具层（具体实现）
│   │   │   │   ├── data/
│   │   │   │   │   └── asset_library.json
│   │   │   │   ├── vision.py          # 抠图、图像合成
│   │   │   │   ├── image_understanding.py  # OCR + 图像理解
│   │   │   │   └── asset_db.py        # 素材搜索
│   │   │   │
│   │   │   ├── prompts/        # Prompt 管理（按 Agent 组织）
│   │   │   │   ├── planner.py        # Planner Agent prompt
│   │   │   │   ├── visual.py         # Visual Agent prompt
│   │   │   │   ├── layout.py         # Layout Agent prompt (DSL)
│   │   │   │   └── critic.py         # Critic Agent prompt
│   │   │   │
│   │   │   └── main.py         # FastAPI 入口
│   │   │
│   │   └── tests/              # 测试目录
│   │
│   └── render/                  # PSD 渲染服务 (Node.js)
│
├── docs/                        # 文档目录
│   ├── README.md                       # 文档索引
│   ├── ARCHITECTURE.md                 # 架构说明（本文件）
│   ├── ONLINE_EDITOR_IMPLEMENTATION.md # 在线编辑器实现
│   ├── TASK_REQUIREMENTS_ANALYSIS.md   # 任务需求分析
│   ├── VISUAL_AGENT_ARCHITECTURE_ANALYSIS.md
│   ├── OCR_AND_IMAGE_UNDERSTANDING.md
│   ├── CONFIGURATION.md
│   ├── DEPENDENCY_INJECTION.md
│   └── EXCEPTION_HANDLING.md
│
├── docker-compose.yml           # Docker 编排
└── README.md                    # 项目主 README
```

---

## 分层设计

### 1. API 层 (`api/`)

**职责**：
- 接收 HTTP 请求
- 参数验证（Pydantic）
- 通过依赖注入获取服务
- 返回统一格式的响应

**路由拆分**：
- `routes/steps.py`: 分步生成接口 `/api/step/*`（plan / assets / layouts / finalize）
- `routes/knowledge.py`: 知识模块接口 `/api/kg/*`, `/api/brand/*`

**响应模型**：
- `models/response.py`: 统一响应模型

**统一响应格式**（定义在 `models/response.py`）：
```python
class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: str = "操作成功"
```

### 2. 服务层 (`services/`)

**职责**：
- 封装业务逻辑
- 协调多个模块
- 不涉及 HTTP 请求/响应

**核心服务**：
- `PosterService`: 海报生成主服务
- `KnowledgeService`: 统一管理 KG + RAG
- `RendererService`: OOP 布局渲染

### 3. Agent 层 (`agents/`)

**职责**：
- AI 决策和规划
- 调用 LLM
- 协调工具层

**四大 Agent**：
- **Planner**: 将用户需求转化为设计简报（集成 KG + RAG）
- **Visual**: 处理图片（抠图、OCR、图像理解、素材搜索）
- **Layout**: 生成海报布局（支持 DSL 模式，使用 OOP 布局引擎）
- **Critic**: 审核海报质量，提供反馈

### 4. 知识层 (`knowledge/`)

**职责**：
- 存储和推理设计规则
- 检索企业品牌知识

**目录结构**：
```
knowledge/
├── kg/                        # Knowledge Graph 子模块
│   ├── types.py               # Pydantic 类型定义
│   ├── loader.py              # 数据加载
│   ├── graph.py               # NetworkX 图操作
│   ├── inference.py           # 推理逻辑
│   └── knowledge_graph.py     # 主入口
├── rag/                       # RAG 子模块
│   ├── types.py               # Pydantic 类型定义
│   ├── embedder.py            # 向量编码
│   ├── loader.py              # 数据加载
│   ├── retriever.py           # 检索逻辑
│   └── knowledge_base.py      # 主入口
└── __init__.py                # 统一导出
```

### 5. Prompt 模块 (`prompts/`)

**职责**：
- 管理各 Agent 的 Prompt 模板
- 按 Agent 组织，职责清晰

**目录结构**：
```
prompts/
├── __init__.py       # 统一导出
├── planner.py        # Planner Agent (设计简报生成)
├── visual.py         # Visual Agent (图像分析)
├── layout.py         # Layout Agent (DSL 布局指令)
└── critic.py         # Critic Agent (质量审核)
```

**文件结构一致**：
```python
# 每个文件包含：
SYSTEM_PROMPT = """..."""          # 系统 prompt
USER_PROMPT_TEMPLATE = """..."""   # 用户 prompt 模板（可选）

def get_prompt(...) -> Dict[str, str]:
    """返回 {"system": ..., "user": ...}"""
```

### 6. 工具层 (`tools/`)

**职责**：
- 具体的技术实现
- 图像处理（抠图、合成）
- OCR + 图像理解
- 素材搜索

### 7. 核心层 (`core/`)

**职责**：
- 配置管理 (`config.py`)
- LLM 客户端工厂 (`llm.py`)
- 日志系统 (`logger.py`)
- 异常定义 (`exceptions.py`)
- 接口抽象 (`interfaces.py`)
- 依赖注入 (`dependencies.py`)
- OOP 布局引擎 (`layout/`)

**注意**：工作流相关代码已移至 `workflow/` 模块。

### 8. 工作流模块 (`workflow/`)

**职责**：
- 定义工作流状态 (`state.py`)
- LangGraph 编排 (`orchestrator.py`)
- 节点连接和条件边

**结构**：
```
workflow/
├── __init__.py           # 模块导出
├── state.py              # AgentState 定义
└── orchestrator.py       # 工作流编排
```

---

## 核心模块

### 1. 依赖注入 (`core/dependencies.py`)

使用 `ServiceContainer` 统一管理所有服务单例：

```python
class ServiceContainer:
    _poster_service = None
    _knowledge_service = None
    _knowledge_graph = None
    _knowledge_base = None
    _renderer_service = None
    
    @classmethod
    def reset_all(cls):
        """重置所有服务（用于测试）"""
        ...

def get_knowledge_service() -> KnowledgeService:
    """获取知识服务（单例）"""
    ...
```

### 2. 接口抽象 (`core/interfaces.py`)

定义核心接口，实现依赖倒置：

```python
class IKnowledgeGraph(ABC):
    @abstractmethod
    def infer_rules(self, keywords: List[str]) -> Dict[str, Any]: ...

class IKnowledgeBase(ABC):
    @abstractmethod
    def search(self, query: str, top_k: int) -> List[Dict]: ...
```

### 3. OOP 布局引擎 (`core/layout/`)

替代硬编码坐标计算，使用容器+组件的流式布局：

```python
class Element(ABC):
    """元素基类"""
    ...

class TextBlock(Element):
    """文本块 - 自动计算高度"""
    ...

class VerticalContainer(Container):
    """垂直容器 - 类似 CSS Flexbox"""
    def arrange(self): ...
```

### 4. 知识服务 (`services/knowledge_service.py`)

统一管理 KG 和 RAG：

```python
class KnowledgeService:
    def get_design_context(self, user_prompt, brand_name) -> Dict:
        """获取完整的设计上下文（KG + RAG）"""
        # 1. 从 prompt 提取关键词
        keywords = self.extract_keywords(user_prompt)
        # 2. KG 推理设计规则
        kg_rules = self.infer_design_rules(keywords)
        # 3. RAG 检索品牌知识
        brand_knowledge = self.search_brand_knowledge(...)
        return {...}
```

---

## 知识模块

### Knowledge Graph (设计规则推理)

**存储结构**：
```
Industry/Vibe → Color/Font/Layout
     ↓              ↓
   Tech  ───────→  #0066FF (科技蓝)
                   Sans-Serif
                   Grid Layout
```

**使用方式**：
```python
kg = DesignKnowledgeGraph()
rules = kg.infer_rules(["Tech", "Promotion"])
# {
#   "recommended_colors": ["#0066FF", "#FF4444"],
#   "recommended_fonts": ["Helvetica", "Arial"],
#   "recommended_layouts": ["Grid", "Center"]
# }
```

### RAG Engine (品牌知识检索)

**技术栈**：
- 轻量级：`sentence-transformers` (paraphrase-multilingual-MiniLM-L12-v2)
- 完整版：`langchain` + `chromadb`（可选）

**使用方式**：
```python
rag = BrandKnowledgeBase()
rag.add_document("华为品牌主色调是昆仑红...", {"brand": "华为"})
results = rag.search("华为的配色", top_k=2)
```

---

## 实现状态

### ✅ 已完成

#### 核心基础设施
- ✅ 配置管理系统（Pydantic Settings V2）
- ✅ LLM 客户端工厂（DeepSeek、Gemini）
- ✅ 统一日志系统
- ✅ 全局异常处理
- ✅ 依赖注入系统（ServiceContainer）
- ✅ 接口抽象（IKnowledgeGraph, IKnowledgeBase）

#### 知识模块
- ✅ Knowledge Graph 设计规则推理
- ✅ RAG 品牌知识检索
- ✅ KnowledgeService 统一管理
- ✅ API 端点（/api/kg/infer, /api/brand/upload, /api/brand/search）

#### Agent 层
- ✅ Planner Agent（集成 KG + RAG）
- ✅ Visual Agent（OCR + 图像理解 + 抠图 + 素材搜索）
- ✅ Layout Agent（支持 DSL 模式）
- ✅ Critic Agent（质量审核）

#### 布局引擎
- ✅ OOP 布局引擎（Element, Container）
- ✅ RendererService（DSL 解析 + Pydantic 转换）

#### 前端
- ✅ React + TypeScript + Tailwind CSS
- ✅ iOS Liquid Glass 风格
- ✅ Landing Page
- ✅ 在线编辑器（图层选择、拖拽、属性编辑）
- ✅ 品牌文档上传功能

#### Docker
- ✅ Dockerfile（frontend, engine, render）
- ✅ docker-compose.yml

### 🗑️ 已删除

- ~~`templates/` 风格模板系统~~ → 已删除，被 KG + RAG 完全替代

---

## 技术栈

### 后端 (Python/FastAPI)

| 类别 | 技术 | 用途 |
|------|------|------|
| **Web 框架** | FastAPI | RESTful API 服务 |
| **AI 编排** | LangGraph | Agent 工作流编排 |
| **LLM** | DeepSeek, Gemini | 大语言模型 |
| **图像处理** | Pillow | 图像分析、合成 |
| **知识图谱** | networkx | 设计规则存储与推理 |
| **向量检索** | sentence-transformers | RAG 语义检索 |
| **数据验证** | Pydantic V2 | 数据模型和配置管理 |
| **测试** | Pytest | 单元测试和集成测试 |

### 渲染服务 (Node.js)

| 类别 | 技术 | 用途 |
|------|------|------|
| **Web 框架** | Express.js | HTTP 服务 |
| **PSD 生成** | ag-psd | PSD 文件生成 |
| **图像处理** | sharp | 图像调整和转换 |

### 前端 (React)

| 类别 | 技术 | 用途 |
|------|------|------|
| **框架** | React 18 | UI 框架 |
| **语言** | TypeScript | 类型安全 |
| **构建工具** | Vite | 开发和构建 |
| **样式** | Tailwind CSS v4 | 原子化 CSS |
| **HTTP 客户端** | Axios | API 调用 |

---

## 设计原则

### 1. 分层架构
- 清晰的层次划分（API → Service → Workflow → Agent → Knowledge → Tools → Core）
- 单向依赖（上层依赖下层，下层不依赖上层）
- 业务逻辑与基础设施分离（workflow/ vs core/）

### 2. 依赖倒置
- 通过接口抽象（`IKnowledgeGraph`, `IKnowledgeBase`）实现解耦
- 便于测试时 Mock

### 3. 单一职责
- 每个模块只负责一件事
- Agent 只做决策，Service 处理业务逻辑，Tools 做具体实现

### 4. 统一规范
- 统一的错误处理
- 统一的日志格式
- 统一的 API 响应格式

---

**最后更新**: 2025-01-09
