"""
LLM Client 工厂 - 统一管理多供应商的 Client
支持根据 PROVIDER 动态创建客户端
"""
from typing import Dict, Any
from openai import OpenAI
import google.generativeai as genai


class LLMClientFactory:
    """LLM Client 工厂类 - 支持多供应商"""
    
    _clients: Dict[str, Any] = {}
    
    @classmethod
    def get_client(cls, provider: str, api_key: str, base_url: str) -> Any:
        """
        根据 provider 获取对应的 Client
        
        Args:
            provider: 供应商名称 (deepseek, openai, gemini, moonshot 等)
            api_key: API Key
            base_url: Base URL
            
        Returns:
            对应的 Client 实例
        """
        provider_lower = provider.lower()
        cache_key = f"{provider_lower}_{api_key[:10] if api_key else 'default'}"
        
        if cache_key not in cls._clients:
            if provider_lower in ["deepseek", "openai", "moonshot"]:
                # 使用 OpenAI 兼容接口
                cls._clients[cache_key] = OpenAI(
                    api_key=api_key,
                    base_url=base_url,
                )
            elif provider_lower == "gemini":
                # 使用 Gemini 客户端
                # 如果 base_url 包含代理地址，不使用 vertexai
                use_vertexai = "openai-proxy.org" not in base_url if base_url else False
                cls._clients[cache_key] = genai.Client(
                    api_key=api_key,
                    vertexai=use_vertexai,
                    http_options={
                        "base_url": base_url,
                    } if base_url else None,
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")
        
        return cls._clients[cache_key]

