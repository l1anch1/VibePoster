"""
RAG Engine - 企业品牌知识检索模块

基于 RAG (Retrieval-Augmented Generation) 的品牌知识库检索系统。
用于检索企业品牌手册，辅助 AI 生成符合品牌规范的海报设计。

默认品牌数据从 data/default_brand_knowledge.json 加载。

技术栈：
    - 轻量级版本: sentence-transformers + cosine similarity
    - 完整版本: langchain + chromadb (可选升级)

Author: VibePoster Team
Date: 2025-01
"""

import json
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ...core.interfaces import IKnowledgeBase
from ...core.logger import get_logger

logger = get_logger(__name__)

# 数据文件路径
DATA_DIR = Path(__file__).parent.parent / "data"
DEFAULT_BRAND_FILE = DATA_DIR / "default_brand_knowledge.json"

# 尝试导入 sentence-transformers（轻量级方案）
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers 未安装，将使用简单文本匹配")

# 尝试导入 chromadb（完整方案）
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


@dataclass
class Document:
    """文档数据结构"""
    id: str
    text: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None


class BrandKnowledgeBase(IKnowledgeBase):
    """
    品牌知识库类
    
    实现 IKnowledgeBase 接口。
    
    支持两种模式：
    1. 轻量级模式：使用 sentence-transformers 进行向量检索
    2. 简单模式：使用关键词匹配（当依赖库不可用时）
    """
    
    def __init__(
        self,
        use_chromadb: Optional[bool] = None,
        persist_directory: Optional[str] = None,
        load_default_data: Optional[bool] = None,
        embedding_model: Optional[str] = None,
        default_data_file: Optional[str] = None
    ):
        """
        初始化品牌知识库
        
        Args:
            use_chromadb: 是否使用 chromadb（默认从配置读取）
            persist_directory: ChromaDB 持久化目录（默认从配置读取）
            load_default_data: 是否加载默认数据（默认从配置读取）
            embedding_model: 嵌入模型名称（默认从配置读取）
            default_data_file: 默认品牌数据文件路径（可选）
        """
        # 从配置读取默认值
        from ...core.config import settings
        
        self.use_chromadb = use_chromadb if use_chromadb is not None else settings.rag.USE_CHROMADB
        self.persist_directory = persist_directory or settings.rag.PERSIST_DIRECTORY
        self.load_default = load_default_data if load_default_data is not None else settings.rag.LOAD_DEFAULT_DATA
        self.embedding_model_name = embedding_model or settings.rag.EMBEDDING_MODEL
        self.default_data_file = Path(default_data_file) if default_data_file else DEFAULT_BRAND_FILE
        
        self.documents: List[Document] = []
        self.use_chromadb = self.use_chromadb and CHROMADB_AVAILABLE
        self.model = None
        
        # 初始化向量模型
        if SENTENCE_TRANSFORMERS_AVAILABLE and not self.use_chromadb:
            logger.info("使用 sentence-transformers 进行向量检索")
            self.model = SentenceTransformer(self.embedding_model_name)
        elif self.use_chromadb:
            logger.info("使用 chromadb 进行向量检索")
            os.makedirs(self.persist_directory, exist_ok=True)
            self.client = chromadb.Client(ChromaSettings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=self.persist_directory
            ))
            self.collection = self.client.get_or_create_collection(
                name="brand_knowledge",
                metadata={"hnsw:space": "cosine"}
            )
        else:
            logger.warning("使用简单关键词匹配（性能较低）")
        
        # 加载默认品牌数据
        if self.load_default:
            self._load_default_data()
    
    def _load_default_data(self):
        """从 JSON 文件加载默认的品牌手册数据"""
        if not self.default_data_file.exists():
            logger.warning(f"默认品牌数据文件不存在: {self.default_data_file}")
            return
        
        try:
            with open(self.default_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            brands = data.get("brands", [])
            
            for doc in brands:
                self.add_document(
                    text=doc["text"],
                    metadata=doc.get("metadata", {}),
                    doc_id=doc.get("id", f"default_{len(self.documents)}")
                )
            
            logger.info(f"已加载 {len(brands)} 条默认品牌知识: {self.default_data_file}")
        
        except Exception as e:
            logger.error(f"加载默认品牌数据失败: {e}")
    
    def add_document(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> str:
        """
        添加文档到知识库
        
        Args:
            text: 文档文本内容
            metadata: 文档元数据
            doc_id: 文档 ID（可选）
        
        Returns:
            文档 ID
        """
        if doc_id is None:
            doc_id = f"doc_{len(self.documents)}"
        
        if metadata is None:
            metadata = {}
        
        # 计算向量嵌入
        embedding = None
        if self.model is not None:
            embedding = self.model.encode(text, convert_to_numpy=True)
        
        # 创建文档对象
        doc = Document(
            id=doc_id,
            text=text,
            metadata=metadata,
            embedding=embedding
        )
        
        # 存储文档
        if self.use_chromadb:
            self.collection.add(
                ids=[doc_id],
                documents=[text],
                metadatas=[metadata],
                embeddings=[embedding.tolist()] if embedding is not None else None
            )
        else:
            self.documents.append(doc)
        
        return doc_id
    
    def search(
        self,
        query: str,
        top_k: int = 2,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        检索知识库
        
        Args:
            query: 查询文本
            top_k: 返回前 k 个结果
            filter_metadata: 元数据过滤条件（可选）
        
        Returns:
            检索结果列表
        """
        if self.use_chromadb:
            return self._search_chromadb(query, top_k, filter_metadata)
        elif self.model is not None:
            return self._search_vector(query, top_k, filter_metadata)
        else:
            return self._search_keyword(query, top_k, filter_metadata)
    
    def _search_vector(
        self,
        query: str,
        top_k: int,
        filter_metadata: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """向量检索（sentence-transformers）"""
        query_embedding = self.model.encode(query, convert_to_numpy=True)
        
        scores = []
        for doc in self.documents:
            if filter_metadata and not self._match_metadata(doc.metadata, filter_metadata):
                continue
            
            if doc.embedding is not None:
                similarity = np.dot(query_embedding, doc.embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(doc.embedding)
                )
                scores.append((doc, similarity))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for doc, score in scores[:top_k]:
            results.append({
                "text": doc.text,
                "metadata": doc.metadata,
                "score": float(score)
            })
        
        return results
    
    def _search_keyword(
        self,
        query: str,
        top_k: int,
        filter_metadata: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """关键词匹配检索（降级方案）"""
        scores = []
        query_lower = query.lower()
        
        for doc in self.documents:
            if filter_metadata and not self._match_metadata(doc.metadata, filter_metadata):
                continue
            
            text_lower = doc.text.lower()
            match_score = 0
            for word in query_lower.split():
                if len(word) > 1:
                    match_score += text_lower.count(word)
            
            if match_score > 0:
                scores.append((doc, match_score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for doc, score in scores[:top_k]:
            results.append({
                "text": doc.text,
                "metadata": doc.metadata,
                "score": float(score)
            })
        
        return results
    
    def _search_chromadb(
        self,
        query: str,
        top_k: int,
        filter_metadata: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """ChromaDB 检索"""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=filter_metadata
        )
        
        formatted_results = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    "text": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "score": 1.0 - results['distances'][0][i] if results['distances'] else 0.0
                })
        
        return formatted_results
    
    def _match_metadata(
        self,
        doc_metadata: Dict[str, Any],
        filter_metadata: Dict[str, Any]
    ) -> bool:
        """检查文档元数据是否匹配过滤条件"""
        for key, value in filter_metadata.items():
            if key not in doc_metadata or doc_metadata[key] != value:
                return False
        return True
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """获取所有文档（用于调试）"""
        return [
            {
                "id": doc.id,
                "text": doc.text,
                "metadata": doc.metadata
            }
            for doc in self.documents
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        return {
            "total_documents": len(self.documents),
            "backend": "chromadb" if self.use_chromadb else (
                "sentence-transformers" if self.model else "keyword"
            ),
            "model_available": SENTENCE_TRANSFORMERS_AVAILABLE,
            "chromadb_available": CHROMADB_AVAILABLE,
            "embedding_model": self.embedding_model_name if self.model else None,
            "default_data_file": str(self.default_data_file)
        }


# ============================================================================
# 单元测试
# ============================================================================

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 80)
    print("RAG Engine - 品牌知识检索测试")
    print("=" * 80)
    
    # 初始化知识库
    rag = BrandKnowledgeBase()
    
    # 统计信息
    print(f"\n📊 知识库统计:")
    stats = rag.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 测试检索
    print("\n" + "=" * 80)
    print("[测试] 查询: '华为的配色'")
    print("=" * 80)
    results = rag.search("华为的配色", top_k=2)
    for i, result in enumerate(results, 1):
        print(f"\n结果 {i} (相似度: {result['score']:.4f}):")
        print(f"  文本: {result['text'][:80]}...")
    
    print("\n✅ 测试完成！")

