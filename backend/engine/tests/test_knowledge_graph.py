"""
Knowledge Graph v2 测试
测试设计规则推理模块（语义推理链：Industry/Vibe -> Emotion -> Visual）
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
        stats = kg.get_graph_stats()
        assert stats["node_count"] > 0
        assert stats["edge_count"] > 0

    def test_infer_rules_tech(self, kg):
        """测试科技行业推理"""
        rules = kg.infer_rules(["Tech"])

        assert "emotions" in rules
        assert "color_palettes" in rules
        assert "typography_styles" in rules
        assert "layout_patterns" in rules

        assert len(rules["emotions"]) > 0
        assert "Sans-Serif" in rules["typography_styles"]

    def test_infer_rules_food(self, kg):
        """测试食品行业推理"""
        rules = kg.infer_rules(["Food"])

        assert len(rules["emotions"]) > 0
        assert len(rules["color_palettes"]) > 0

    def test_infer_rules_combined(self, kg):
        """测试组合关键词推理"""
        rules = kg.infer_rules(["Tech", "Minimalist"])

        assert len(rules["emotions"]) > 0
        assert len(rules["color_strategies"]) > 0
        assert len(rules["layout_patterns"]) > 0

    def test_infer_rules_luxury(self, kg):
        """测试奢华行业推理"""
        rules = kg.infer_rules(["Luxury"])

        assert len(rules["emotions"]) > 0
        assert "Serif" in rules["typography_styles"]

    def test_infer_rules_unknown_keyword(self, kg):
        """测试未知关键词返回空结果"""
        rules = kg.infer_rules(["UnknownKeyword"])

        assert rules["emotions"] == []
        assert rules["color_strategies"] == []
        assert rules["layout_patterns"] == []

    def test_infer_rules_empty_input(self, kg):
        """测试空输入返回空结果"""
        rules = kg.infer_rules([])

        assert rules["emotions"] == []
        assert rules["color_strategies"] == []
        assert rules["layout_patterns"] == []

    def test_get_graph_stats(self, kg):
        """测试图谱统计"""
        stats = kg.get_graph_stats()

        assert "node_count" in stats
        assert "edge_count" in stats
        assert "rules_file" in stats
        assert "version" in stats
        assert "industries" in stats
        assert "vibes" in stats

        assert stats["node_count"] > 0
        assert stats["edge_count"] > 0

    def test_get_supported_keywords(self, kg):
        """测试获取支持的关键词"""
        keywords = kg.get_supported_keywords()

        assert "industries" in keywords
        assert "vibes" in keywords
        assert len(keywords["industries"]) > 0
        assert "Tech" in keywords["industries"]

    def test_visualize_inference_chain(self, kg):
        """测试推理链可视化"""
        chain = kg.visualize_inference_chain("Tech")

        assert "keyword" in chain
        assert chain["keyword"] == "Tech"
