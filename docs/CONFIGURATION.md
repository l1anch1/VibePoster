# 配置说明

## 概述

本项目使用 Pydantic Settings V2 进行配置管理，所有配置集中在 `core/config.py`。

---

## 配置文件结构

### 1. Agent 配置

每个 Agent 都有独立的配置类：

```python
class PlannerAgentConfig(BaseSettings):
    """Planner Agent 配置"""
    API_KEY: str = Field(..., env="DEEPSEEK_API_KEY")
    BASE_URL: str = Field(default="https://api.deepseek.com")
    MODEL: str = "deepseek-chat"
    TEMPERATURE: float = 0.7
    DEFAULT_INTENT: str = "promotion"

class VisualAgentConfig(BaseSettings):
    """Visual Agent 配置"""
    ...

class LayoutAgentConfig(BaseSettings):
    """Layout Agent 配置"""
    USE_DSL_MODE: bool = True  # 是否使用 DSL 模式
    ...

class CriticAgentConfig(BaseSettings):
    """Critic Agent 配置"""
    MAX_RETRY_COUNT: int = 2
    ...
```

### 2. Knowledge Graph 配置

```python
class KGConfig(BaseSettings):
    """Knowledge Graph 配置"""
    
    RULES_FILE: str = "./app/knowledge/data/kg_rules.json"  # 规则数据文件
```

### 3. RAG 配置

```python
class RAGConfig(BaseSettings):
    """RAG 知识库配置"""
    
    # 存储配置
    PERSIST_DIRECTORY: str = "./data/chroma_db"
    
    # 默认数据配置
    LOAD_DEFAULT_DATA: bool = True
    DEFAULT_DATA_PATH: str = "./app/knowledge/data/default_brand_knowledge.json"
    
    # 模型配置
    EMBEDDING_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"
    USE_CHROMADB: bool = False  # 否则使用内存存储
```

### 4. 画布配置

```python
class CanvasConfig(BaseSettings):
    """画布默认配置"""
    WIDTH: int = 1080
    HEIGHT: int = 1920
    BG_COLOR: str = "#FFFFFF"
```

### 5. CORS 配置

```python
class CORSConfig(BaseSettings):
    """CORS 配置"""
    ALLOW_ORIGINS: str = "http://localhost,http://localhost:5173,*"
    ALLOW_METHODS: str = "GET,POST,PUT,DELETE,OPTIONS"
    ALLOW_HEADERS: str = "Content-Type,Authorization"
```

---

## 环境变量

在 `backend/engine/.env` 文件中配置：

```bash
# DeepSeek API (用于 Planner, Visual, Critic)
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# Gemini API (用于 Layout)
GEMINI_API_KEY=your_gemini_api_key

# Pexels API (用于素材搜索)
PEXELS_API_KEY=your_pexels_api_key

# Knowledge Graph 配置 (可选)
KG_RULES_FILE=./data/kg_rules.json

# RAG 配置 (可选)
RAG_PERSIST_DIRECTORY=./data/chroma_db
RAG_LOAD_DEFAULT_DATA=true
RAG_DEFAULT_DATA_PATH=./data/default_brand_knowledge.json
RAG_EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
RAG_USE_CHROMADB=false

# 可选：OpenAI API
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
```

---

## Prompt 管理

### 目录结构

```
prompts/
├── templates.py       # 基础 Prompt 模板
├── dsl_templates.py   # DSL 模式 Prompt 模板 (NEW)
└── manager.py         # Prompt 组装
```

### 获取 Prompt

```python
from app.prompts.manager import (
    get_planner_prompt,
    get_layout_prompt,      # 传统 JSON 模式
    get_layout_dsl_prompt,  # DSL 模式 (NEW)
    get_critic_prompt,
)

# Planner Prompt（支持模板上下文）
prompts = get_planner_prompt(
    user_prompt="设计一张招聘海报",
    chat_history=None,
    template_context="【知识图谱推荐】\n- 推荐颜色: #0066FF..."
)

# Layout DSL Prompt
prompt = get_layout_dsl_prompt(
    design_brief={...},
    asset_list={...},
    canvas_width=1080,
    canvas_height=1920,
    review_feedback=None
)
```

---

## 知识模块配置

### Knowledge Graph

Knowledge Graph 规则已从硬编码迁移到外部数据文件。

**数据文件**：`data/kg_rules.json`

**配置项**：
| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| `RULES_FILE` | `KG_RULES_FILE` | `./data/kg_rules.json` | 规则数据文件路径 |

**支持的关键词**：
- 行业：Tech, Food, Education, Fashion, Real Estate, Healthcare, Finance, Travel, Music
- 氛围：Minimalist, Energetic, Luxury, Friendly, Professional, Promotion, Vintage, Modern, Natural

### RAG Engine

RAG Engine 配置通过 `RAGConfig` 管理。

**数据文件**：`data/default_brand_knowledge.json`

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| `LOAD_DEFAULT_DATA` | `RAG_LOAD_DEFAULT_DATA` | `true` | 是否加载默认华为品牌数据 |
| `DEFAULT_DATA_PATH` | `RAG_DEFAULT_DATA_PATH` | `./data/default_brand_knowledge.json` | 默认数据文件路径 |
| `EMBEDDING_MODEL` | `RAG_EMBEDDING_MODEL` | `paraphrase-multilingual-MiniLM-L12-v2` | 向量模型 |
| `USE_CHROMADB` | `RAG_USE_CHROMADB` | `false` | 是否使用 ChromaDB 持久化 |

---

## 使用全局配置

```python
from app.core.config import settings

# 访问 Agent 配置
settings.planner.MODEL  # "deepseek-chat"
settings.layout.USE_DSL_MODE  # True

# 访问 KG 配置
settings.kg.RULES_FILE  # "./data/kg_rules.json"

# 访问 RAG 配置
settings.rag.LOAD_DEFAULT_DATA  # True
settings.rag.DEFAULT_DATA_PATH  # "./data/default_brand_knowledge.json"
settings.rag.EMBEDDING_MODEL

# 访问画布配置
settings.canvas.WIDTH  # 1080
settings.canvas.HEIGHT  # 1920

# 访问 CORS 配置
settings.cors.allow_origins_list  # ["*"]
```

---

## 配置最佳实践

### 1. 环境变量优先

所有敏感信息（如 API Key）通过环境变量配置：

```python
class MyConfig(BaseSettings):
    API_KEY: str = Field(..., env="MY_API_KEY")  # 必需
    DEBUG: bool = Field(default=False, env="DEBUG")  # 可选
```

### 2. 使用 Pydantic Settings

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class MyConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MY_",  # 环境变量前缀
        env_file=".env",
        extra="ignore"
    )
    
    API_KEY: str
    TIMEOUT: int = 30
```

### 3. 提供默认值

为所有配置提供合理的默认值：

```python
class LayoutAgentConfig(BaseSettings):
    USE_DSL_MODE: bool = True  # 默认启用 DSL 模式
    MAX_TOKENS: int = 4096
```

### 4. 类型安全

使用类型注解确保配置正确：

```python
class CanvasConfig(BaseSettings):
    WIDTH: int = Field(default=1080, ge=100, le=10000)  # 带验证
    HEIGHT: int = Field(default=1920, ge=100, le=10000)
```

---

## 常见问题

### Q: 如何切换 Layout Agent 的输出模式？

A: 修改 `LayoutAgentConfig.USE_DSL_MODE`：

```python
# core/config.py
class LayoutAgentConfig(BaseSettings):
    USE_DSL_MODE: bool = False  # 改为 False 使用传统 JSON 模式
```

或通过环境变量：
```bash
LAYOUT_USE_DSL_MODE=false
```

### Q: 如何禁用默认品牌数据加载？

A: 设置 `RAG_LOAD_DEFAULT_DATA=false`：

```bash
# .env
RAG_LOAD_DEFAULT_DATA=false
```

### Q: 如何使用 ChromaDB 持久化？

A: 配置以下环境变量：

```bash
RAG_USE_CHROMADB=true
RAG_PERSIST_DIRECTORY=./data/chroma_db
```

---

## 总结

| 配置类型 | 配置类 | 数据文件 | 说明 |
|----------|--------|----------|------|
| Agent | `PlannerAgentConfig` 等 | - | LLM 模型、温度等 |
| KG | `KGConfig` | `data/kg_rules.json` | 设计规则数据路径 |
| RAG | `RAGConfig` | `data/default_brand_knowledge.json` | 向量模型、存储路径 |
| 画布 | `CanvasConfig` | - | 默认尺寸、背景色 |
| CORS | `CORSConfig` | - | 跨域配置 |

---

**最后更新**: 2025-01-08
