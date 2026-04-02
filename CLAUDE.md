# VibePoster

AI 驱动的海报生成系统。多 Agent 编排 + 知识图谱（KG）+ RAG 品牌知识库 + 图像理解/生成 + 在线编辑器。

## 项目结构

```
VibePoster/
├── frontend/          # React 19 + TypeScript + Vite 7 + Tailwind CSS 4
├── backend/
│   ├── engine/        # Python FastAPI — AI Agent 引擎（LangGraph 编排）
│   └── render/        # Node.js Express — PNG/JPG/PSD 导出服务
└── docs/              # 架构文档
```

## 快速启动

### Docker（推荐）

```bash
cp backend/engine/env.template backend/engine/.env
# 编辑 .env 填入 API Keys
docker-compose up -d --build                                          # 生产
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up     # 开发（热更新）
```

### 本地开发（三个终端）

```bash
# Terminal 1: Engine
cd backend/engine && pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Render
cd backend/render && npm install && node src/server.js

# Terminal 3: Frontend
cd frontend && npm install && npm run dev
```

| 服务 | 开发端口 | 生产端口 |
|------|---------|---------|
| Frontend (Vite) | 5173 | 80 (Nginx) |
| Engine (FastAPI) | 8000 | 8000 |
| Render (Express) | 3000 | 3000 |

## 环境变量

唯一配置文件：`backend/engine/.env`（模板：`backend/engine/env.template`）

必填 API Keys：`PLANNER_API_KEY`、`VISUAL_API_KEY`、`LAYOUT_API_KEY`、`CRITIC_API_KEY`，以及 `VISUAL_FLUX_API_KEY` 或 `VISUAL_PEXELS_API_KEY` 至少一个。

每个 Agent 支持独立配置：`{AGENT}_PROVIDER`、`{AGENT}_API_KEY`、`{AGENT}_BASE_URL`、`{AGENT}_MODEL`、`{AGENT}_TEMPERATURE`。

前端环境变量通过 Vite 注入：`VITE_API_URL`（默认 `http://localhost:8000`）、`VITE_RENDER_URL`（默认 `http://localhost:3000`）。

## Agent 架构

```
Planner → Visual → Layout → Critic → [retry Layout 或 END]
```

- **Planner**: 4-Skill 编排（IntentParse → DesignRule/KG → BrandContext/RAG → DesignBrief/LLM）
- **Visual**: 图像理解 + 素材搜索/生成（Pexels/Flux）
- **Layout**: DSL 指令生成（绝对坐标），KG 驱动字体和装饰风格
- **Critic**: 双路审核（JSON 结构 + 视觉渲染），失败重试 Layout（最多 2 次）

### 知识图谱（KG）

位于 `backend/engine/app/knowledge/kg/`。三层语义推理链：

```
Entry (Industry/Vibe) → Emotion → Visual Elements + Decorations
```

数据文件：`kg/data/kg_rules.json`。7 个 Emotion、6 个 Industry、5 个 Vibe。

### DSL 命令

Layout LLM 输出 DSL 指令，DSL Parser 转换为图层：

| 命令 | 产出类型 | 说明 |
|------|---------|------|
| `add_image` | image | 图片图层 |
| `add_title` / `add_subtitle` / `add_text` / `add_cta` | text | 文本图层 |
| `add_divider` / `add_overlay` / `add_shape` | rect | 装饰图层（KG 驱动样式） |

装饰类命令的视觉属性由 DSL Parser 从 KG 推理结果自动填充，LLM 只需指定位置。

### 图层类型

- `text`: 文本（content, fontSize, color, fontFamily, textAlign, fontWeight）
- `image`: 图片（src）
- `rect`: 形状（subtype: rect/divider/overlay, backgroundColor, borderRadius, borderColor, borderWidth, gradient）

## API 路由

### Engine（FastAPI, :8000）

- `POST /api/step/plan` — 意图理解，返回设计简报
- `POST /api/step/assets` — 素材搜索（支持 FormData 图片上传）
- `POST /api/step/layouts` — 布局生成 + 审核（180s 超时）
- `POST /api/step/finalize` — 确认选择
- `POST /api/brand/upload` — 品牌文档上传（RAG）
- `GET /health` — 健康检查

### Render（Express, :3000）

- `POST /api/render/image?format=png|jpg&quality=95` — 生成 PNG/JPG
- `POST /api/render/psd` — 生成 PSD（ZIP 包含 PSD + 字体 README）
- `GET /health` — 健康检查

## 测试

```bash
cd backend/engine
pytest                          # 全部测试
pytest -m unit                  # 单元测试
pytest -m api                   # API 测试
pytest -m "not slow"            # 跳过慢速测试
pytest --cov=app                # 覆盖率
```

前端和 Render 服务暂无测试套件。

## 代码规范

- **Python**: Black 格式化（line-length=100），Pydantic v2 模型
- **TypeScript**: ESLint + react-hooks/react-refresh 插件
- **前端设计**: iOS 液态玻璃风格，详见 `docs/DESIGN_SYSTEM.md`
- **Commit 风格**: `feat:` / `refactor:` / `polish:` / `fix:` 前缀

## 关键文件索引

| 领域 | 文件 |
|------|------|
| Agent 编排 | `backend/engine/app/workflow/orchestrator.py` |
| Agent 实现 | `backend/engine/app/agents/{planner,visual,layout,critic}.py` |
| Prompt 模板 | `backend/engine/app/prompts/{planner,layout,visual,critic}.py` |
| KG 数据 | `backend/engine/app/knowledge/kg/data/kg_rules.json` |
| KG 推理 | `backend/engine/app/knowledge/kg/inference.py` |
| Skills | `backend/engine/app/skills/{intent_parse,design_rule,brand_context,design_brief}/` |
| DSL 解析 | `backend/engine/app/services/renderer/dsl_parser.py` |
| 字体注册 | `backend/engine/app/services/renderer/font_registry.py` |
| 数据模型 | `backend/engine/app/models/poster.py` |
| 配置中心 | `backend/engine/app/core/config.py` |
| 前端类型 | `frontend/src/types/PosterSchema.ts` |
| 编辑器 | `frontend/src/components/editor/` |
| 状态管理 | `frontend/src/hooks/useEditorState.ts` |
| PNG/JPG 导出 | `backend/render/src/services/imageGenerator.js` |
| PSD 导出 | `backend/render/src/services/psdGenerator.js` |
