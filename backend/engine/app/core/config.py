"""
核心配置 - VibePoster

设计原则：
1. 每个 Agent 拥有独立的完整配置（API_KEY, BASE_URL, MODEL, TEMPERATURE）
2. 通过环境变量前缀隔离各 Agent 配置（PLANNER_*, VISUAL_*, LAYOUT_*, CRITIC_*）
"""

import os
from typing import Dict, Any, List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class PlannerAgentConfig(BaseSettings):
    """
    Planner Agent 配置
    """

    model_config = SettingsConfigDict(env_prefix="PLANNER_", env_file=".env", extra="ignore")

    # LLM 配置
    PROVIDER: str = Field(
        default="deepseek", description="LLM 提供商：deepseek, openai, gemini, moonshot"
    )
    API_KEY: str = Field(..., description="Planner Agent 的 API Key")
    BASE_URL: str = Field(
        default="https://api.deepseek.com", description="Planner Agent 的 API Base URL"
    )
    MODEL: str = Field(default="deepseek-chat", description="Planner Agent 使用的模型")
    TEMPERATURE: float = Field(
        default=0.7, ge=0.0, le=2.0, description="Planner Agent 的温度参数（0.0-2.0）"
    )

    # Planner 专用参数
    DEFAULT_INTENT: str = Field(default="poster", description="默认意图类型")


class VisualAgentConfig(BaseSettings):
    """
    Visual Agent 配置
    """

    model_config = SettingsConfigDict(env_prefix="VISUAL_", env_file=".env", extra="ignore")

    # LLM 配置（用于 OCR 和图像理解）
    PROVIDER: str = Field(
        default="deepseek", description="LLM 提供商：deepseek, openai, gemini, moonshot"
    )
    API_KEY: str = Field(..., description="Visual Agent 的 API Key")
    BASE_URL: str = Field(
        default="https://api.deepseek.com", description="Visual Agent 的 API Base URL"
    )
    MODEL: str = Field(
        default="deepseek-chat", description="Visual Agent 使用的模型（需支持 Vision）"
    )
    TEMPERATURE: float = Field(
        default=0.2, ge=0.0, le=2.0, description="Visual Agent 的温度参数（较低以确保准确性）"
    )

    # Visual 专用参数
    DEFAULT_POSITION: str = Field(default="center_bottom", description="前景图层默认位置")
    PEXELS_API_KEY: str = Field(..., description="Pexels 素材库 API Key")


class LayoutAgentConfig(BaseSettings):
    """
    Layout Agent 配置
    """

    model_config = SettingsConfigDict(env_prefix="LAYOUT_", env_file=".env", extra="ignore")

    # LLM 配置
    PROVIDER: str = Field(
        default="deepseek", description="LLM 提供商：deepseek, openai, gemini, moonshot"
    )
    API_KEY: str = Field(..., description="Layout Agent 的 API Key")
    BASE_URL: str = Field(
        default="https://api.deepseek.com", description="Layout Agent 的 API Base URL"
    )
    MODEL: str = Field(
        default="deepseek-reasoner", description="Layout Agent 使用的模型（推荐使用推理模型）"
    )
    TEMPERATURE: float = Field(
        default=0.1, ge=0.0, le=2.0, description="Layout Agent 的温度参数（非常低以确保精确性）"
    )

    # Layout 模式配置
    USE_DSL_MODE: bool = Field(
        default=True, 
        description="是否使用 DSL 模式（OOP 布局引擎）。True=DSL模式，False=传统JSON模式"
    )
    
    # Layout 专用参数（排版约束）
    FG_MAX_WIDTH_RATIO: float = Field(
        default=0.5, ge=0.1, le=1.0, description="前景图层最大宽度占画布比例"
    )
    FG_MAX_HEIGHT_RATIO: float = Field(
        default=0.6, ge=0.1, le=1.0, description="前景图层最大高度占画布比例"
    )
    Z_INDEX_BG: int = Field(default=0, description="背景图层 z-index")
    Z_INDEX_FG: int = Field(default=10, description="前景图层 z-index")
    Z_INDEX_TEXT: int = Field(default=20, description="文字图层 z-index")


class CriticAgentConfig(BaseSettings):
    """
    Critic Agent 配置
    """

    model_config = SettingsConfigDict(env_prefix="CRITIC_", env_file=".env", extra="ignore")

    # LLM 配置
    PROVIDER: str = Field(
        default="deepseek", description="LLM 提供商：deepseek, openai, gemini, moonshot"
    )
    API_KEY: str = Field(..., description="Critic Agent 的 API Key")
    BASE_URL: str = Field(
        default="https://api.deepseek.com", description="Critic Agent 的 API Base URL"
    )
    MODEL: str = Field(
        default="deepseek-reasoner", description="Critic Agent 使用的模型（推荐使用推理模型）"
    )
    TEMPERATURE: float = Field(
        default=0.0, ge=0.0, le=2.0, description="Critic Agent 的温度参数（0.0 确保严格审核）"
    )

    # Critic 专用参数
    MAX_RETRY_COUNT: int = Field(default=2, ge=0, le=5, description="最大重试次数")
    DEFAULT_STATUS: str = Field(default="PASS", description="默认审核状态")


class CanvasConfig(BaseSettings):
    """画布默认配置"""

    model_config = SettingsConfigDict(env_prefix="CANVAS_", env_file=".env", extra="ignore")

    WIDTH: int = Field(default=1080, ge=100, le=10000, description="默认画布宽度")
    HEIGHT: int = Field(default=1920, ge=100, le=10000, description="默认画布高度")
    BG_COLOR: str = Field(default="#FFFFFF", description="默认背景颜色")


class KGConfig(BaseSettings):
    """Knowledge Graph 配置"""

    model_config = SettingsConfigDict(env_prefix="KG_", env_file=".env", extra="ignore")

    RULES_FILE: str = Field(
        default="./app/knowledge/kg/data/kg_rules.json",
        description="KG 规则数据文件路径"
    )


class RAGConfig(BaseSettings):
    """RAG 知识库配置"""

    model_config = SettingsConfigDict(env_prefix="RAG_", env_file=".env", extra="ignore")

    # 存储配置
    PERSIST_DIRECTORY: str = Field(
        default="./data/chroma_db", 
        description="ChromaDB 持久化目录"
    )
    
    # 默认数据配置
    LOAD_DEFAULT_DATA: bool = Field(
        default=True, 
        description="是否加载默认品牌数据"
    )
    DEFAULT_DATA_PATH: str = Field(
        default="./app/knowledge/rag/data/default_brand_knowledge.json",
        description="默认品牌数据文件路径"
    )
    
    # 模型配置
    EMBEDDING_MODEL: str = Field(
        default="paraphrase-multilingual-MiniLM-L12-v2",
        description="句子嵌入模型名称"
    )
    USE_CHROMADB: bool = Field(
        default=False,
        description="是否使用 ChromaDB（否则使用内存存储）"
    )


class CORSConfig(BaseSettings):
    """CORS 配置"""

    model_config = SettingsConfigDict(env_prefix="CORS_", env_file=".env", extra="ignore")

    ALLOW_ORIGINS: str = Field(
        default="http://localhost,http://localhost:80,http://localhost:3000,http://localhost:5173,http://localhost:5174,http://127.0.0.1,http://127.0.0.1:3000,http://127.0.0.1:5173,http://127.0.0.1:5174,*",
        description="允许的来源列表（逗号分隔）",
    )
    ALLOW_METHODS: str = Field(
        default="GET,POST,PUT,DELETE,OPTIONS", description="允许的 HTTP 方法（逗号分隔）"
    )
    ALLOW_HEADERS: str = Field(
        default="Content-Type,Authorization", description="允许的请求头（逗号分隔）"
    )
    ALLOW_CREDENTIALS: bool = Field(default=False, description="是否允许携带凭证")

    @property
    def allow_origins_list(self) -> List[str]:
        """将逗号分隔的字符串转换为列表"""
        # 开发环境直接返回通配符
        return ["*"]

    @property
    def allow_methods_list(self) -> List[str]:
        """将逗号分隔的字符串转换为列表"""
        if not self.ALLOW_METHODS:
            return ["GET", "POST"]
        return [method.strip() for method in self.ALLOW_METHODS.split(",") if method.strip()]

    @property
    def allow_headers_list(self) -> List[str]:
        """将逗号分隔的字符串转换为列表"""
        if not self.ALLOW_HEADERS:
            return ["Content-Type"]
        return [header.strip() for header in self.ALLOW_HEADERS.split(",") if header.strip()]


# =============================================================================
# 全局配置（单例）
# =============================================================================


class Settings:
    """
    全局配置单例

    每个 Agent 拥有独立的完整配置，配置清晰明确
    """

    def __init__(self):
        # Agent 配置（每个 Agent 独立）
        self.planner = PlannerAgentConfig()
        self.visual = VisualAgentConfig()
        self.layout = LayoutAgentConfig()
        self.critic = CriticAgentConfig()

        # 应用配置
        self.canvas = CanvasConfig()
        self.cors = CORSConfig()
        self.kg = KGConfig()
        self.rag = RAGConfig()

    # 静态配置
    ERROR_FALLBACKS: Dict[str, Any] = {
        "planner": {
            "title": "Error",
            "subtitle": "",
            "main_color": "#000000",
            "background_color": "#FFFFFF",
            "style_keywords": [],
            "intent": "other",
        },
        "visual": {"background_layer": {"type": "image", "src": "", "source_type": "fallback"}},
        "layout": {
            "canvas": {"width": 1080, "height": 1920, "backgroundColor": "#FFFFFF"},
            "layers": [],
        },
        "critic": {"status": "PASS", "feedback": "System Error", "issues": []},
    }

    WORKFLOW_CONFIG: Dict[str, Any] = {
        "nodes": [
            {"name": "planner", "description": "Planning Agent", "agent": "planner"},
            {"name": "visual", "description": "Visual Agent", "agent": "visual"},
            {"name": "layout", "description": "Layout Agent", "agent": "layout"},
            {"name": "critic", "description": "Critic Agent", "agent": "critic"},
        ],
        "edges": [
            {"from": "planner", "to": "visual"},
            {"from": "visual", "to": "layout"},
            {"from": "layout", "to": "critic"},
            {"from": "critic", "to": "layout", "condition": "reject"},
            {"from": "critic", "to": "END", "condition": "pass"},
        ],
        "entry_point": "planner",
    }


# 导出全局配置单例
settings = Settings()
