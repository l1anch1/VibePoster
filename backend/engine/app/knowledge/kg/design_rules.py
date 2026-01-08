"""
Design Knowledge Graph - 设计规则推理引擎

基于 Knowledge Graph 的设计规则推理模块，用于解决 LLM 生成风格不稳定的问题。
通过图结构存储设计知识（如：科技行业 -> 适合蓝色 -> 适合无衬线字体）。

规则数据从 data/kg_rules.json 加载，便于维护和扩展。

Author: VibePoster Team
Date: 2025-01
"""

import json
import os
from typing import List, Dict, Any, Set
from pathlib import Path

import networkx as nx

from ...core.interfaces import IKnowledgeGraph
from ...core.logger import get_logger

logger = get_logger(__name__)

# 数据文件路径（默认值，可通过配置覆盖）
DATA_DIR = Path(__file__).parent.parent / "data"
DEFAULT_KG_RULES_FILE = DATA_DIR / "kg_rules.json"


class DesignKnowledgeGraph(IKnowledgeGraph):
    """
    设计知识图谱类
    
    使用有向图存储设计领域的知识规则，支持基于关键词的规则推理。
    规则数据从 JSON 文件加载，文件路径可通过配置或参数指定。
    
    节点类型：
        - Industry (行业): Tech, Food, Education, Fashion, Real Estate, etc.
        - Vibe (氛围): Minimalist, Energetic, Luxury, Friendly, Professional, etc.
        - Color (颜色): 十六进制颜色值
        - Font (字体): Sans-Serif, Serif, Handwritten, etc.
        - Layout (布局): Grid, Center, Diagonal, etc.
    
    边类型：
        - is_associated_with: 关联关系（行业/氛围 -> 颜色）
        - recommends: 推荐关系（行业/氛围 -> 字体/布局）
    """
    
    def __init__(self, rules_file: str = None):
        """
        初始化知识图谱
        
        Args:
            rules_file: 规则文件路径（可选，默认从配置读取）
        """
        self.graph = nx.DiGraph()
        
        # 优先使用参数，否则从配置读取，最后使用默认值
        if rules_file:
            self.rules_file = Path(rules_file)
        else:
            try:
                from ...core.config import settings
                config_path = settings.kg.RULES_FILE
                if config_path and Path(config_path).exists():
                    self.rules_file = Path(config_path)
                else:
                    self.rules_file = DEFAULT_KG_RULES_FILE
            except Exception:
                self.rules_file = DEFAULT_KG_RULES_FILE
        
        self._build_graph()
    
    def _load_rules_from_file(self) -> Dict[str, Any]:
        """从 JSON 文件加载规则数据"""
        if not self.rules_file.exists():
            logger.warning(f"规则文件不存在: {self.rules_file}，使用空规则")
            return {"industries": {}, "vibes": {}}
        
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"成功加载 KG 规则: {self.rules_file}")
            return data
        except Exception as e:
            logger.error(f"加载规则文件失败: {e}")
            return {"industries": {}, "vibes": {}}
    
    def _build_graph(self):
        """
        构建设计知识图谱
        
        从 JSON 文件加载规则数据，构建 NetworkX 有向图。
        """
        rules_data = self._load_rules_from_file()
        
        # 加载行业规则
        industries = rules_data.get("industries", {})
        for industry, config in industries.items():
            # 颜色关联
            for color in config.get("colors", []):
                self.graph.add_edge(industry, color, relation="is_associated_with")
            # 字体推荐
            for font in config.get("fonts", []):
                self.graph.add_edge(industry, font, relation="recommends")
            # 布局推荐
            for layout in config.get("layouts", []):
                self.graph.add_edge(industry, layout, relation="recommends")
        
        # 加载氛围规则
        vibes = rules_data.get("vibes", {})
        for vibe, config in vibes.items():
            # 颜色关联
            for color in config.get("colors", []):
                self.graph.add_edge(vibe, color, relation="is_associated_with")
            # 字体推荐
            for font in config.get("fonts", []):
                self.graph.add_edge(vibe, font, relation="recommends")
            # 布局推荐
            for layout in config.get("layouts", []):
                self.graph.add_edge(vibe, layout, relation="recommends")
        
        logger.info(f"KG 构建完成: {self.graph.number_of_nodes()} 节点, {self.graph.number_of_edges()} 边")
    
    def infer_rules(self, keywords: List[str]) -> Dict[str, List[str]]:
        """
        基于关键词推理设计规则
        
        Args:
            keywords: 用户意图关键词列表，如 ["Tech", "Promotion"]
        
        Returns:
            推理结果字典，包含推荐的颜色、字体、布局
            {
                "recommended_colors": ["#0066FF", "#FF0000"],
                "recommended_fonts": ["Sans-Serif"],
                "recommended_layouts": ["Grid", "Diagonal"]
            }
        """
        recommended_colors: Set[str] = set()
        recommended_fonts: Set[str] = set()
        recommended_layouts: Set[str] = set()
        
        # 遍历关键词，查找图中的节点
        for keyword in keywords:
            if keyword not in self.graph:
                continue
            
            # 获取该节点的所有邻居节点
            neighbors = self.graph.neighbors(keyword)
            
            for neighbor in neighbors:
                # 获取边的关系类型
                edge_data = self.graph.get_edge_data(keyword, neighbor)
                relation = edge_data.get("relation", "")
                
                # 根据关系类型分类推荐结果
                if relation == "is_associated_with":
                    # 颜色推荐（以 # 开头）
                    if neighbor.startswith("#"):
                        recommended_colors.add(neighbor)
                
                elif relation == "recommends":
                    # 字体推荐
                    if neighbor in ["Sans-Serif", "Serif", "Handwritten"]:
                        recommended_fonts.add(neighbor)
                    # 布局推荐
                    elif neighbor in ["Grid", "Center", "Diagonal"]:
                        recommended_layouts.add(neighbor)
        
        return {
            "recommended_colors": sorted(list(recommended_colors)),
            "recommended_fonts": sorted(list(recommended_fonts)),
            "recommended_layouts": sorted(list(recommended_layouts))
        }
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """
        获取图谱统计信息
        
        Returns:
            图谱统计信息
        """
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "rules_file": str(self.rules_file),
            "nodes": list(self.graph.nodes()),
        }
    
    def get_supported_keywords(self) -> Dict[str, List[str]]:
        """
        获取支持的关键词列表
        
        Returns:
            {"industries": [...], "vibes": [...]}
        """
        rules_data = self._load_rules_from_file()
        return {
            "industries": list(rules_data.get("industries", {}).keys()),
            "vibes": list(rules_data.get("vibes", {}).keys())
        }
    
    def visualize_subgraph(self, keyword: str) -> Dict[str, Any]:
        """
        可视化某个关键词的子图（用于调试）
        
        Args:
            keyword: 关键词
        
        Returns:
            子图信息
        """
        if keyword not in self.graph:
            return {"error": f"Keyword '{keyword}' not found in graph"}
        
        neighbors = list(self.graph.neighbors(keyword))
        
        return {
            "keyword": keyword,
            "neighbors": neighbors,
            "edges": [
                {
                    "from": keyword,
                    "to": neighbor,
                    "relation": self.graph.get_edge_data(keyword, neighbor).get("relation", "")
                }
                for neighbor in neighbors
            ]
        }


# ============================================================================
# 单元测试
# ============================================================================

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 80)
    print("Design Knowledge Graph - 单元测试")
    print("=" * 80)
    
    # 实例化知识图谱
    kg = DesignKnowledgeGraph()
    
    # 测试 1: 科技行业
    print("\n[测试 1] 输入关键词: ['Tech']")
    result_tech = kg.infer_rules(["Tech"])
    print(f"推荐颜色: {result_tech['recommended_colors']}")
    print(f"推荐字体: {result_tech['recommended_fonts']}")
    print(f"推荐布局: {result_tech['recommended_layouts']}")
    
    # 测试 2: 组合关键词（科技 + 促销）
    print("\n[测试 2] 输入关键词: ['Tech', 'Promotion']")
    result_combo = kg.infer_rules(["Tech", "Promotion"])
    print(f"推荐颜色: {result_combo['recommended_colors']}")
    print(f"推荐字体: {result_combo['recommended_fonts']}")
    print(f"推荐布局: {result_combo['recommended_layouts']}")
    
    # 测试 3: 支持的关键词
    print("\n[测试 3] 支持的关键词")
    supported = kg.get_supported_keywords()
    print(f"行业: {supported['industries']}")
    print(f"氛围: {supported['vibes']}")
    
    # 测试 4: 图谱统计
    print("\n[测试 4] 图谱统计信息")
    stats = kg.get_graph_stats()
    print(f"总节点数: {stats['total_nodes']}")
    print(f"总边数: {stats['total_edges']}")
    print(f"规则文件: {stats['rules_file']}")
    
    print("\n" + "=" * 80)
    print("✅ 所有测试完成！")
    print("=" * 80)

