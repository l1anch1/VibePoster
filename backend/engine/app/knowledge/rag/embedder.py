"""
RAG 嵌入计算器

负责文本向量化。

Author: VibePoster Team
Date: 2025-01
"""

from typing import Optional, List
from abc import ABC, abstractmethod
import numpy as np

from ...core.logger import get_logger

logger = get_logger(__name__)

# 尝试导入 sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers 未安装")


class BaseEmbedder(ABC):
    """嵌入器基类"""
    
    @abstractmethod
    def encode(self, text: str) -> Optional[np.ndarray]:
        """将文本编码为向量"""
        pass
    
    @abstractmethod
    def encode_batch(self, texts: List[str]) -> List[Optional[np.ndarray]]:
        """批量编码"""
        pass
    
    @property
    @abstractmethod
    def is_available(self) -> bool:
        """是否可用"""
        pass


class SentenceTransformerEmbedder(BaseEmbedder):
    """
    Sentence Transformers 嵌入器
    
    使用预训练模型进行文本向量化。
    """
    
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """
        初始化嵌入器
        
        Args:
            model_name: 模型名称
        """
        self.model_name = model_name
        self._model = None
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                logger.info(f"加载嵌入模型: {model_name}")
                self._model = SentenceTransformer(model_name)
                logger.info("✅ 嵌入模型加载成功")
            except Exception as e:
                logger.error(f"加载嵌入模型失败: {e}")
    
    @property
    def is_available(self) -> bool:
        """是否可用"""
        return self._model is not None
    
    def encode(self, text: str) -> Optional[np.ndarray]:
        """将文本编码为向量"""
        if not self.is_available:
            return None
        
        try:
            return self._model.encode(text, convert_to_numpy=True)
        except Exception as e:
            logger.error(f"文本编码失败: {e}")
            return None
    
    def encode_batch(self, texts: List[str]) -> List[Optional[np.ndarray]]:
        """批量编码"""
        if not self.is_available:
            return [None] * len(texts)
        
        try:
            embeddings = self._model.encode(texts, convert_to_numpy=True)
            return list(embeddings)
        except Exception as e:
            logger.error(f"批量编码失败: {e}")
            return [None] * len(texts)


class NullEmbedder(BaseEmbedder):
    """
    空嵌入器（降级方案）
    
    当没有可用的嵌入模型时使用。
    """
    
    @property
    def is_available(self) -> bool:
        return False
    
    def encode(self, text: str) -> Optional[np.ndarray]:
        return None
    
    def encode_batch(self, texts: List[str]) -> List[Optional[np.ndarray]]:
        return [None] * len(texts)


def create_embedder(model_name: Optional[str] = None) -> BaseEmbedder:
    """
    创建嵌入器工厂方法
    
    Args:
        model_name: 模型名称（可选）
    
    Returns:
        嵌入器实例
    """
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        logger.warning("sentence-transformers 不可用，使用空嵌入器")
        return NullEmbedder()
    
    # 从配置读取默认模型
    if model_name is None:
        try:
            from ...core.config import settings
            model_name = settings.rag.EMBEDDING_MODEL
        except Exception:
            model_name = "paraphrase-multilingual-MiniLM-L12-v2"
    
    embedder = SentenceTransformerEmbedder(model_name)
    
    if not embedder.is_available:
        logger.warning("嵌入器初始化失败，使用空嵌入器")
        return NullEmbedder()
    
    return embedder

