# VibePoster - AI 海报设计系统

一个能听懂人话、能看懂图片、会自我反思的海报设计系统。支持文生图、图生图以及复杂的双图融合（换背景/换人）场景，最终交付可分层编辑的 PSD 源文件。

## 📋 系统架构

### 四大智能体架构 (The 4-Agent Architecture)

1. 🧠 **Planner (规划)**：理解意图，写文案，定色调
2. 🎨 **Visual (感知)**：处理图片（抠图、分析、搜图），是"视觉感知中心"
3. 📐 **Layout (执行)**：计算坐标，生成图层数据
4. ⚖️ **Critic (反思)**：基于规则和视觉冲突检测，进行自修正

### 技术栈

- **前端**: React + TypeScript + Vite
- **后端引擎**: Python + FastAPI + LangGraph
- **渲染服务**: Node.js + Express + ag-psd
- **AI 模型**: DeepSeek (Planner/Visual/Critic) + Gemini (Layout)

## 🚀 快速开始

### 方式一：Docker 部署（推荐）

最简单的部署方式，一键启动所有服务。

- Docker 20.10+
- Docker Compose 2.0+

#### 部署步骤

```bash
# 1. 克隆项目
git clone <repository-url>
cd VibePoster

# 2. 配置环境变量
cp backend/engine/env.template backend/engine/.env
# 编辑 backend/engine/.env 文件，填入你的 API Keys

# 3. 构建并启动所有服务
docker-compose up -d --build

# 4. 查看服务状态
docker-compose ps

# 5. 查看日志
docker-compose logs -f
```

#### 访问应用

- **前端**: <http://localhost>
- **后端 API**: <http://localhost:8000>
- **渲染服务**: <http://localhost:3000>

#### 常用命令

```bash
# 停止所有服务
docker-compose down

# 重新构建并启动
docker-compose up -d --build

# 查看特定服务日志
docker-compose logs -f engine

# 进入容器调试
docker exec -it vibeposter-engine bash
```

---

### 方式二：本地开发

#### 前置要求

- Python 3.13+ (推荐使用 venv)
- Node.js 18+
- npm 或 yarn

### 1. 环境配置

#### 后端引擎 (Python)

```bash
# 进入后端引擎目录
cd backend/engine

# 创建虚拟环境（如果还没有）
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 安装 Python 依赖
pip install fastapi uvicorn langgraph openai google-genai python-dotenv pydantic pillow numpy

# 安装图像处理库（可选，用于抠图功能）
pip install rembg[new]

# 复制 .env.example 为 .env 并填写你的 API Key
cp .env.example .env
# 然后编辑 .env 文件，填入你的 API Key

```

#### 渲染服务 (Node.js)

```bash
# 进入渲染服务目录
cd backend/render

# 安装依赖
npm install
```

#### 前端 (React)

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install
```

### 2. 启动服务

项目需要同时运行三个服务：

#### 终端 1: 启动后端引擎 (FastAPI)

```bash
cd backend/engine
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 启动 FastAPI 服务（端口 8000）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 终端 2: 启动渲染服务 (Node.js)

```bash
cd backend/render

# 启动 Express 服务（端口 3000）
node src/server.js
```

#### 终端 3: 启动前端 (Vite)

```bash
cd frontend

# 启动开发服务器（默认端口 5173）
npm run dev
```

### 3. 访问应用

打开浏览器访问：`http://localhost:5173`

## 📁 项目结构

```plaintext
VibePoster/
├── frontend/                 # React 前端
│   ├── src/
│   │   ├── components/      # 组件
│   │   ├── types/           # TypeScript 类型定义
│   │   └── App.tsx          # 主应用
│   └── package.json
│
├── backend/
│   ├── engine/              # Python 后端引擎
│   │   ├── app/
│   │   │   ├── core/        # 核心配置和状态
│   │   │   ├── agents/      # 四个智能体
│   │   │   ├── tools/       # 工具函数（抠图、素材库）
│   │   │   ├── prompts/    # Prompt 管理
│   │   │   ├── workflow.py  # LangGraph 工作流
│   │   │   └── main.py      # FastAPI 入口
│   │   └── venv/            # Python 虚拟环境
│   │
│   └── render/              # Node.js 渲染服务
│       ├── src/
│       │   └── server.js    # PSD 生成服务
│       └── package.json
│
└── README.md
```

## 🔧 配置说明

### 端口配置

- **前端**: `http://localhost:5173` (Vite 默认)
- **后端引擎**: `http://localhost:8000` (FastAPI)
- **渲染服务**: `http://localhost:3000` (Express)

如需修改端口，请更新：

- 前端：修改 `vite.config.ts` 或使用 `npm run dev -- --port <端口>`
- 后端引擎：修改 `uvicorn` 命令中的 `--port` 参数
- 渲染服务：修改 `backend/render/src/server.js` 中的 `PORT` 常量

## 🎯 使用说明

### 基本流程

1. **输入设计需求**：在左侧控制区输入文字描述
2. **上传图片**（可选）：
   - 上传背景图：作为海报背景
   - 上传人物图：系统会自动抠图并合成
3. **选择画布尺寸**：竖版或横版，三种尺寸可选
4. **生成海报**：点击"开始融合生成"按钮
5. **下载 PSD**：点击下载按钮，获取可编辑的 PSD 文件

### 工作流说明

（待补充）

## 🛠️ 开发指南

### 添加新的 Agent

1. 在 `backend/engine/app/agents/` 创建新文件
2. 实现 `BaseAgent` 子类
3. 在 `agents/base.py` 的 `AgentFactory` 中添加获取方法
4. 在 `core/config.py` 中添加配置
5. 在 `workflow.py` 中注册节点

### 修改 Prompt

- Prompt 模板：`backend/engine/app/prompts/templates.py`
- Prompt 管理：`backend/engine/app/prompts/manager.py`

### 修改配置

所有配置集中在：`backend/engine/app/core/config.py`

## 🐛 故障排除

### 后端引擎启动失败

- 检查 Python 版本（需要 3.13+）
- 确认虚拟环境已激活
- 检查 `.env` 文件中的 API Key 是否正确
- 确认所有依赖已安装：`pip list`

### 渲染服务启动失败

- 检查 Node.js 版本（需要 18+）
- 确认依赖已安装：`npm list`
- 检查端口 3000 是否被占用

### 前端无法连接后端

- 确认三个服务都已启动
- 检查浏览器控制台的错误信息
- 确认 API 地址配置正确

### 抠图功能不工作

- 确认已安装 `rembg`：`pip install rembg[new]`
- 如果未安装，系统会使用占位实现（返回原图）

## 📄 许可证

© 2025 Graduation Project by Anchi Li
