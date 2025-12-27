"""
FastAPI 入口
"""
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

# 引入核心工作流 (LangGraph)
from .workflow import app_workflow

# 引入工具
from .tools.vision import image_to_base64

app = FastAPI()

# 配置跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/generate_multimodal")
async def generate_multimodal(
    prompt: str = Form(...),
    image_person: Optional[UploadFile] = File(None),
    image_bg: Optional[UploadFile] = File(None),
):
    print(f"🚀 收到设计请求: {prompt}")

    # === 处理用户上传的图片 ===
    user_images = []
    
    # 处理背景图
    if image_bg:
        print("📸 检测到用户上传了背景图...")
        file_bytes = await image_bg.read()
        user_images.append({
            "type": "background",
            "data": file_bytes,
        })
    
    # 处理人物图
    if image_person:
        print("📸 检测到用户上传了人物图...")
        file_bytes = await image_person.read()
        user_images.append({
            "type": "person",
            "data": file_bytes,
        })

    # === 启动 LangGraph 编排 ===
    print("🤖 启动 Agent 工作流 (Director -> Prompter -> Layout -> Reviewer)...")

    initial_state = {
        "user_prompt": prompt,
        "chat_history": None,  # 暂时不支持多轮对话
        "user_images": user_images if user_images else None,
        "design_brief": {},
        "asset_list": None,
        "selected_asset": None,  # 兼容旧字段
        "final_poster": {},
        "review_feedback": None,
        "_retry_count": 0,  # 重试计数器
    }

    # 运行工作流
    final_state = app_workflow.invoke(initial_state)

    print("🏁 生成结束，返回 JSON 数据。")
    return final_state["final_poster"]


# 兼容旧接口 (纯文字模式)
@app.post("/api/generate")
async def generate_simple(prompt: str):
    """兼容旧接口 (纯文字模式)"""
    # 复用同一个工作流
    state = app_workflow.invoke(
        {
            "user_prompt": prompt,
            "chat_history": None,
            "user_images": None,
            "design_brief": {},
            "asset_list": None,
            "selected_asset": None,
            "final_poster": {},
            "review_feedback": None,
            "_retry_count": 0,
        }
    )
    return state["final_poster"]
