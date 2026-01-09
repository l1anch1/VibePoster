"""
RAG 数据加载器

负责从 JSON 文件加载品牌知识数据。

Author: VibePoster Team
Date: 2025-01
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path

from .types import Document
from ...core.logger import get_logger

logger = get_logger(__name__)

# 默认数据文件路径
DEFAULT_DATA_DIR = Path(__file__).parent / "data"
DEFAULT_BRAND_FILE = DEFAULT_DATA_DIR / "default_brand_knowledge.json"


class BrandDataLoader:
    """品牌数据加载器"""
    
    def __init__(self, data_file: Optional[str] = None):
        """
        初始化加载器
        
        Args:
            data_file: 数据文件路径（可选）
        """
        self.data_file = Path(data_file) if data_file else DEFAULT_BRAND_FILE
    
    def load(self) -> List[Document]:
        """
        加载品牌数据
        
        Returns:
            文档列表
        """
        if not self.data_file.exists():
            logger.warning(f"品牌数据文件不存在: {self.data_file}")
            return []
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            documents = []
            brands = data.get("brands", [])
            
            for i, item in enumerate(brands):
                doc = Document(
                    id=item.get("id", f"default_{i}"),
                    text=item["text"],
                    metadata=item.get("metadata", {})
                )
                documents.append(doc)
            
            logger.info(f"已加载 {len(documents)} 条品牌知识: {self.data_file}")
            return documents
        
        except json.JSONDecodeError as e:
            logger.error(f"品牌数据 JSON 解析失败: {e}")
            return []
        except Exception as e:
            logger.error(f"加载品牌数据失败: {e}")
            return []
    
    def load_from_dict(self, data: Dict[str, Any]) -> List[Document]:
        """
        从字典加载品牌数据
        
        Args:
            data: 数据字典
        
        Returns:
            文档列表
        """
        documents = []
        brands = data.get("brands", [])
        
        for i, item in enumerate(brands):
            doc = Document(
                id=item.get("id", f"dict_{i}"),
                text=item["text"],
                metadata=item.get("metadata", {})
            )
            documents.append(doc)
        
        return documents

