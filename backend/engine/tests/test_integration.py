"""
集成测试
测试完整的数据流和模块协作
"""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestKGAndRAGIntegration:
    """KG 和 RAG 集成测试"""

    def test_kg_infer_and_rag_search(self):
        """测试 KG 推理 + RAG 检索协作"""
        from app.knowledge import DesignKnowledgeGraph, BrandKnowledgeBase

        kg = DesignKnowledgeGraph()
        rules = kg.infer_rules(["Tech"])

        assert len(rules["emotions"]) > 0

        rag = BrandKnowledgeBase()
        results = rag.search("华为配色", top_k=2)

        assert rules is not None
        assert isinstance(results, list)

    def test_extract_keywords_from_prompt(self):
        """测试从 prompt 提取关键词并推理"""
        from app.knowledge import DesignKnowledgeGraph

        kg = DesignKnowledgeGraph()

        prompt = "为科技公司做一个极简风格海报"
        keyword_map = {"科技": "Tech", "极简": "Minimalist"}

        keywords = [en for cn, en in keyword_map.items() if cn in prompt]

        if keywords:
            rules = kg.infer_rules(keywords)
            assert len(rules["emotions"]) > 0
            assert len(rules["color_palettes"]) > 0


class TestLayoutEngineIntegration:
    """布局引擎集成测试"""

    def test_full_layout_workflow(self):
        """测试完整布局工作流"""
        from app.core.layout import (
            VerticalContainer, TextBlock, ImageBlock, Style
        )

        container = VerticalContainer(
            x=0, y=0, width=1080, padding=40, gap=20
        )

        title = TextBlock(
            content="测试标题",
            font_size=48,
            max_width=1000,
            style=Style(font_size=48, font_weight="bold", color="#FF0000")
        )

        subtitle = TextBlock(
            content="测试副标题",
            font_size=24,
            max_width=1000
        )

        image = ImageBlock(
            src="https://example.com/image.jpg",
            width=1000,
            height=600
        )

        container.add(title).add(subtitle).add(image)
        container.arrange()

        elements = container.get_all_elements()

        assert len(elements) == 3

        for i in range(1, len(elements)):
            assert elements[i]["y"] > elements[i - 1]["y"]

    def test_layout_to_schema_conversion(self):
        """测试布局到 Schema 转换"""
        from app.services.renderer import RendererService
        from app.models.poster import PosterData

        renderer = RendererService()

        dsl = [
            {"command": "add_title", "content": "Title", "font_size": 48},
            {"command": "add_image", "src": "img.jpg", "width": 1000, "height": 600},
        ]

        container = renderer.parse_dsl_and_build_layout(dsl, 1080, 1920)
        poster_data = renderer.convert_to_pydantic_schema(container)

        assert isinstance(poster_data, PosterData)

        json_data = poster_data.model_dump()
        assert "canvas" in json_data
        assert "layers" in json_data


class TestDesignBriefIntegration:
    """设计简报集成测试"""

    def test_design_brief_with_kg_rules(self):
        """测试设计简报包含 KG 规则"""
        from app.knowledge import DesignKnowledgeGraph

        kg = DesignKnowledgeGraph()
        keywords = ["Tech"]
        kg_rules = kg.infer_rules(keywords)

        primary_colors = kg_rules.get("color_palettes", {}).get("primary", [])

        design_brief = {
            "title": "科技新品发布",
            "user_prompt": "为科技产品做海报",
            "kg_rules": kg_rules,
            "primary_color": primary_colors[0] if primary_colors else "#0066FF",
        }

        assert "kg_rules" in design_brief
        assert design_brief["primary_color"].startswith("#")

    def test_design_brief_with_brand_knowledge(self):
        """测试设计简报包含品牌知识"""
        from app.knowledge import BrandKnowledgeBase

        rag = BrandKnowledgeBase()
        results = rag.search("华为配色", top_k=1)

        design_brief = {
            "brand_name": "华为",
            "brand_knowledge": results,
        }

        assert "brand_name" in design_brief
        assert "brand_knowledge" in design_brief


class TestEndToEndWorkflow:
    """端到端工作流测试"""

    def test_complete_poster_generation_flow(self):
        """测试完整海报生成流程（模拟，不调用 LLM）"""
        from app.knowledge import DesignKnowledgeGraph, BrandKnowledgeBase
        from app.services.renderer import RendererService

        # 1. KG 推理
        kg = DesignKnowledgeGraph()
        kg_rules = kg.infer_rules(["Tech"])

        # 2. RAG 检索
        rag = BrandKnowledgeBase()
        brand_info = rag.search("华为配色", top_k=1)

        # 3. 构建设计简报
        primary_colors = kg_rules.get("color_palettes", {}).get("primary", [])
        design_brief = {
            "title": "华为 Mate 60",
            "subtitle": "遥遥领先",
            "primary_color": primary_colors[0] if primary_colors else "#C32228",
            "kg_rules": kg_rules,
            "brand_knowledge": brand_info,
        }

        # 4. 布局渲染
        renderer = RendererService()
        dsl = [
            {"command": "add_title", "content": design_brief["title"], "font_size": 48},
            {"command": "add_subtitle", "content": design_brief["subtitle"], "font_size": 24},
            {"command": "add_image", "src": "https://example.com/product.jpg", "width": 800, "height": 600},
        ]

        container = renderer.parse_dsl_and_build_layout(dsl, 1080, 1920)
        poster_data = renderer.convert_to_pydantic_schema(container)

        assert poster_data is not None
        assert poster_data.canvas.width == 1080
        assert len(poster_data.layers) == 3

        json_output = poster_data.model_dump()
        assert "canvas" in json_output
        assert "layers" in json_output
        assert len(json_output["layers"]) == 3


class TestErrorHandling:
    """错误处理测试"""

    def test_kg_with_invalid_keywords(self):
        """测试 KG 处理无效关键词"""
        from app.knowledge import DesignKnowledgeGraph

        kg = DesignKnowledgeGraph()
        rules = kg.infer_rules(["InvalidKeyword1", "InvalidKeyword2"])

        assert rules["emotions"] == []
        assert rules["color_strategies"] == []
        assert rules["layout_patterns"] == []

    def test_renderer_with_empty_dsl(self):
        """测试渲染器处理空 DSL"""
        from app.services.renderer import RendererService

        renderer = RendererService()
        container = renderer.parse_dsl_and_build_layout([], 1080, 1920)
        poster_data = renderer.convert_to_pydantic_schema(container)

        assert poster_data is not None
        assert poster_data.canvas.width == 1080
        assert len(poster_data.layers) == 0
