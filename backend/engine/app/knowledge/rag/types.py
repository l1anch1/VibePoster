"""
RAG 类型定义

Author: VibePoster Team
Date: 2025-01
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
import numpy as np


class BackendType(str, Enum):
    """检索后端类型"""
    VECTOR = "sentence-transformers"    # 向量检索
    CHROMADB = "chromadb"               # ChromaDB
    KEYWORD = "keyword"                 # 关键词匹配（降级方案）


class Document(BaseModel):
    """文档数据结构"""
    id: str = Field(..., description="文档 ID")
    text: str = Field(..., description="文档文本")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    embedding: Optional[Any] = Field(default=None, exclude=True, description="向量嵌入")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（不含 embedding）"""
        return {
            "id": self.id,
            "text": self.text,
            "metadata": self.metadata
        }
    
    model_config = {"arbitrary_types_allowed": True}


class SearchResult(BaseModel):
    """检索结果"""
    text: str = Field(..., description="文档文本")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    score: float = Field(..., description="相似度分数")
    document_id: Optional[str] = Field(default=None, description="文档 ID")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "text": self.text,
            "metadata": self.metadata,
            "score": self.score
        }


class KnowledgeBaseStats(BaseModel):
    """知识库统计信息"""
    total_documents: int = Field(..., description="文档总数")
    backend: str = Field(..., description="检索后端类型")
    model_available: bool = Field(..., description="嵌入模型是否可用")
    chromadb_available: bool = Field(..., description="ChromaDB 是否可用")
    embedding_model: Optional[str] = Field(default=None, description="嵌入模型名称")
    default_data_file: Optional[str] = Field(default=None, description="默认数据文件路径")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.model_dump()
