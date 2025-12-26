from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .schemas import PosterData
from .agents.director import run_director_agent  # <--- 引入刚才写的智能体

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 为了方便开发，先允许所有来源
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/generate", response_model=PosterData)
async def generate_poster(prompt: str):
    # 1. 调用策划智能体 (Director Agent)
    # 它会返回: { "title": "...", "subtitle": "...", "main_color": "..." }
    design_brief = run_director_agent(prompt)

    # 2. 组装数据 (模拟 Layout Agent 的工作)
    # 暂时把 AI 想出来的字，填到固定的位置上，让前端能先跑通

    return {
        "canvas": {
            "width": 1080,
            "height": 1920,
            "backgroundColor": design_brief.get("background_color", "#fff"),
        },
        "layers": [
            # 背景层 (暂时用纯色或占位图)
            {
                "id": "bg",
                "type": "image",
                "name": "Background",
                "x": 0,
                "y": 0,
                "width": 1080,
                "height": 1920,
                "src": "https://placehold.co/1080x1920/png?text=Background",
                "opacity": 1.0,
                "rotation": 0,
            },
            # 主标题层 (内容和颜色由 AI 决定！)
            {
                "id": "title",
                "type": "text",
                "name": "Title",
                "x": 100,
                "y": 400,
                "width": 880,
                "height": 200,
                "content": design_brief.get("title", "默认标题"),
                "fontSize": 120,
                "color": design_brief.get("main_color", "#000"),
                "fontFamily": "Yuanti TC",
                "textAlign": "center",
                "fontWeight": "bold",
                "rotation": 0,
                "opacity": 1.0,
            },
            # 副标题层
            {
                "id": "subtitle",
                "type": "text",
                "name": "Subtitle",
                "x": 140,
                "y": 600,
                "width": 800,
                "height": 100,
                "content": design_brief.get("subtitle", "默认副标题"),
                "fontSize": 60,
                "color": design_brief.get("main_color", "#333"),  # 跟随主色
                "fontFamily": "Yuanti TC",
                "textAlign": "center",
                "fontWeight": "normal",
                "rotation": 0,
                "opacity": 0.8,
            },
        ],
    }
