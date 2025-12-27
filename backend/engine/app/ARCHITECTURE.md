# 架构说明

## 目录结构

```
backend/engine/app/
├── core/                   # 系统的"地基"
│   ├── __init__.py
│   ├── config.py           # 环境变量、模型名称、全局常量
│   ├── llm.py              # 统一管理 DeepSeek/Gemini 的 Client 工厂
│   └── state.py            # 定义 AgentState 和 PosterSchema (防止循环引用)
│
├── tools/                  # 具体的"脏活累活" (非 Agent 逻辑)
│   ├── __init__.py
│   ├── vision.py           # 抠图、图像合成 (RMBG/Pillow)
│   └── asset_db.py         # 素材库查询
│
├── agents/                 # 纯粹的"大脑" (只写 Prompt 和调用 LLM)
│   ├── __init__.py
│   ├── base.py             # Agent 基类 (定义 invoke 接口规范)
│   ├── director.py         # Director Agent
│   ├── asset.py            # Asset Agent (只调用 tools，不写具体实现)
│   └── layout.py           # Layout Agent
│
├── prompts/                # Prompt 管理
│   ├── __init__.py
│   ├── templates.py        # 存放具体的 Prompt 字符串
│   └── manager.py          # 动态组装 Prompt 的逻辑
│
├── workflow.py             # LangGraph 编排 (只负责连线)
└── main.py                 # FastAPI 入口
```

## 模块说明

### core/ - 系统基础

- **config.py**: 所有配置集中管理
  - LLM 配置（DeepSeek、Gemini）
  - Agent 配置
  - 工作流配置
  - 画布默认配置
  - 错误处理配置

- **llm.py**: LLM Client 工厂
  - 统一管理 DeepSeek 和 Gemini 的 Client
  - 单例模式，避免重复创建

- **state.py**: 状态和 Schema 定义
  - `AgentState`: LangGraph 工作流状态
  - `PosterData`, `TextLayer`, `ImageLayer` 等 Pydantic Schema

### tools/ - 具体实现

- **asset_db.py**: 素材库查询工具
  - 根据关键词搜索素材

- **vision.py**: 视觉处理工具
  - 抠图、图像合成（待实现）
  - Base64 转换等工具函数

### agents/ - Agent 逻辑

- **base.py**: Agent 基类
  - 定义统一的 `invoke` 接口
  - Agent 工厂类

- **director.py**: Director Agent
  - 策划与意图理解
  - 调用 LLM 生成设计简报

- **asset.py**: Asset Agent
  - 素材管理
  - 只调用 tools，不写具体实现

- **layout.py**: Layout Agent
  - 空间计算与排版
  - 调用 LLM 生成海报布局

### prompts/ - Prompt 管理

- **templates.py**: Prompt 模板
  - 存放所有 Prompt 字符串

- **manager.py**: Prompt 管理器
  - 动态组装 Prompt 的逻辑

### workflow.py

- 只负责组装工作流
- 从配置读取节点连接关系
- 不包含任何业务逻辑

### main.py

- FastAPI 入口
- 处理 HTTP 请求
- 调用工作流

## 设计原则

1. **职责分离**: 每个模块只负责自己的职责
2. **配置集中**: 所有配置在 `core/config.py` 中
3. **Prompt 分离**: Prompt 模板和管理逻辑分离
4. **工具独立**: 具体实现放在 `tools/` 中
5. **Agent 纯粹**: Agent 只负责 Prompt 和调用 LLM，不写具体实现

## 扩展指南

### 添加新 Agent

1. 在 `core/config.py` 中添加配置
2. 在 `prompts/templates.py` 中添加 Prompt 模板
3. 在 `prompts/manager.py` 中添加 Prompt 管理函数
4. 在 `agents/` 中创建新的 Agent 文件
5. 在 `workflow.py` 中注册新节点

### 添加新工具

1. 在 `tools/` 中创建新文件
2. 实现具体功能
3. 在 Agent 中调用工具

