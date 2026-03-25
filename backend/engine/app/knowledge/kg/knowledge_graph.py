"""
Design Knowledge Graph v2 - 组合入口

支持语义化推理链：Industry/Vibe → Emotion → Visual Elements

使用示例:
    kg = DesignKnowledgeGraph()
    result = kg.infer_rules(["Tech", "Minimalist"])
    
    print(result["emotions"])           # ["Trust", "Innovation", "Premium"]
    print(result["color_strategies"])   # ["Monochromatic", "Analogous"]
    print(result["color_palettes"])     # {"primary": [...], "accent": [...]}
    print(result["layout_patterns"])    # ["Grid", "Centered", "Minimal"]
    print(result["design_principles"])  # ["Clean interfaces", ...]
    print(result["avoid"])              # ["Warm earth tones", ...]

Author: VibePoster Team
Date: 2025-01
"""

from typing import List, Dict, Any, Optional

from .types import InferenceResult, GraphStats
from .loader import RulesLoader
from .graph import DesignGraph
from .inference import InferenceEngine
from ...core.interfaces import IKnowledgeGraph
from ...core.logger import get_logger

logger = get_logger(__name__)


class DesignKnowledgeGraph(IKnowledgeGraph):
    """
    设计知识图谱 v2
    
    支持多层语义推理：
    1. 从 Industry/Vibe 关键词找到对应的 Emotions
    2. 合并所有 Emotions 的视觉设计规则
    3. 返回结构化的推理结果
    """
    
    def __init__(self, rules_file: Optional[str] = None):
        """
        初始化知识图谱
        
        Args:
            rules_file: 规则文件路径（可选）
        """
        logger.info("🔮 初始化设计知识图谱 v2...")
        
        self._loader = RulesLoader(rules_file)
        self._graph = DesignGraph(self._loader)
        self._engine = InferenceEngine(self._graph)
        
        stats = self._graph.get_stats()
        logger.info(
            f"✅ KG v{stats.version} 初始化完成: "
            f"{stats.node_count} 节点, {stats.edge_count} 边 | "
            f"Emotions: {len(stats.emotions)}, "
            f"Industries: {len(stats.industries)}, "
            f"Vibes: {len(stats.vibes)}"
        )
    
    # ========================================================================
    # IKnowledgeGraph 接口实现（兼容旧版）
    # ========================================================================
    
    def infer_rules(self, keywords: List[str]) -> Dict[str, Any]:
        """
        基于关键词推理设计规则（接口方法）
        
        返回完整的 v2 格式结果。
        
        Args:
            keywords: 关键词列表
        
        Returns:
            完整推理结果
        """
        result = self._engine.infer(keywords)
        return result.to_dict()
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """获取图谱统计信息"""
        return self._graph.get_stats().to_dict()
    
    # ========================================================================
    # 扩展方法
    # ========================================================================
    
    def get_emotions_for_keyword(self, keyword: str) -> List[str]:
        """获取关键词对应的情绪列表"""
        return self._graph.get_embodied_emotions(keyword)
    
    def get_emotion_visual_rules(self, emotion: str) -> Optional[Dict[str, Any]]:
        """获取单个情绪的视觉规则"""
        return self._graph.get_emotion_definition(emotion)
    
    def visualize_inference_chain(self, keyword: str) -> Dict[str, Any]:
        """可视化推理链"""
        return self._graph.visualize_inference_chain(keyword)
    
    def get_supported_keywords(self) -> Dict[str, List[str]]:
        """获取支持的关键词"""
        return self._loader.get_supported_keywords()
    
    def rebuild(self):
        """重建图谱"""
        logger.info("🔄 重建知识图谱...")
        self._graph.rebuild()
        stats = self._graph.get_stats()
        logger.info(f"✅ 重建完成: {stats.node_count} 节点, {stats.edge_count} 边")
    
    # ========================================================================
    # 属性
    # ========================================================================
    
    @property
    def loader(self) -> RulesLoader:
        return self._loader
    
    @property
    def graph(self) -> DesignGraph:
        return self._graph
    
    @property
    def engine(self) -> InferenceEngine:
        return self._engine
    
    @property
    def version(self) -> str:
        return self._loader.get_version()
