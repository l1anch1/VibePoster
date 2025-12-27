# Agent 和 Prompt 配置说明

## 概述

本项目将原本硬编码的 Agent 配置和 Prompts 提取到了配置文件中，使其更易于管理和修改。

## 配置文件结构

### 1. `config.py` - 核心配置文件

包含所有 Agent 的配置、Prompt 模板、工作流配置等。

#### Agent 配置

- **DIRECTOR_CONFIG**: Director Agent (策划总监) 的配置
  - `provider`: 提供商 (如 "deepseek", "openai")
  - `model`: 模型名称
  - `api_key`: API 密钥（从环境变量读取）
  - `base_url`: API 基础 URL
  - `temperature`: 温度参数
  - `response_format`: 响应格式

- **LAYOUT_CONFIG**: Layout Agent (排版设计师) 的配置
  - 类似结构，针对 Gemini API

- **ASSET_CONFIG**: Asset Agent (素材管理) 的配置
  - 本地素材库配置

#### Prompt 模板

- **DIRECTOR_SYSTEM_PROMPT**: Director Agent 的系统提示词
- **LAYOUT_PROMPT_TEMPLATE**: Layout Agent 的提示词模板（支持格式化）

#### 工作流配置

- **WORKFLOW_CONFIG**: 定义工作流的节点顺序和连接关系

### 2. `prompts.py` - Prompt 管理

提供函数来获取格式化的 prompts：
- `get_director_prompt()`: 获取 Director Agent 的 prompt
- `get_layout_prompt()`: 获取 Layout Agent 的 prompt（支持参数化）

### 3. `agents/base.py` - Agent 基类和工厂

- **BaseAgent**: Agent 基类
- **DeepSeekAgent**: DeepSeek 实现
- **GeminiAgent**: Gemini 实现
- **AgentFactory**: Agent 工厂类，用于创建和管理 Agent 实例

## 使用方法

### 修改 Agent 配置

编辑 `config.py` 中的配置字典：

```python
DIRECTOR_CONFIG = {
    "provider": "deepseek",
    "model": "deepseek-chat",  # 修改模型名称
    "temperature": 0.7,  # 修改温度参数
    # ...
}
```

### 修改 Prompt

编辑 `config.py` 中的 Prompt 模板：

```python
DIRECTOR_SYSTEM_PROMPT = """
你是一个专业的海报设计总监...
"""
```

### 通过环境变量配置

在 `.env` 文件中设置：

```env
DIRECTOR_MODEL=deepseek-chat
DIRECTOR_TEMPERATURE=0.7
LAYOUT_MODEL=gemini-3-flash-preview
CANVAS_WIDTH=1080
CANVAS_HEIGHT=1920
```

### 修改工作流结构

编辑 `config.py` 中的 `WORKFLOW_CONFIG`：

```python
WORKFLOW_CONFIG = {
    "nodes": [
        {"name": "director", "description": "...", "agent": "director"},
        # 添加新节点...
    ],
    "edges": [
        {"from": "director", "to": "asset"},
        # 修改连接关系...
    ],
    "entry_point": "director",
}
```

## 优势

1. **集中管理**: 所有配置集中在一个地方，易于查找和修改
2. **环境变量支持**: 可以通过环境变量动态配置
3. **类型安全**: 使用 TypedDict 和类型提示
4. **易于扩展**: 添加新的 Agent 或修改工作流结构都很简单
5. **测试友好**: 可以轻松替换配置进行测试

## 扩展指南

### 添加新的 Agent

1. 在 `config.py` 中添加配置：
```python
NEW_AGENT_CONFIG = {
    "provider": "openai",
    "model": "gpt-4",
    # ...
}
```

2. 在 `agents/base.py` 中添加实现类（如果需要）

3. 在 `AgentFactory` 中添加创建逻辑

4. 在 `workflow.py` 中添加节点函数

5. 在 `WORKFLOW_CONFIG` 中注册节点

### 修改 Prompt 模板

直接编辑 `config.py` 中的模板字符串即可。如果需要在运行时动态生成，可以在 `prompts.py` 中添加新的函数。

