"""
Brand Knowledge Base - 组合入口

整合嵌入器、检索器和加载器，提供统一接口。
实现 IKnowledgeBase 接口。

Author: VibePoster Team
Date: 2025-01
"""

from typing import List, Dict, Any, Optional

from .types import Document, SearchResult, KnowledgeBaseStats, BackendType
from .embedder import create_embedder, BaseEmbedder, SENTENCE_TRANSFORMERS_AVAILABLE
from .retriever import (
    BaseRetriever, 
    VectorRetriever, 
    KeywordRetriever, 
    ChromaDBRetriever,
    CHROMADB_AVAILABLE
)
from .loader import BrandDataLoader
from ...core.interfaces import IKnowledgeBase
from ...core.logger import get_logger

logger = get_logger(__name__)


class BrandKnowledgeBase(IKnowledgeBase):
    """
    品牌知识库
    
    组合 Embedder、Retriever 和 Loader，
    提供符合 IKnowledgeBase 接口的统一入口。
    
    使用示例:
        kb = BrandKnowledgeBase()
        results = kb.search("华为的配色", top_k=2)
        for r in results:
            print(r["text"])
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
            use_chromadb: 是否使用 ChromaDB
            persist_directory: ChromaDB 持久化目录
            load_default_data: 是否加载默认数据
            embedding_model: 嵌入模型名称
            default_data_file: 默认数据文件路径
        """
        logger.info("📚 初始化品牌知识库...")
        
        # 从配置读取默认值
        config = self._load_config()
        
        self._use_chromadb = use_chromadb if use_chromadb is not None else config.get("use_chromadb", False)
        self._persist_directory = persist_directory or config.get("persist_directory", "./chroma_db")
        self._load_default = load_default_data if load_default_data is not None else config.get("load_default", True)
        self._embedding_model = embedding_model or config.get("embedding_model")
        
        # 初始化组件
        self._embedder = create_embedder(self._embedding_model)
        self._retriever = self._create_retriever()
        self._loader = BrandDataLoader(default_data_file)
        
        # 加载默认数据
        if self._load_default:
            self._load_default_data()
        
        logger.info(f"✅ 知识库初始化完成: backend={self._retriever.backend_type.value}")
    
    def _load_config(self) -> Dict[str, Any]:
        """从配置加载默认值"""
        try:
            from ...core.config import settings
            return {
                "use_chromadb": settings.rag.USE_CHROMADB,
                "persist_directory": settings.rag.PERSIST_DIRECTORY,
                "load_default": settings.rag.LOAD_DEFAULT_DATA,
                "embedding_model": settings.rag.EMBEDDING_MODEL
            }
        except Exception:
            return {}
    
    def _create_retriever(self) -> BaseRetriever:
        """创建检索器"""
        # 优先使用 ChromaDB
        if self._use_chromadb and CHROMADB_AVAILABLE:
            logger.info("使用 ChromaDB 检索后端")
            return ChromaDBRetriever(self._persist_directory)
        
        # 其次使用向量检索
        if self._embedder.is_available:
            logger.info("使用 sentence-transformers 向量检索后端")
            return VectorRetriever(self._embedder)
        
        # 降级到关键词检索
        logger.warning("使用关键词检索后端（降级方案）")
        return KeywordRetriever()
    
    def _load_default_data(self):
        """加载默认品牌数据"""
        documents = self._loader.load()
        for doc in documents:
            self._add_document_internal(doc)
    
    def _add_document_internal(self, document: Document):
        """内部添加文档方法"""
        # 如果使用向量检索且文档没有嵌入，计算嵌入
        if (
            isinstance(self._retriever, VectorRetriever) and 
            document.embedding is None and 
            self._embedder.is_available
        ):
            document.embedding = self._embedder.encode(document.text)
        
        self._retriever.add(document)
    
    # ========================================================================
    # IKnowledgeBase 接口实现
    # ========================================================================
    
    def add_document(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> str:
        """
        添加文档到知识库（接口方法）
        
        Args:
            text: 文档文本
            metadata: 元数据
            doc_id: 文档 ID
        
        Returns:
            文档 ID
        """
        if doc_id is None:
            doc_id = f"doc_{self._retriever.document_count}"
        
        document = Document(
            id=doc_id,
            text=text,
            metadata=metadata or {}
        )
        
        self._add_document_internal(document)
        logger.debug(f"添加文档: {doc_id}")
        
        return doc_id
    
    def search(
        self,
        query: str,
        top_k: int = 2,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        检索知识库（接口方法）
        
        Args:
            query: 查询文本
            top_k: 返回数量
            filter_metadata: 元数据过滤
        
        Returns:
            检索结果列表
        """
        results = self._retriever.search(query, top_k, filter_metadata)
        return [r.to_dict() for r in results]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取知识库统计信息（接口方法）
        
        Returns:
            统计信息字典
        """
        stats = KnowledgeBaseStats(
            total_documents=self._retriever.document_count,
            backend=self._retriever.backend_type.value,
            model_available=SENTENCE_TRANSFORMERS_AVAILABLE,
            chromadb_available=CHROMADB_AVAILABLE,
            embedding_model=self._embedding_model if self._embedder.is_available else None,
            default_data_file=str(self._loader.data_file)
        )
        return stats.to_dict()
    
    # ========================================================================
    # 扩展方法
    # ========================================================================
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """获取所有文档（仅向量检索器支持）"""
        if isinstance(self._retriever, (VectorRetriever, KeywordRetriever)):
            return [doc.to_dict() for doc in self._retriever.documents]
        return []
    
    def clear(self):
        """清空知识库"""
        if isinstance(self._retriever, (VectorRetriever, KeywordRetriever)):
            self._retriever.documents.clear()
        logger.info("知识库已清空")
    
    # ========================================================================
    # 属性访问
    # ========================================================================
    
    @property
    def embedder(self) -> BaseEmbedder:
        """嵌入器"""
        return self._embedder
    
    @property
    def retriever(self) -> BaseRetriever:
        """检索器"""
        return self._retriever
    
    @property
    def loader(self) -> BrandDataLoader:
        """数据加载器"""
        return self._loader

