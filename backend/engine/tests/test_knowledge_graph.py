"""
Knowledge Graph v3 测试
测试五层设计知识本体（Industry/Vibe → Emotion → Visual Strategy）
"""
import pytest
from app.knowledge.kg import DesignKnowledgeGraph


class TestDesignKnowledgeGraph:
    """设计知识本体测试"""

    @pytest.fixture
    def kg(self):
        return DesignKnowledgeGraph()

    # ==================================================================
    # 初始化与统计
    # ==================================================================

    def test_graph_initialization(self, kg):
        """本体图应包含五层节点和四种边"""
        assert kg.graph is not None
        stats = kg.get_graph_stats()
        assert stats["node_count"] > 0
        assert stats["edge_count"] > 0
        assert "node_type_counts" in stats
        assert "edge_type_counts" in stats

    def test_node_type_coverage(self, kg):
        """应包含全部 7 种节点类型"""
        stats = kg.get_graph_stats()
        ntc = stats["node_type_counts"]
        assert ntc.get("emotion", 0) >= 9
        assert ntc.get("industry", 0) >= 8
        assert ntc.get("vibe", 0) >= 7
        assert ntc.get("color_strategy", 0) >= 10
        assert ntc.get("typography_style", 0) >= 5
        assert ntc.get("layout_pattern", 0) >= 10
        assert ntc.get("decoration_theme", 0) >= 6

    def test_edge_type_coverage(self, kg):
        """应包含 EMBODIES, EVOKES, AVOIDS, CONFLICTS_WITH 四种边"""
        stats = kg.get_graph_stats()
        etc = stats["edge_type_counts"]
        assert "embodies" in etc
        assert "evokes" in etc
        assert "avoids" in etc
        assert "conflicts_with" in etc

    def test_get_graph_stats(self, kg):
        """统计信息结构完整"""
        stats = kg.get_graph_stats()
        for key in ("node_count", "edge_count", "rules_file", "version",
                     "industries", "vibes", "emotions"):
            assert key in stats
        assert stats["node_count"] > 0
        assert stats["edge_count"] > 0

    def test_get_supported_keywords(self, kg):
        keywords = kg.get_supported_keywords()
        assert "industries" in keywords
        assert "vibes" in keywords
        assert "Tech" in keywords["industries"]
        assert "Finance" in keywords["industries"]
        assert "Beauty" in keywords["industries"]
        assert "Retro" in keywords["vibes"]
        assert "Futuristic" in keywords["vibes"]

    # ==================================================================
    # 基本推理 — 与 v2 输出格式兼容
    # ==================================================================

    def test_infer_rules_tech(self, kg):
        """Tech 推理应产出 Trust+Innovation 的视觉策略"""
        rules = kg.infer_rules(["Tech"])
        assert "emotions" in rules
        assert "color_palettes" in rules
        assert "typography_styles" in rules
        assert "layout_patterns" in rules
        assert "decoration_styles" in rules

        assert len(rules["emotions"]) > 0
        assert "Trust" in rules["emotions"]
        assert "Innovation" in rules["emotions"]
        assert "Sans-Serif" in rules["typography_styles"]
        assert len(rules["color_strategies"]) > 0
        assert len(rules["layout_patterns"]) > 0

    def test_infer_rules_food(self, kg):
        rules = kg.infer_rules(["Food"])
        assert len(rules["emotions"]) > 0
        assert len(rules["color_palettes"]) > 0
        assert "Warmth" in rules["emotions"]

    def test_infer_rules_luxury(self, kg):
        rules = kg.infer_rules(["Luxury"])
        assert len(rules["emotions"]) > 0
        assert "Premium" in rules["emotions"]
        assert "Serif" in rules["typography_styles"]

    def test_infer_rules_combined(self, kg):
        rules = kg.infer_rules(["Tech", "Minimalist"])
        assert len(rules["emotions"]) > 0
        assert len(rules["color_strategies"]) > 0
        assert len(rules["layout_patterns"]) > 0

    def test_infer_rules_empty_input(self, kg):
        rules = kg.infer_rules([])
        assert rules["emotions"] == []
        assert rules["color_strategies"] == []
        assert rules["layout_patterns"] == []

    def test_infer_rules_unknown_keyword(self, kg):
        rules = kg.infer_rules(["UnknownKeyword"])
        assert rules["emotions"] == []
        assert rules["color_strategies"] == []
        assert rules["layout_patterns"] == []

    # ==================================================================
    # 新行业 / 新风格
    # ==================================================================

    def test_infer_rules_finance(self, kg):
        """Finance 应激活 Trust + Premium"""
        rules = kg.infer_rules(["Finance"])
        assert "Trust" in rules["emotions"]
        assert "Premium" in rules["emotions"]
        assert len(rules["decoration_styles"]) > 0

    def test_infer_rules_beauty(self, kg):
        """Beauty 应激活 Premium + Freshness + Warmth"""
        rules = kg.infer_rules(["Beauty"])
        emotions = set(rules["emotions"])
        assert "Premium" in emotions
        assert "Freshness" in emotions

    def test_infer_rules_retro(self, kg):
        rules = kg.infer_rules(["Retro"])
        assert "Warmth" in rules["emotions"]

    def test_infer_rules_futuristic(self, kg):
        rules = kg.infer_rules(["Futuristic"])
        assert "Innovation" in rules["emotions"]

    # ==================================================================
    # 新情绪
    # ==================================================================

    def test_emotion_serenity_reachable(self, kg):
        """Serenity 应可通过 Minimalist 或 Healthcare 到达"""
        rules_m = kg.infer_rules(["Minimalist"])
        rules_h = kg.infer_rules(["Healthcare"])
        assert "Serenity" in rules_m["emotions"]
        assert "Serenity" in rules_h["emotions"]

    def test_emotion_urgency_reachable(self, kg):
        """Urgency 应可通过 Bold 到达"""
        rules = kg.infer_rules(["Bold"])
        assert "Urgency" in rules["emotions"]

    # ==================================================================
    # 装饰主题流通
    # ==================================================================

    def test_decoration_styles_populated(self, kg):
        """decoration_styles 应包含 divider/overlay/shape"""
        rules = kg.infer_rules(["Tech"])
        ds = rules["decoration_styles"]
        assert "divider" in ds
        assert "overlay" in ds
        assert "shape" in ds

    # ==================================================================
    # 冲突消解
    # ==================================================================

    def test_conflicts_monochromatic_vs_multicolor(self, kg):
        """同时激活 Trust(Monochromatic) 和 Playfulness(Multi-color) 时应消解冲突"""
        rules = kg.infer_rules(["Education"])
        cs = set(rules["color_strategies"])
        has_mono = "Monochromatic" in cs
        has_multi = "Multi-color" in cs
        assert not (has_mono and has_multi), "互斥策略不应同时出现"

    # ==================================================================
    # AVOIDS 过滤
    # ==================================================================

    def test_avoids_tech_no_earth_tones(self, kg):
        """Tech 应通过 AVOIDS 过滤掉 Earth-tones"""
        rules = kg.infer_rules(["Tech"])
        assert "Earth-tones" not in rules["color_strategies"]

    def test_avoids_luxury_no_multicolor(self, kg):
        """Luxury 应通过 AVOIDS 过滤掉 Multi-color"""
        rules = kg.infer_rules(["Luxury"])
        assert "Multi-color" not in rules["color_strategies"]

    # ==================================================================
    # 推理链追踪（v3 新增）
    # ==================================================================

    def test_inference_traces(self, kg):
        """infer_with_traces 应返回完整推理链"""
        result = kg.infer_with_traces(["Tech"])
        assert len(result.inference_traces) > 0

        trace = result.inference_traces[0]
        assert len(trace.path) == 3
        assert trace.path[0] == "Tech"
        assert trace.relation_chain == ["EMBODIES", "EVOKES"]
        assert trace.weight > 0

    # ==================================================================
    # 推理链可视化
    # ==================================================================

    def test_visualize_inference_chain(self, kg):
        chain = kg.visualize_inference_chain("Tech")
        assert chain["keyword"] == "Tech"
        assert "emotions" in chain
        assert "visual_elements" in chain

    def test_visualize_unknown_keyword(self, kg):
        chain = kg.visualize_inference_chain("NonExistent")
        assert "error" in chain

    # ==================================================================
    # 设计原则与避免项
    # ==================================================================

    def test_design_principles_from_entry(self, kg):
        rules = kg.infer_rules(["Tech"])
        assert len(rules["design_principles"]) > 0
        assert "Clean interfaces" in rules["design_principles"]

    def test_avoid_texts_from_entry(self, kg):
        rules = kg.infer_rules(["Tech"])
        assert len(rules["avoid"]) > 0
        assert "Script fonts" in rules["avoid"]

    # ==================================================================
    # to_dict 兼容性（不含 inference_traces）
    # ==================================================================

    def test_to_dict_excludes_traces(self, kg):
        """to_dict() 输出不含 inference_traces，兼容下游"""
        result = kg.infer_with_traces(["Tech"])
        d = result.to_dict()
        assert "inference_traces" not in d
        assert "emotions" in d
        assert "color_strategies" in d
