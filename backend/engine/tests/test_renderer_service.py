"""
Renderer Service 测试
测试 DSL 解析（绝对坐标模式）、Schema 转换
"""
import pytest
from app.services.renderer import RendererService, create_simple_poster_from_text
from app.models.poster import PosterData, TextLayer, ImageLayer


class TestRendererService:
    """渲染服务测试类"""

    @pytest.fixture
    def renderer(self):
        return RendererService()

    def test_initialization(self, renderer):
        assert renderer is not None
        assert renderer.dsl_parser is not None
        assert renderer.schema_converter is not None

    def test_parse_dsl_text(self, renderer):
        """解析文本指令 → 返回元素列表"""
        dsl = [{
            "command": "add_title", "content": "测试标题", "font_size": 48,
            "x": 100, "y": 200, "width": 880, "height": 80,
        }]
        elements = renderer.parse_dsl_and_build_layout(dsl, 1080, 1920)

        assert isinstance(elements, list)
        assert len(elements) == 1
        assert elements[0]["type"] == "text"
        assert elements[0]["content"] == "测试标题"

    def test_parse_dsl_image(self, renderer):
        dsl = [{
            "command": "add_image", "src": "https://example.com/img.jpg",
            "x": 0, "y": 0, "width": 1080, "height": 1920,
            "layer_type": "background",
        }]
        elements = renderer.parse_dsl_and_build_layout(dsl, 1080, 1920)

        assert isinstance(elements, list)
        assert len(elements) == 1
        assert elements[0]["type"] == "image"

    def test_convert_to_pydantic_text_layer(self, renderer):
        dsl = [{
            "command": "add_title", "content": "测试", "font_size": 24,
            "x": 40, "y": 300, "width": 1000, "height": 60,
        }]
        elements = renderer.parse_dsl_and_build_layout(dsl, 1080, 1920)
        poster = renderer.convert_to_pydantic_schema(elements)

        assert isinstance(poster, PosterData)
        text_layers = [l for l in poster.layers if isinstance(l, TextLayer)]
        assert len(text_layers) == 1
        assert text_layers[0].content == "测试"

    def test_convert_to_pydantic_image_layer(self, renderer):
        dsl = [{
            "command": "add_image", "src": "https://example.com/img.jpg",
            "x": 0, "y": 0, "width": 1080, "height": 1920,
            "layer_type": "background",
        }]
        elements = renderer.parse_dsl_and_build_layout(dsl, 1080, 1920)
        poster = renderer.convert_to_pydantic_schema(elements)

        assert isinstance(poster, PosterData)
        img_layers = [l for l in poster.layers if isinstance(l, ImageLayer)]
        assert len(img_layers) == 1

    def test_full_render_flow(self, renderer):
        dsl = [
            {"command": "add_image", "src": "bg.jpg", "x": 0, "y": 0, "width": 1080, "height": 1920, "layer_type": "background"},
            {"command": "add_title", "content": "标题", "font_size": 48, "x": 100, "y": 200, "width": 880, "height": 80},
            {"command": "add_subtitle", "content": "副标题", "font_size": 24, "x": 100, "y": 300, "width": 880, "height": 50},
        ]
        elements = renderer.parse_dsl_and_build_layout(dsl, 1080, 1920)
        poster = renderer.convert_to_pydantic_schema(elements)

        assert isinstance(poster, PosterData)
        assert poster.canvas.width == 1080
        assert len(poster.layers) == 3

    def test_layers_have_type_field(self, renderer):
        dsl = [{"command": "add_title", "content": "Test", "font_size": 24, "x": 40, "y": 100, "width": 1000, "height": 50}]
        elements = renderer.parse_dsl_and_build_layout(dsl, 1080, 1920)
        poster = renderer.convert_to_pydantic_schema(elements)

        for layer in poster.layers:
            layer_dict = layer.model_dump()
            assert "type" in layer_dict

    def test_absolute_coordinates_preserved(self, renderer):
        """绝对坐标模式：指定的 x, y 应保持（除越界修正外）"""
        dsl = [
            {"command": "add_title", "content": "Top",    "font_size": 48, "x": 100, "y": 100, "width": 880, "height": 80},
            {"command": "add_subtitle", "content": "Mid",  "font_size": 32, "x": 100, "y": 500, "width": 880, "height": 50},
            {"command": "add_text", "content": "Bottom",   "font_size": 24, "x": 100, "y": 900, "width": 880, "height": 40},
        ]
        elements = renderer.parse_dsl_and_build_layout(dsl, 1080, 1920)
        poster = renderer.convert_to_pydantic_schema(elements)

        ys = [l.y for l in poster.layers]
        assert ys[0] == 100
        assert ys[1] == 500
        assert ys[2] == 900

    def test_clamp_bounds(self, renderer):
        """越界元素应被修正到画布内"""
        dsl = [{
            "command": "add_title", "content": "Out", "font_size": 24,
            "x": -100, "y": -50, "width": 2000, "height": 40,
        }]
        elements = renderer.parse_dsl_and_build_layout(dsl, 1080, 1920)

        assert elements[0]["x"] >= 20
        assert elements[0]["y"] >= 20
        assert elements[0]["width"] <= 1080

    def test_unknown_command_ignored(self, renderer):
        dsl = [{"command": "unknown_cmd", "x": 0, "y": 0, "width": 100, "height": 100}]
        elements = renderer.parse_dsl_and_build_layout(dsl, 1080, 1920)
        assert len(elements) == 0


class TestCreateSimplePosterFromText:
    """简单海报生成函数测试"""

    def test_basic_creation(self):
        poster = create_simple_poster_from_text(
            title="测试标题", subtitle="测试副标题",
            canvas_width=1080, canvas_height=1920,
        )
        assert isinstance(poster, PosterData)
        assert poster.canvas.width == 1080

    def test_title_only(self):
        poster = create_simple_poster_from_text(
            title="Title", canvas_width=1080, canvas_height=1920,
        )
        assert isinstance(poster, PosterData)
        assert len(poster.layers) >= 1

    def test_has_text_layers(self):
        poster = create_simple_poster_from_text(
            title="Title", subtitle="Subtitle",
            canvas_width=1080, canvas_height=1920,
        )
        text_layers = [l for l in poster.layers if l.model_dump().get("type") == "text"]
        assert len(text_layers) >= 2
