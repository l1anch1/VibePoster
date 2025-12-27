"""
核心配置 - 环境变量、模型名称、全局常量
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

# === LLM 配置 ===

# DeepSeek 配置
DEEPSEEK_CONFIG = {
    "provider": "deepseek",
    "model": os.getenv("DIRECTOR_MODEL", "deepseek-chat"),
    "api_key": os.getenv("DEEPSEEK_API_KEY"),
    "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    "temperature": float(os.getenv("DIRECTOR_TEMPERATURE", "0.7")),
    "response_format": {"type": "json_object"},
}

# Gemini 配置
GEMINI_CONFIG = {
    "provider": "gemini",
    "model": os.getenv("LAYOUT_MODEL", "gemini-3-flash-preview"),
    "api_key": os.getenv("GEMINI_API_KEY"),
    "base_url": os.getenv("GEMINI_BASE_URL", "https://api.openai-proxy.org/google"),
    "vertexai": True,
    "response_mime_type": "application/json",
}

# === Agent 配置 ===

DIRECTOR_CONFIG = {
    "llm": "deepseek",
    **DEEPSEEK_CONFIG,
}

PROMPTER_CONFIG = {
    "llm": "deepseek",  # Prompter 也使用 DeepSeek 做路由决策
    **DEEPSEEK_CONFIG,
}

LAYOUT_CONFIG = {
    "llm": "gemini",
    **GEMINI_CONFIG,
}

REVIEWER_CONFIG = {
    "llm": "deepseek",  # Reviewer 使用 DeepSeek 做审核
    **DEEPSEEK_CONFIG,
}

ASSET_CONFIG = {
    "provider": "unsplash",  # 使用 Unsplash API
    "unsplash_access_key": os.getenv("UNSPLASH_ACCESS_KEY"),
    "fallback_url": os.getenv("ASSET_FALLBACK_URL", "https://placehold.co/1080x1920/333333/FFF?text=Default+Background"),
}

# === 工作流配置 ===

WORKFLOW_CONFIG = {
    "nodes": [
        {"name": "director", "description": "策划与意图理解", "agent": "director"},
        {"name": "prompter", "description": "视觉调度中心", "agent": "prompter"},
        {"name": "layout", "description": "空间计算与排版", "agent": "layout"},
        {"name": "reviewer", "description": "质量审核", "agent": "reviewer"},
    ],
    "edges": [
        {"from": "director", "to": "prompter"},
        {"from": "prompter", "to": "layout"},
        {"from": "layout", "to": "reviewer"},
        {"from": "reviewer", "to": "layout", "condition": "reject"},  # 条件边：如果审核不通过，回到 layout
        {"from": "reviewer", "to": "END", "condition": "pass"},  # 条件边：如果审核通过，结束
    ],
    "entry_point": "director",
}

# === 画布默认配置 ===

CANVAS_DEFAULTS = {
    "width": int(os.getenv("CANVAS_WIDTH", "1080")),
    "height": int(os.getenv("CANVAS_HEIGHT", "1920")),
    "backgroundColor": os.getenv("CANVAS_BG_COLOR", "#FFFFFF"),
}

# === 错误处理配置 ===

ERROR_FALLBACKS = {
    "director": {
        "title": "生成失败",
        "subtitle": "请检查 API Key",
        "main_color": "#000000",
        "background_color": "#FFFFFF",
        "style_keywords": [],
        "intent": "other",
    },
    "prompter": {
        "background_layer": {
            "type": "image",
            "src": "https://placehold.co/1080x1920/333333/FFF?text=Default+Background",
            "source_type": "stock",
        },
    },
    "layout": {
        "canvas": {"width": 1080, "height": 1920, "backgroundColor": "#FFFFFF"},
        "layers": [],
    },
    "reviewer": {
        "status": "PASS",
        "feedback": "审核通过",
        "issues": [],
    },
}
