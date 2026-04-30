# VibePoster

AI-powered poster design system. Multi-agent orchestration + Knowledge Graph (KG) + RAG brand knowledge + image understanding/generation + online editor.

## Project Structure

```
VibePoster/
├── frontend/          # React 19 + TypeScript + Vite 7 + Tailwind CSS 4
├── backend/
│   ├── engine/        # Python FastAPI — AI Agent engine (LangGraph orchestration)
│   └── render/        # Node.js Express — PNG/JPG/PSD export service
└── docs/              # Architecture docs
```

## Quick Start

### Docker (recommended)

```bash
cp backend/engine/env.template backend/engine/.env
# Edit .env with your API keys
docker-compose up -d --build                                          # production
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up     # dev (hot reload)
```

### Local Development (3 terminals)

```bash
# Terminal 1: Engine
cd backend/engine && uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Render
cd backend/render && npm install && node src/server.js

# Terminal 3: Frontend
cd frontend && npm install && npm run dev
```

| Service | Dev Port | Prod Port |
|---------|----------|-----------|
| Frontend (Vite) | 5173 | 80 (Nginx) |
| Engine (FastAPI) | 8000 | 8000 |
| Render (Express) | 3000 | 3000 |

## Environment Variables

Single config file: `backend/engine/.env` (template: `backend/engine/env.template`)

Required API keys: `PLANNER_API_KEY`, `VISUAL_API_KEY`, `LAYOUT_API_KEY`, `CRITIC_API_KEY`, plus at least one of `VISUAL_FLUX_API_KEY` or `VISUAL_PEXELS_API_KEY`.

Each agent supports independent config: `{AGENT}_PROVIDER`, `{AGENT}_API_KEY`, `{AGENT}_BASE_URL`, `{AGENT}_MODEL`, `{AGENT}_TEMPERATURE`.

Frontend env vars injected via Vite: `VITE_API_URL` (default `http://localhost:8000`), `VITE_RENDER_URL` (default `http://localhost:3000`).

## Agent Architecture

```
Planner → Visual → Layout → Critic → [retry Layout or END]
```

- **Planner**: 4-Skill pipeline (IntentParse → DesignRule/KG → BrandContext/RAG → DesignBrief/LLM)
- **Visual**: Image understanding + asset search/generation (Pexels/Flux)
- **Layout**: Semantic DSL generation + OOP layout engine (7 strategies, dynamic coordinate computation)
- **Critic**: Dual-path review (JSON structure + visual rendering), retries Layout on failure (up to 2x)

### Knowledge Graph (KG)

Located at `backend/engine/app/knowledge/kg/`. Five-layer design ontology with explicit semantic triples:

```
Layer 0: Domain Entry    — Industry(8) / Vibe(7)
Layer 1: Emotion         — 9 emotions (semantic hub)
Layer 2: Visual Strategy — ColorStrategy(11) / TypographyStyle(5) / LayoutPattern(11) / DecorationTheme(6)
```

Relations: `EMBODIES` · `EVOKES` · `AVOIDS` · `CONFLICTS_WITH` (119 edges total).
Inference: multi-hop graph traversal + weighted aggregation + conflict resolution + trace recording.

Data file: `kg/data/ontology.json`. 57 nodes, 119 edges.

### OOP Layout Engine

Located at `backend/engine/app/core/layout/`. CSS Flexbox-like container + component model:

```
Element (ABC)
├── TextBlock   — auto-calculates height from content + font_size
├── ImageBlock  — aspect-ratio-aware resize
└── ShapeBlock  — divider / overlay / rect decorations
Container (extends Element)
├── VerticalContainer  — top-to-bottom flow, auto y-spacing
└── HorizontalContainer — left-to-right flow
```

### DSL Commands + Layout Strategies

LLM outputs **semantic DSL** (no coordinates). `LayoutBuilder` maps `layout_strategy` to OOP containers:

| Strategy | Description | Content Region |
|----------|-------------|---------------|
| `top_text` | Title top, visual below | 6%–55% |
| `centered` | Vertically centered | 25%–75% |
| `bottom_heavy` | Content at bottom | 55%–95% |
| `left_aligned` | Magazine-style left | 10%–90% |
| `diagonal` | Title top-left, CTA bottom-right | split regions |
| `big_title` | 1.5× title scale | 20%–80% |
| `split_vertical` | Top half / bottom half | split regions |

DSL commands (no x/y/width/height):

| Command | Output Type | Description |
|---------|-------------|-------------|
| `add_image` | image | Background (fullscreen) / subject image |
| `add_title` / `add_subtitle` / `add_text` / `add_cta` | text | Text layers (auto-height) |
| `add_divider` / `add_overlay` / `add_shape` | rect | Decoration layers (KG-driven styles) |

Coordinate pipeline: `LLM semantic DSL → LayoutBuilder → VerticalContainer.arrange() → flat element list → SchemaConverter → PosterData`.

### Layer Types

- `text`: content, fontSize, color, fontFamily, textAlign, fontWeight
- `image`: src
- `rect`: subtype (rect/divider/overlay), backgroundColor, borderRadius, borderColor, borderWidth, gradient

## API Routes

### Engine (FastAPI, :8000)

- `POST /api/step/plan` — Intent understanding, returns design brief
- `POST /api/step/assets` — Asset search (accepts FormData with image uploads)
- `POST /api/step/layouts` — Layout generation + review (180s timeout)
- `POST /api/step/finalize` — Confirm selection
- `POST /api/brand/upload` — Upload brand documents (RAG)
- `GET /health` — Health check

### Render (Express, :3000)

- `POST /api/render/image?format=png|jpg&quality=95` — Generate PNG/JPG
- `POST /api/render/psd` — Generate PSD (ZIP with PSD + font README)
- `GET /health` — Health check

## Testing

```bash
cd backend/engine
pytest                          # all tests
pytest -m unit                  # unit tests
pytest -m api                   # API tests
pytest -m "not slow"            # skip slow tests
pytest --cov=app                # coverage
```

Frontend and Render service have no test suites yet.

## Code Conventions

- **Python**: Black formatter (line-length=100), Pydantic v2 models
- **TypeScript**: ESLint + react-hooks/react-refresh plugins
- **Frontend design**: iOS liquid glass style, see `docs/DESIGN_SYSTEM.md`
- **Commits**: `feat:` / `refactor:` / `polish:` / `fix:` prefixes

## Key File Index

| Area | File |
|------|------|
| Agent orchestration | `backend/engine/app/workflow/orchestrator.py` |
| Agent implementations | `backend/engine/app/agents/{planner,visual,layout,critic}.py` |
| Prompt templates | `backend/engine/app/prompts/{planner,layout,visual,critic}.py` |
| KG ontology data | `backend/engine/app/knowledge/kg/data/ontology.json` |
| KG inference | `backend/engine/app/knowledge/kg/inference.py` |
| Skills | `backend/engine/app/skills/{intent_parse,design_rule,brand_context,design_brief}/` |
| OOP layout engine | `backend/engine/app/core/layout/` |
| Layout builder | `backend/engine/app/services/renderer/layout_builder.py` |
| DSL parser (delegate) | `backend/engine/app/services/renderer/dsl_parser.py` |
| Font registry | `backend/engine/app/services/renderer/font_registry.py` |
| Data models | `backend/engine/app/models/poster.py` |
| Config | `backend/engine/app/core/config.py` |
| Frontend types | `frontend/src/types/PosterSchema.ts` |
| Editor | `frontend/src/components/editor/` |
| State management | `frontend/src/hooks/useEditorState.ts` |
| PNG/JPG export | `backend/render/src/services/imageGenerator.js` |
| PSD export | `backend/render/src/services/psdGenerator.js` |
