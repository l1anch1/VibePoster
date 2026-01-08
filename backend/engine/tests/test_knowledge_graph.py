"""
Knowledge Graph 测试
测试设计规则推理模块
"""
import pytest
from app.knowledge.kg import DesignKnowledgeGraph


class TestDesignKnowledgeGraph:
    """设计知识图谱测试类"""
    
    @pytest.fixture
    def kg(self):
        """创建知识图谱实例"""
        return DesignKnowledgeGraph()
    
    def test_graph_initialization(self, kg):
        """测试图谱初始化"""
        assert kg.graph is not None
        assert kg.graph.number_of_nodes() > 0
        assert kg.graph.number_of_edges() > 0
    
    def test_infer_rules_tech(self, kg):
        """测试科技行业推理"""
        rules = kg.infer_rules(["Tech"])
        
        assert "recommended_colors" in rules
        assert "recommended_fonts" in rules
        assert "recommended_layouts" in rules
        
        # 科技行业应该推荐蓝色系和无衬线字体
        assert "#0066FF" in rules["recommended_colors"]
        assert "Sans-Serif" in rules["recommended_fonts"]
    
    def test_infer_rules_food(self, kg):
        """测试食品行业推理"""
        rules = kg.infer_rules(["Food"])
        
        # 食品行业应该推荐暖色
        assert "#FFA500" in rules["recommended_colors"]  # 橙色
        assert "Handwritten" in rules["recommended_fonts"]
    
    def test_infer_rules_promotion(self, kg):
        """测试促销氛围推理"""
        rules = kg.infer_rules(["Promotion"])
        
        # 促销应该推荐红色、金色
        assert "#FF0000" in rules["recommended_colors"]
        assert "Diagonal" in rules["recommended_layouts"]
    
    def test_infer_rules_combined(self, kg):
        """测试组合关键词推理"""
        rules = kg.infer_rules(["Tech", "Promotion"])
        
        # 应该同时包含科技和促销的推荐
        assert "#0066FF" in rules["recommended_colors"]  # 科技蓝
        assert "#FF0000" in rules["recommended_colors"]  # 促销红
    
    def test_infer_rules_luxury(self, kg):
        """测试奢华氛围推理"""
        rules = kg.infer_rules(["Luxury"])
        
        # 奢华应该推荐金色、衬线字体
        assert "#FFD700" in rules["recommended_colors"]
        assert "Serif" in rules["recommended_fonts"]
    
    def test_infer_rules_unknown_keyword(self, kg):
        """测试未知关键词"""
        rules = kg.infer_rules(["UnknownKeyword"])
        
        # 未知关键词应该返回空列表
        assert rules["recommended_colors"] == []
        assert rules["recommended_fonts"] == []
        assert rules["recommended_layouts"] == []
    
    def test_infer_rules_empty_input(self, kg):
        """测试空输入"""
        rules = kg.infer_rules([])
        
        assert rules["recommended_colors"] == []
        assert rules["recommended_fonts"] == []
        assert rules["recommended_layouts"] == []
    
    def test_get_graph_stats(self, kg):
        """测试图谱统计"""
        stats = kg.get_graph_stats()
        
        assert "total_nodes" in stats
        assert "total_edges" in stats
        assert "nodes" in stats
        assert "rules_file" in stats
        
        assert stats["total_nodes"] > 0
        assert stats["total_edges"] > 0
    
    def test_visualize_subgraph(self, kg):
        """测试子图可视化"""
        subgraph = kg.visualize_subgraph("Tech")
        
        assert "keyword" in subgraph
        assert "neighbors" in subgraph
        assert "edges" in subgraph
        
        assert subgraph["keyword"] == "Tech"
        assert len(subgraph["neighbors"]) > 0
    
    def test_visualize_subgraph_not_found(self, kg):
        """测试不存在的关键词子图"""
        subgraph = kg.visualize_subgraph("NotExists")
        
        assert "error" in subgraph

