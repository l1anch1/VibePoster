"""
Renderer Service 测试
测试 OOP 布局到 Schema 的序列化适配器
"""
import pytest
from app.services.renderer import RendererService, create_simple_poster_from_text
from app.models.poster import PosterData, TextLayer, ImageLayer


class TestRendererService:
    """渲染服务测试类"""
    
    @pytest.fixture
    def renderer(self):
        """创建渲染服务实例"""
        return RendererService()
    
    def test_initialization(self, renderer):
        """测试初始化"""
        assert renderer is not None
    
    def test_parse_text_dsl(self, renderer):
        """测试解析文本 DSL 指令"""
        dsl_command = {
            "type": "text",
            "content": "测试标题",
            "fontSize": 48,
            "color": "#FF0000",
            "width": 1000
        }
        
        element = renderer._parse_dsl_command(dsl_command)
        
        assert element is not None
        assert element.content == "测试标题"
        assert element.font_size == 48
    
    def test_parse_image_dsl(self, renderer):
        """测试解析图片 DSL 指令"""
        dsl_command = {
            "type": "image",
            "src": "https://example.com/image.jpg",
            "width": 800,
            "height": 600
        }
        
        element = renderer._parse_dsl_command(dsl_command)
        
        assert element is not None
        assert element.src == "https://example.com/image.jpg"
        assert element.width == 800
        assert element.height == 600
    
    def test_parse_vertical_container_dsl(self, renderer):
        """测试解析垂直容器 DSL 指令"""
        dsl_command = {
            "type": "vertical_container",
            "width": 1080,
            "padding": 40,
            "gap": 20,
            "elements": [
                {"type": "text", "content": "Title", "fontSize": 48, "width": 1000},
                {"type": "text", "content": "Subtitle", "fontSize": 24, "width": 1000}
            ]
        }
        
        element = renderer._parse_dsl_command(dsl_command)
        
        assert element is not None
        assert len(element.elements) == 2
    
    def test_parse_invalid_dsl(self, renderer):
        """测试解析无效 DSL 指令"""
        dsl_command = {
            "type": "invalid_type"
        }
        
        with pytest.raises(ValueError):
            renderer._parse_dsl_command(dsl_command)
    
    def test_to_pydantic_text_layer(self, renderer):
        """测试转换为 Pydantic 文本图层"""
        element_data = {
            "type": "text",
            "content": "测试",
            "x": 100,
            "y": 200,
            "width": 500,
            "height": 50,
            "fontSize": 24,
            "color": "#000000"
        }
        
        layer = renderer._to_pydantic_layer(element_data)
        
        assert isinstance(layer, TextLayer)
        assert layer.content == "测试"
        assert layer.x == 100
        assert layer.y == 200
    
    def test_to_pydantic_image_layer(self, renderer):
        """测试转换为 Pydantic 图片图层"""
        element_data = {
            "type": "image",
            "src": "https://example.com/image.jpg",
            "x": 0,
            "y": 0,
            "width": 1080,
            "height": 1920
        }
        
        layer = renderer._to_pydantic_layer(element_data)
        
        assert isinstance(layer, ImageLayer)
        assert layer.src == "https://example.com/image.jpg"
    
    def test_render_poster_basic(self, renderer):
        """测试基本海报渲染"""
        design_brief = {
            "title": "测试海报",
            "padding": 40,
            "gap": 20
        }
        
        layout_dsl = [
            {
                "type": "text",
                "content": "标题",
                "fontSize": 48,
                "color": "#FF0000",
                "width": 1000
            },
            {
                "type": "image",
                "src": "https://example.com/image.jpg",
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
        
        assert isinstance(poster_data, PosterData)
        assert poster_data.canvas.width == 1080
        assert len(poster_data.layers) == 2
    
    def test_render_poster_has_type_field(self, renderer):
        """测试渲染的海报图层包含 type 字段"""
        design_brief = {}
        layout_dsl = [
            {"type": "text", "content": "Test", "fontSize": 24, "width": 500}
        ]
        
        poster_data = renderer.render_poster(
            design_brief=design_brief,
            layout_dsl=layout_dsl,
            canvas_width=1080,
            canvas_height=1920
        )
        
        for layer in poster_data.layers:
            layer_dict = layer.model_dump()
            assert "type" in layer_dict
    
    def test_render_poster_auto_layout(self, renderer):
        """测试自动布局计算"""
        design_brief = {"padding": 40, "gap": 20}
        layout_dsl = [
            {"type": "text", "content": "Title", "fontSize": 48, "width": 1000},
            {"type": "text", "content": "Subtitle", "fontSize": 24, "width": 1000},
            {"type": "image", "src": "img.jpg", "width": 1000, "height": 600}
        ]
        
        poster_data = renderer.render_poster(
            design_brief=design_brief,
            layout_dsl=layout_dsl,
            canvas_width=1080,
            canvas_height=1920
        )
        
        # 验证 y 坐标递增
        prev_y = -1
        for layer in poster_data.layers:
            layer_dict = layer.model_dump()
            assert layer_dict["y"] > prev_y
            prev_y = layer_dict["y"]


class TestCreateSimplePosterFromText:
    """简单海报生成函数测试"""
    
    def test_basic_creation(self):
        """测试基本创建"""
        poster = create_simple_poster_from_text(
            title="测试标题",
            subtitle="测试副标题",
            canvas_width=1080,
            canvas_height=1920
        )
        
        assert isinstance(poster, PosterData)
        assert poster.canvas.width == 1080
        assert poster.canvas.height == 1920
    
    def test_with_custom_colors(self):
        """测试自定义颜色"""
        poster = create_simple_poster_from_text(
            title="Test",
            canvas_width=1080,
            canvas_height=1920,
            primary_color="#FF6700",
            background_color="#FFF8F0"
        )
        
        assert poster.canvas.backgroundColor == "#FFF8F0"
    
    def test_has_text_layers(self):
        """测试包含文本图层"""
        poster = create_simple_poster_from_text(
            title="Title",
            subtitle="Subtitle",
            canvas_width=1080,
            canvas_height=1920
        )
        
        # 至少应该有标题和副标题两个文本图层
        text_layers = [
            l for l in poster.layers 
            if l.model_dump().get("type") == "text"
        ]
        
        assert len(text_layers) >= 2

