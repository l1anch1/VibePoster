"""
KG 图结构管理 v2

支持语义化推理链：Industry/Vibe → Emotion → Visual Elements

Author: VibePoster Team
Date: 2025-01
"""

from typing import Dict, Any, List, Optional, Set
import networkx as nx

from .types import EdgeType, GraphStats, NodeType
from .loader import RulesLoader
from ...core.logger import get_logger

logger = get_logger(__name__)


class DesignGraph:
    """
    设计知识图结构 v2
    
    图结构：
        - Industry/Vibe 节点通过 EMBODIES 边连接到 Emotion 节点
        - Emotion 节点包含完整的视觉设计规则
    """
    
    def __init__(self, loader: Optional[RulesLoader] = None):
        """
        初始化图结构
        
        Args:
            loader: 规则加载器
        """
        self.graph = nx.DiGraph()
        self.loader = loader or RulesLoader()
        self._build()
    
    def _build(self):
        """构建图结构"""
        # 添加情绪节点（核心节点）
        emotions = self.loader.get_emotions()
        for emotion_name, emotion_def in emotions.items():
            self.graph.add_node(
                emotion_name,
                node_type=NodeType.EMOTION.value,
                data=emotion_def.model_dump()
            )
        
        # 添加行业节点及其到情绪的边
        industries = self.loader.get_industries()
        for industry_name, industry_def in industries.items():
            self.graph.add_node(
                industry_name,
                node_type=NodeType.INDUSTRY.value,
                data=industry_def.model_dump()
            )
            
            # 建立 Industry → Emotion 的 embodies 边
            for emotion in industry_def.embodies:
                if emotion in emotions:
                    self.graph.add_edge(
                        industry_name,
                        emotion,
                        relation=EdgeType.EMBODIES.value
                    )
        
        # 添加风格节点及其到情绪的边
        vibes = self.loader.get_vibes()
        for vibe_name, vibe_def in vibes.items():
            self.graph.add_node(
                vibe_name,
                node_type=NodeType.VIBE.value,
                data=vibe_def.model_dump()
            )
            
            # 建立 Vibe → Emotion 的 embodies 边
            for emotion in vibe_def.embodies:
                if emotion in emotions:
                    self.graph.add_edge(
                        vibe_name,
                        emotion,
                        relation=EdgeType.EMBODIES.value
                    )
        
        logger.info(
            f"KG v2 构建完成: {self.node_count} 节点, {self.edge_count} 边 "
            f"(Emotions: {len(emotions)}, Industries: {len(industries)}, Vibes: {len(vibes)})"
        )
    
    @property
    def node_count(self) -> int:
        return self.graph.number_of_nodes()
    
    @property
    def edge_count(self) -> int:
        return self.graph.number_of_edges()
    
    def has_node(self, keyword: str) -> bool:
        return keyword in self.graph
    
    def get_node_type(self, keyword: str) -> Optional[str]:
        """获取节点类型"""
        if not self.has_node(keyword):
            return None
        return self.graph.nodes[keyword].get("node_type")
    
    def get_node_data(self, keyword: str) -> Optional[Dict[str, Any]]:
        """获取节点数据"""
        if not self.has_node(keyword):
            return None
        return self.graph.nodes[keyword].get("data")
    
    def get_embodied_emotions(self, keyword: str) -> List[str]:
        """
        获取节点体现的情绪列表
        
        对于 Industry/Vibe 节点，返回其 embodies 的 Emotion 列表
        对于 Emotion 节点，返回自身
        """
        if not self.has_node(keyword):
            return []
        
        node_type = self.get_node_type(keyword)
        
        if node_type == NodeType.EMOTION.value:
            return [keyword]
        
        # 获取所有 embodies 边指向的情绪节点
        emotions = []
        for _, target, edge_data in self.graph.out_edges(keyword, data=True):
            if edge_data.get("relation") == EdgeType.EMBODIES.value:
                emotions.append(target)
        
        return emotions
    
    def get_emotion_definition(self, emotion: str) -> Optional[Dict[str, Any]]:
        """获取情绪节点的完整定义"""
        if not self.has_node(emotion):
            return None
        
        if self.get_node_type(emotion) != NodeType.EMOTION.value:
            return None
        
        return self.get_node_data(emotion)
    
    def get_stats(self) -> GraphStats:
        """获取图谱统计信息"""
        keywords = self.loader.get_supported_keywords()
        return GraphStats(
            node_count=self.node_count,
            edge_count=self.edge_count,
            rules_file=str(self.loader.rules_file),
            version=self.loader.get_version(),
            industries=keywords.get("industries", []),
            vibes=keywords.get("vibes", []),
            emotions=keywords.get("emotions", [])
        )
    
    def visualize_inference_chain(self, keyword: str) -> Dict[str, Any]:
        """可视化推理链"""
        if not self.has_node(keyword):
            return {"error": f"关键词 '{keyword}' 不在图谱中"}
        
        node_type = self.get_node_type(keyword)
        emotions = self.get_embodied_emotions(keyword)
        
        chain = {
            "keyword": keyword,
            "node_type": node_type,
            "emotions": emotions,
            "visual_elements": {}
        }
        
        # 收集每个情绪的视觉元素
        for emotion in emotions:
            emotion_def = self.get_emotion_definition(emotion)
            if emotion_def:
                chain["visual_elements"][emotion] = {
                    "color_strategies": emotion_def.get("color_strategies", []),
                    "typography": emotion_def.get("typography", {}),
                    "layout": emotion_def.get("layout", {})
                }
        
        return chain
    
    def rebuild(self):
        """重建图结构"""
        self.graph.clear()
        self.loader.clear_cache()
        self._build()
