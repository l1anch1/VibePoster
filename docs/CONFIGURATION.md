# 配置说明

## 概述

本项目将原本硬编码的 Agent 配置和 Prompts 提取到了配置文件中，使其更易于管理和修改。

## 配置文件结构

### 1. `config.py` - 核心配置文件

包含所有 Agent 的配置、Prompt 模板、工作流配置等。

#### Agent 配置

- **PLANNER_CONFIG**: Planner Agent (规划) 的配置
  - `provider`: 提供商 (如 "deepseek", "openai")
  - `model`: 模型名称
  - `api_key`: API 密钥（从环境变量读取）
  - `base_url`: API 基础 URL
  - `temperature`: 温度参数
  - `response_format`: 响应格式

- **VISUAL_CONFIG**: Visual Agent (感知) 的配置
  - 类似结构，针对 DeepSeek API

- **LAYOUT_CONFIG**: Layout Agent (执行) 的配置
  - 类似结构，针对 Gemini API

- **CRITIC_CONFIG**: Critic Agent (反思) 的配置
  - 类似结构，针对 DeepSeek API

#### 工作流配置

- **WORKFLOW_CONFIG**: 工作流相关配置
  - `MAX_RETRY_TIMES`: 最大重试次数（默认 3）
  - `ENABLE_CRITIC`: 是否启用 Critic Agent（默认 True）

#### 画布配置

- **DEFAULT_CANVAS_WIDTH**: 默认画布宽度（800）
- **DEFAULT_CANVAS_HEIGHT**: 默认画布高度（1200）

#### CORS 配置

- **ALLOWED_ORIGINS**: 允许的跨域来源（默认 `["http://localhost:5173"]`）

#### 错误处理配置

- **ERROR_FALLBACKS**: 各个 Agent 的错误回退值

### 2. `prompts/templates.py` - Prompt 模板文件

包含所有 Agent 的 Prompt 模板字符串。

- **PLANNER_SYSTEM_PROMPT**: Planner Agent 的系统提示词
- **VISUAL_ROUTING_PROMPT**: Visual Agent 的路由决策 Prompt
- **LAYOUT_PROMPT_TEMPLATE**: Layout Agent 的 Prompt 模板
- **CRITIC_PROMPT_TEMPLATE**: Critic Agent 的 Prompt 模板
- **IMAGE_ANALYSIS_PROMPT_TEMPLATE**: OCR + 图像理解的统一 Prompt

### 3. `prompts/manager.py` - Prompt 管理器

提供动态组装 Prompt 的函数。

- `get_planner_prompt(user_prompt, chat_history)`: 获取 Planner Prompt
- `get_visual_routing_prompt(image_count, design_brief)`: 获取 Visual 路由 Prompt
- `get_layout_prompt(design_brief, asset_list, canvas_width, canvas_height, review_feedback)`: 获取 Layout Prompt
- `get_critic_prompt(poster_data)`: 获取 Critic Prompt

## 环境变量

需要在 `.env` 文件中配置以下环境变量：

```bash
# DeepSeek API (用于 Planner, Visual, Critic)
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# Gemini API (用于 Layout)
GEMINI_API_KEY=your_gemini_api_key

# Pexels API (用于素材搜索)
PEXELS_API_KEY=your_pexels_api_key

# 可选：OpenAI API
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1

# 可选：Moonshot API
MOONSHOT_API_KEY=your_moonshot_api_key
MOONSHOT_BASE_URL=https://api.moonshot.cn/v1
```

## 配置示例

### 修改 Agent 配置

如果你想修改某个 Agent 的配置，可以直接编辑 `core/config.py`：

```python
# core/config.py

class PlannerConfig(BaseSettings):
    """Planner Agent 配置"""
    API_KEY: str = Field(..., env="DEEPSEEK_API_KEY")
    BASE_URL: str = Field(..., env="DEEPSEEK_BASE_URL")
    MODEL: str = "deepseek-chat"
    TEMPERATURE: float = 0.7  # 修改温度参数
    RESPONSE_FORMAT: Dict[str, str] = {"type": "json_object"}
```

### 修改 Prompt 模板

如果你想修改某个 Agent 的 Prompt，可以直接编辑 `prompts/templates.py`：

```python
# prompts/templates.py

PLANNER_SYSTEM_PROMPT = """
你是一个专业的海报设计总监。你的任务是将用户的模糊需求转化为结构化的设计简报。

请严格按照以下 JSON 格式输出，不要包含 Markdown 格式（如 ```json ... ```）：
{
    "title": "海报主标题 (简短有力)",
    "subtitle": "副标题 (补充说明)",
    "main_color": "主色调Hex值 (如 #FF0000)",
    "background_color": "背景色Hex值",
    "style_keywords": ["background image keyword 1 in English", "background image keyword 2 in English"],
    "intent": "promotion"  // promotion | invite | cover | other
}
...
"""
```

### 动态组装 Prompt

如果你需要根据上下文动态组装 Prompt，可以使用 `prompts/manager.py` 中的函数：

```python
# 使用示例
from app.prompts.manager import get_layout_prompt

prompt = get_layout_prompt(
    design_brief={"title": "诚聘英才", "subtitle": "共创未来"},
    asset_list={"background_layer": {...}, "foreground_layer": {...}},
    canvas_width=800,
    canvas_height=1200,
    review_feedback=None  # 如果有审核反馈，传入这里
)
```

## 配置最佳实践

### 1. 环境变量优先

所有敏感信息（如 API Key）应该通过环境变量配置，不要硬编码在代码中。

### 2. 使用 Pydantic Settings

使用 Pydantic Settings V2 管理配置，提供类型检查和验证。

```python
from pydantic_settings import BaseSettings

class MyConfig(BaseSettings):
    api_key: str = Field(..., env="MY_API_KEY")
    
    class Config:
        env_file = ".env"
```

### 3. 配置分层

- **核心配置** (`core/config.py`): 系统级配置
- **Prompt 模板** (`prompts/templates.py`): Prompt 字符串
- **Prompt 管理** (`prompts/manager.py`): 动态组装逻辑

### 4. 提供默认值

为所有配置提供合理的默认值，减少配置负担。

```python
class WorkflowConfig(BaseSettings):
    MAX_RETRY_TIMES: int = 3  # 默认值
    ENABLE_CRITIC: bool = True  # 默认值
```

### 5. 文档化配置

为每个配置项添加注释，说明其用途和默认值。

```python
class Settings(BaseSettings):
    """系统配置"""
    
    # LLM 配置
    planner: PlannerConfig  # Planner Agent 配置
    visual: VisualConfig    # Visual Agent 配置
    
    # 工作流配置
    MAX_RETRY_TIMES: int = 3  # 最大重试次数（默认 3）
```

## 常见问题

### Q: 如何切换 LLM 提供商？

A: 修改对应 Agent 的配置，例如将 Planner 从 DeepSeek 切换到 OpenAI：

```python
# core/config.py

class PlannerConfig(BaseSettings):
    API_KEY: str = Field(..., env="OPENAI_API_KEY")  # 改为 OpenAI
    BASE_URL: str = Field(..., env="OPENAI_BASE_URL")
    MODEL: str = "gpt-4"  # 改为 GPT-4
    TEMPERATURE: float = 0.7
```

### Q: 如何调整 Agent 的温度参数？

A: 直接修改配置中的 `TEMPERATURE` 字段：

```python
class PlannerConfig(BaseSettings):
    TEMPERATURE: float = 0.5  # 降低温度，提高确定性
```

### Q: 如何禁用 Critic Agent？

A: 修改工作流配置：

```python
class WorkflowConfig(BaseSettings):
    ENABLE_CRITIC: bool = False  # 禁用 Critic
```

### Q: 如何增加重试次数？

A: 修改工作流配置：

```python
class WorkflowConfig(BaseSettings):
    MAX_RETRY_TIMES: int = 5  # 增加到 5 次
```

## 总结

- **集中管理**：所有配置集中在 `core/config.py`
- **环境变量**：敏感信息通过环境变量配置
- **Prompt 分离**：Prompt 模板独立管理
- **易于修改**：修改配置不需要改动业务代码
- **类型安全**：使用 Pydantic 提供类型检查

---

**最后更新**: 2025-01-01

