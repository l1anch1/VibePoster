"""
LLM Client 工厂 - 统一管理 DeepSeek/Gemini 的 Client
"""
from typing import Dict, Any
from openai import OpenAI
from google import genai
from google.genai import types

from .config import DEEPSEEK_CONFIG, GEMINI_CONFIG


class LLMClientFactory:
    """LLM Client 工厂类"""
    
    _clients: Dict[str, Any] = {}
    
    @classmethod
    def get_deepseek_client(cls) -> OpenAI:
        """获取 DeepSeek Client"""
        cache_key = "deepseek"
        if cache_key not in cls._clients:
            cls._clients[cache_key] = OpenAI(
                api_key=DEEPSEEK_CONFIG["api_key"],
                base_url=DEEPSEEK_CONFIG["base_url"],
            )
        return cls._clients[cache_key]
    
    @classmethod
    def get_gemini_client(cls) -> genai.Client:
        """获取 Gemini Client"""
        cache_key = "gemini"
        if cache_key not in cls._clients:
            cls._clients[cache_key] = genai.Client(
                api_key=GEMINI_CONFIG["api_key"],
                vertexai=GEMINI_CONFIG.get("vertexai", True),
                http_options={
                    "base_url": GEMINI_CONFIG.get("base_url"),
                },
            )
        return cls._clients[cache_key]
    
    @classmethod
    def get_client(cls, provider: str):
        """根据 provider 获取对应的 Client"""
        if provider == "deepseek":
            return cls.get_deepseek_client()
        elif provider == "gemini":
            return cls.get_gemini_client()
        else:
            raise ValueError(f"Unknown provider: {provider}")

