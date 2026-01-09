"""
RAG (Retrieval-Augmented Generation) 模块

提供品牌知识检索功能。

模块结构:
    - types.py: 类型定义
    - embedder.py: 嵌入计算
    - retriever.py: 检索策略
    - loader.py: 数据加载
    - knowledge_base.py: 组合入口
"""

from .knowledge_base import BrandKnowledgeBase
from .types import Document, SearchResult, KnowledgeBaseStats, BackendType
from .embedder import (
    BaseEmbedder,
    SentenceTransformerEmbedder,
    NullEmbedder,
    create_embedder,
    SENTENCE_TRANSFORMERS_AVAILABLE
)
from .retriever import (
    BaseRetriever,
    VectorRetriever,
    KeywordRetriever,
    ChromaDBRetriever,
    CHROMADB_AVAILABLE
)
from .loader import BrandDataLoader

__all__ = [
    # 主入口
    "BrandKnowledgeBase",
    
    # 类型
    "Document",
    "SearchResult",
    "KnowledgeBaseStats",
    "BackendType",
    
    # 嵌入器
    "BaseEmbedder",
    "SentenceTransformerEmbedder",
    "NullEmbedder",
    "create_embedder",
    "SENTENCE_TRANSFORMERS_AVAILABLE",
    
    # 检索器
    "BaseRetriever",
    "VectorRetriever",
    "KeywordRetriever",
    "ChromaDBRetriever",
    "CHROMADB_AVAILABLE",
    
    # 加载器
    "BrandDataLoader",
]
