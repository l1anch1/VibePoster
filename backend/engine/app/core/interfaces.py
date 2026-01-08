"""
接口抽象定义

定义核心模块的抽象接口，实现依赖倒置原则。
便于测试时 Mock，便于未来替换实现。

Author: VibePoster Team
Date: 2025-01
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class IKnowledgeGraph(ABC):
    """知识图谱接口"""
    
    @abstractmethod
    def infer_rules(self, keywords: List[str]) -> Dict[str, Any]:
        """
        根据关键词推理设计规则
        
        Args:
            keywords: 关键词列表（行业/氛围）
            
        Returns:
            推荐规则字典：
            {
                "recommended_colors": [...],
                "recommended_fonts": [...],
                "recommended_layouts": [...]
            }
        """
        pass
    
    @abstractmethod
    def get_graph_stats(self) -> Dict[str, Any]:
        """获取图谱统计信息"""
        pass


class IKnowledgeBase(ABC):
    """知识库接口（RAG）"""
    
    @abstractmethod
    def add_document(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> None:
        """添加文档到知识库"""
        pass
    
    @abstractmethod
    def search(
        self,
        query: str,
        top_k: int = 2,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """检索知识库"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        pass


class IRendererService(ABC):
    """渲染服务接口"""
    
    @abstractmethod
    def render_poster_from_workflow_state(
        self,
        workflow_state: Dict[str, Any]
    ) -> Any:
        """从工作流状态渲染海报"""
        pass


class IAssetSearcher(ABC):
    """素材搜索接口"""
    
    @abstractmethod
    def search(
        self,
        query: str,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """搜索素材"""
        pass

