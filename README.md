# VibePoster

AI-powered poster design system. Multi-agent orchestration + Knowledge Graph + RAG brand knowledge + image understanding/generation + online editor, delivering layered PSD source files.

## Architecture

```
User Input → Planner → Visual → Layout → Critic → Poster
                │          │        │        │
            Intent      Image    Pixel     Quality
           KG+RAG+LLM  OCR+Gen  DSL Cmds  Dual Review
                                            ↓ REJECT
                                         Retry Layout
```

- **Planner**: 4-Skill pipeline (IntentParse → KG inference → RAG brand context → LLM design brief)
- **Visual**: Image understanding + asset search/generation (Pexels / Flux text-to-image)
- **Layout**: Pixel-precise DSL instructions; decoration styles auto-driven by KG
- **Critic**: JSON structure review + visual rendering review, auto-retry on failure

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | React 19 + TypeScript + Vite 7 + Tailwind CSS 4 |
| Backend Engine | Python + FastAPI + LangGraph |
| Render Service | Node.js + Express + Sharp + ag-psd |
| AI Models | DeepSeek / Gemini / GPT-4o-mini / Flux |

## Quick Start

```bash
# 1. Configure
cp backend/engine/env.template backend/engine/.env
# Edit .env with your API keys (5 required — see checklist at bottom of env.template)

# 2. Docker
docker-compose up -d --build

# Or local dev (3 terminals)
cd backend/engine && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000
cd backend/render && npm install && node src/server.js
cd frontend && npm install && npm run dev
```

| Service | Dev Port | Prod Port |
|---------|----------|-----------|
| Frontend | 5173 | 80 (Nginx) |
| Engine | 8000 | 8000 |
| Render | 3000 | 3000 |

## Project Structure

```
VibePoster/
├── frontend/              # React SPA + online editor
├── backend/
│   ├── engine/            # Python FastAPI — Agent engine
│   │   ├── app/
│   │   │   ├── agents/    # 4 Agents
│   │   │   ├── skills/    # Semantic Kernel-style skill orchestration
│   │   │   ├── knowledge/ # KG + RAG
│   │   │   ├── prompts/   # Prompt templates
│   │   │   ├── services/  # Business services + DSL parser
│   │   │   └── workflow/  # LangGraph orchestration
│   │   └── tests/         # pytest tests
│   └── render/            # Node.js — PNG/JPG/PSD export
├── docs/                  # Architecture docs, design system
└── CLAUDE.md              # Claude Code project guide
```

## Docs

See `CLAUDE.md` for developer guide, and `docs/` for architecture, configuration, and design system references.

## License

(c) 2025 Graduation Project by Anchi Li
