"""
RAG 检索策略

支持多种检索后端。

Author: VibePoster Team
Date: 2025-01
"""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import numpy as np

from .types import Document, SearchResult, BackendType
from .embedder import BaseEmbedder
from ...core.logger import get_logger

logger = get_logger(__name__)

# 尝试导入 chromadb
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


class BaseRetriever(ABC):
    """检索器基类"""
    
    @abstractmethod
    def add(self, document: Document):
        """添加文档"""
        pass
    
    @abstractmethod
    def search(
        self,
        query: str,
        top_k: int = 2,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """检索文档"""
        pass
    
    @property
    @abstractmethod
    def backend_type(self) -> BackendType:
        """后端类型"""
        pass
    
    @property
    @abstractmethod
    def document_count(self) -> int:
        """文档数量"""
        pass


class VectorRetriever(BaseRetriever):
    """
    向量检索器
    
    使用 sentence-transformers 进行向量相似度检索。
    """
    
    def __init__(self, embedder: BaseEmbedder):
        """
        初始化检索器
        
        Args:
            embedder: 嵌入器
        """
        self.embedder = embedder
        self.documents: List[Document] = []
    
    @property
    def backend_type(self) -> BackendType:
        return BackendType.VECTOR
    
    @property
    def document_count(self) -> int:
        return len(self.documents)
    
    def add(self, document: Document):
        """添加文档（自动计算嵌入）"""
        if document.embedding is None and self.embedder.is_available:
            document.embedding = self.embedder.encode(document.text)
        self.documents.append(document)
    
    def search(
        self,
        query: str,
        top_k: int = 2,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """向量检索"""
        query_embedding = self.embedder.encode(query)
        
        if query_embedding is None:
            logger.warning("查询向量化失败，回退到关键词检索")
            return self._keyword_search(query, top_k, filter_metadata)
        
        scores = []
        for doc in self.documents:
            # 元数据过滤
            if filter_metadata and not self._match_metadata(doc.metadata, filter_metadata):
                continue
            
            if doc.embedding is not None:
                similarity = self._cosine_similarity(query_embedding, doc.embedding)
                scores.append((doc, similarity))
        
        # 排序
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # 构建结果
        results = []
        for doc, score in scores[:top_k]:
            results.append(SearchResult(
                text=doc.text,
                metadata=doc.metadata,
                score=float(score),
                document_id=doc.id
            ))
        
        return results
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """计算余弦相似度"""
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    
    def _keyword_search(
        self,
        query: str,
        top_k: int,
        filter_metadata: Optional[Dict[str, Any]]
    ) -> List[SearchResult]:
        """关键词检索（降级方案）"""
        scores = []
        query_lower = query.lower()
        
        for doc in self.documents:
            if filter_metadata and not self._match_metadata(doc.metadata, filter_metadata):
                continue
            
            text_lower = doc.text.lower()
            match_score = sum(
                text_lower.count(word)
                for word in query_lower.split()
                if len(word) > 1
            )
            
            if match_score > 0:
                scores.append((doc, match_score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for doc, score in scores[:top_k]:
            results.append(SearchResult(
                text=doc.text,
                metadata=doc.metadata,
                score=float(score),
                document_id=doc.id
            ))
        
        return results
    
    def _match_metadata(
        self,
        doc_metadata: Dict[str, Any],
        filter_metadata: Dict[str, Any]
    ) -> bool:
        """检查元数据是否匹配"""
        for key, value in filter_metadata.items():
            if key not in doc_metadata or doc_metadata[key] != value:
                return False
        return True


class KeywordRetriever(BaseRetriever):
    """
    关键词检索器
    
    简单的关键词匹配，作为降级方案。
    """
    
    def __init__(self):
        self.documents: List[Document] = []
    
    @property
    def backend_type(self) -> BackendType:
        return BackendType.KEYWORD
    
    @property
    def document_count(self) -> int:
        return len(self.documents)
    
    def add(self, document: Document):
        self.documents.append(document)
    
    def search(
        self,
        query: str,
        top_k: int = 2,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """关键词检索"""
        scores = []
        query_lower = query.lower()
        
        for doc in self.documents:
            if filter_metadata:
                match = all(
                    doc.metadata.get(k) == v
                    for k, v in filter_metadata.items()
                )
                if not match:
                    continue
            
            text_lower = doc.text.lower()
            match_score = sum(
                text_lower.count(word)
                for word in query_lower.split()
                if len(word) > 1
            )
            
            if match_score > 0:
                scores.append((doc, match_score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for doc, score in scores[:top_k]:
            results.append(SearchResult(
                text=doc.text,
                metadata=doc.metadata,
                score=float(score),
                document_id=doc.id
            ))
        
        return results


class ChromaDBRetriever(BaseRetriever):
    """
    ChromaDB 检索器
    
    使用 ChromaDB 进行向量检索（完整方案）。
    """
    
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "brand_knowledge"
    ):
        """
        初始化检索器
        
        Args:
            persist_directory: 持久化目录
            collection_name: 集合名称
        """
        if not CHROMADB_AVAILABLE:
            raise RuntimeError("chromadb 未安装")
        
        import os
        os.makedirs(persist_directory, exist_ok=True)
        
        self.client = chromadb.Client(ChromaSettings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory
        ))
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self._count = 0
    
    @property
    def backend_type(self) -> BackendType:
        return BackendType.CHROMADB
    
    @property
    def document_count(self) -> int:
        return self._count
    
    def add(self, document: Document):
        """添加文档"""
        self.collection.add(
            ids=[document.id],
            documents=[document.text],
            metadatas=[document.metadata],
            embeddings=[document.embedding.tolist()] if document.embedding is not None else None
        )
        self._count += 1
    
    def search(
        self,
        query: str,
        top_k: int = 2,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """ChromaDB 检索"""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=filter_metadata
        )
        
        search_results = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                search_results.append(SearchResult(
                    text=doc,
                    metadata=results['metadatas'][0][i] if results['metadatas'] else {},
                    score=1.0 - results['distances'][0][i] if results['distances'] else 0.0
                ))
        
        return search_results

