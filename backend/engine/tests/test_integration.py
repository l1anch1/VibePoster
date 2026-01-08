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
        
        # 1. KG 推理
        kg = DesignKnowledgeGraph()
        rules = kg.infer_rules(["Tech", "Promotion"])
        
        assert len(rules["recommended_colors"]) > 0
        
        # 2. RAG 检索
        rag = BrandKnowledgeBase()
        results = rag.search("华为配色", top_k=2)
        
        # 两个模块应该能正常协作
        assert rules is not None
        assert isinstance(results, list)
    
    def test_extract_keywords_from_prompt(self):
        """测试从 prompt 提取关键词"""
        from app.knowledge import DesignKnowledgeGraph
        
        kg = DesignKnowledgeGraph()
        
        # 模拟从 prompt 中提取关键词
        prompt = "为科技公司做一个促销海报"
        
        # 简单的关键词映射
        keyword_map = {
            "科技": "Tech",
            "促销": "Promotion"
        }
        
        keywords = []
        for cn, en in keyword_map.items():
            if cn in prompt:
                keywords.append(en)
        
        # 使用提取的关键词进行推理
        if keywords:
            rules = kg.infer_rules(keywords)
            assert len(rules["recommended_colors"]) > 0


class TestLayoutEngineIntegration:
    """布局引擎集成测试"""
    
    def test_full_layout_workflow(self):
        """测试完整布局工作流"""
        from app.core.layout import (
            VerticalContainer, TextBlock, ImageBlock, Style
        )
        
        # 1. 创建容器
        container = VerticalContainer(
            x=0, y=0, width=1080, padding=40, gap=20
        )
        
        # 2. 添加元素
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
        
        # 3. 排列
        container.arrange()
        
        # 4. 验证结果
        elements = container.get_all_elements()
        
        assert len(elements) == 3
        
        # 验证 y 坐标递增
        for i in range(1, len(elements)):
            assert elements[i]["y"] > elements[i-1]["y"]
    
    def test_layout_to_schema_conversion(self):
        """测试布局到 Schema 转换"""
        from app.services.renderer import RendererService
        from app.models.poster import PosterData
        
        renderer = RendererService()
        
        design_brief = {"padding": 40, "gap": 20}
        layout_dsl = [
            {"type": "text", "content": "Title", "fontSize": 48, "width": 1000},
            {"type": "image", "src": "img.jpg", "width": 1000, "height": 600}
        ]
        
        poster_data = renderer.render_poster(
            design_brief=design_brief,
            layout_dsl=layout_dsl,
            canvas_width=1080,
            canvas_height=1920
        )
        
        # 验证是 Pydantic 模型
        assert isinstance(poster_data, PosterData)
        
        # 验证可以序列化为 JSON
        json_data = poster_data.model_dump()
        assert "canvas" in json_data
        assert "layers" in json_data


class TestDesignBriefIntegration:
    """设计简报集成测试"""
    
    def test_design_brief_with_kg_rules(self):
        """测试设计简报包含 KG 规则"""
        from app.knowledge import DesignKnowledgeGraph
        
        kg = DesignKnowledgeGraph()
        
        # 模拟用户输入
        user_prompt = "为科技产品做一个促销海报"
        keywords = ["Tech", "Promotion"]
        
        # KG 推理
        kg_rules = kg.infer_rules(keywords)
        
        # 构建设计简报
        design_brief = {
            "title": "科技新品发布",
            "subtitle": "限时优惠",
            "user_prompt": user_prompt,
            "kg_rules": kg_rules,
            "primary_color": kg_rules["recommended_colors"][0] if kg_rules["recommended_colors"] else "#0066FF",
            "font_family": kg_rules["recommended_fonts"][0] if kg_rules["recommended_fonts"] else "Sans-Serif",
        }
        
        # 验证设计简报
        assert "kg_rules" in design_brief
        assert design_brief["primary_color"].startswith("#")
    
    def test_design_brief_with_brand_knowledge(self):
        """测试设计简报包含品牌知识"""
        from app.knowledge import BrandKnowledgeBase
        
        rag = BrandKnowledgeBase()
        
        # 检索品牌知识
        brand_name = "华为"
        results = rag.search(f"{brand_name}配色", top_k=1)
        
        # 构建设计简报
        design_brief = {
            "brand_name": brand_name,
            "brand_knowledge": results,
        }
        
        # 验证设计简报
        assert "brand_name" in design_brief
        assert "brand_knowledge" in design_brief


class TestEndToEndWorkflow:
    """端到端工作流测试"""
    
    def test_complete_poster_generation_flow(self):
        """测试完整海报生成流程（模拟）"""
        from app.knowledge import DesignKnowledgeGraph, BrandKnowledgeBase
        from app.core.layout import VerticalContainer, TextBlock, ImageBlock
        from app.services.renderer import RendererService
        
        # 步骤 1: 用户输入
        user_prompt = "为科技产品做一个促销海报"
        brand_name = "华为"
        
        # 步骤 2: KG 推理
        kg = DesignKnowledgeGraph()
        keywords = ["Tech", "Promotion"]
        kg_rules = kg.infer_rules(keywords)
        
        # 步骤 3: RAG 检索
        rag = BrandKnowledgeBase()
        brand_info = rag.search(f"{brand_name}配色", top_k=1)
        
        # 步骤 4: 构建设计简报
        design_brief = {
            "title": "华为 Mate 60",
            "subtitle": "遥遥领先",
            "primary_color": kg_rules["recommended_colors"][0] if kg_rules["recommended_colors"] else "#C32228",
            "kg_rules": kg_rules,
            "brand_knowledge": brand_info,
        }
        
        # 步骤 5: 布局渲染
        renderer = RendererService()
        layout_dsl = [
            {
                "type": "text",
                "content": design_brief["title"],
                "fontSize": 48,
                "color": design_brief["primary_color"],
                "width": 1000
            },
            {
                "type": "text",
                "content": design_brief["subtitle"],
                "fontSize": 24,
                "width": 1000
            },
            {
                "type": "image",
                "src": "https://example.com/product.jpg",
                "width": 1000,
                "height": 600
            }
        ]
        
        poster_data = renderer.render_poster(
            design_brief=design_brief,
            layout_dsl=layout_dsl,
            canvas_width=1080,
            canvas_height=1920
        )
        
        # 验证最终结果
        assert poster_data is not None
        assert poster_data.canvas.width == 1080
        assert len(poster_data.layers) == 3
        
        # 验证可以导出 JSON
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
        
        # 使用无效关键词
        rules = kg.infer_rules(["InvalidKeyword1", "InvalidKeyword2"])
        
        # 应该返回空列表，不是异常
        assert rules["recommended_colors"] == []
        assert rules["recommended_fonts"] == []
        assert rules["recommended_layouts"] == []
    
    def test_renderer_with_empty_dsl(self):
        """测试渲染器处理空 DSL"""
        from app.services.renderer import RendererService
        
        renderer = RendererService()
        
        poster_data = renderer.render_poster(
            design_brief={},
            layout_dsl=[],
            canvas_width=1080,
            canvas_height=1920
        )
        
        # 应该返回有效的海报数据，只是图层为空
        assert poster_data is not None
        assert poster_data.canvas.width == 1080
        assert len(poster_data.layers) == 0

