"""
OOP Layout Engine + LayoutBuilder 集成测试

测试两层：
1. 基础层：OOP 布局引擎组件（TextBlock, ImageBlock, ShapeBlock, Container）
2. 集成层：LayoutBuilder 将语义 DSL → OOP 容器 → 扁平元素列表
"""
import sys
import pytest
from app.core.layout import (
    Element,
    TextBlock,
    ImageBlock,
    ShapeBlock,
    Container,
    VerticalContainer,
    HorizontalContainer,
    Style,
)

_builder_available = False
try:
    from app.services.renderer.layout_builder import (
        LayoutBuilder,
        STRATEGIES,
        VALID_STRATEGIES,
        DEFAULT_STRATEGY,
        _classify_instructions,
    )
    _builder_available = True
except ImportError:
    pass

needs_builder = pytest.mark.skipif(
    not _builder_available,
    reason="LayoutBuilder 依赖链不完整（缺少 google.genai 等）"
)


# ============================================================================
# 一、基础 OOP 组件测试
# ============================================================================

class TestStyle:
    def test_default_values(self):
        style = Style()
        assert style.font_size == 16
        assert style.font_family == "Arial"
        assert style.font_weight == "normal"
        assert style.color == "#000000"
        assert style.text_align == "left"
        assert style.opacity == 1.0

    def test_custom_values(self):
        style = Style(font_size=24, font_family="Helvetica", font_weight="bold", color="#FF0000")
        assert style.font_size == 24
        assert style.font_family == "Helvetica"


class TestTextBlock:
    def test_basic_creation(self):
        text = TextBlock(content="Hello World", font_size=24, max_width=400)
        assert text.content == "Hello World"
        assert text.font_size == 24
        assert text.width == 400

    def test_auto_height_calculation(self):
        short = TextBlock(content="短文本", font_size=16, max_width=400)
        long = TextBlock(
            content="这是一段非常长的文本，用于测试自动换行和高度计算功能，应该会占用多行",
            font_size=16, max_width=200,
        )
        assert long.height > short.height

    def test_render_output(self):
        text = TextBlock(content="Test", font_size=24, max_width=400, x=100, y=200)
        out = text.render()
        assert out["type"] == "text"
        assert out["content"] == "Test"
        assert out["x"] == 100
        assert out["y"] == 200
        assert out["width"] == 400
        assert "fontSize" in out

    def test_update_content_triggers_recompute(self):
        text = TextBlock(content="Short", font_size=16, max_width=400)
        h0 = text.height
        text.update_content("这是一段更长的文本，应该会导致高度增加")
        assert text.height >= h0


class TestImageBlock:
    def test_render_output(self):
        img = ImageBlock(src="data:image/png;base64,...", width=400, height=300, x=100, y=200)
        out = img.render()
        assert out["type"] == "image"
        assert out["src"] == "data:image/png;base64,..."
        assert out["width"] == 400

    def test_resize_preserves_aspect_ratio(self):
        img = ImageBlock(src="image.jpg", width=400, height=300, maintain_aspect_ratio=True)
        img.resize(200)
        assert img.width == 200
        assert img.height == 150


class TestShapeBlock:
    def test_render_output(self):
        shape = ShapeBlock(
            width=200, height=4, subtype="divider",
            background_color="#FF0000",
        )
        out = shape.render()
        assert out["type"] == "rect"
        assert out["subtype"] == "divider"
        assert out["backgroundColor"] == "#FF0000"
        assert out["width"] == 200
        assert out["height"] == 4

    def test_default_values(self):
        shape = ShapeBlock(width=100, height=80)
        out = shape.render()
        assert out["subtype"] == "rect"
        assert out["backgroundColor"] == "transparent"
        assert out["borderRadius"] == 0
        assert out["gradient"] == ""

    def test_with_gradient(self):
        shape = ShapeBlock(
            width=1080, height=960,
            subtype="overlay",
            gradient="linear-gradient(180deg, #000000cc, #00000000)",
        )
        out = shape.render()
        assert "linear-gradient" in out["gradient"]


class TestVerticalContainer:
    def test_arrange_vertical_layout(self):
        ctr = VerticalContainer(x=0, y=0, width=400, padding=20, gap=10)
        t1 = TextBlock(content="Title", font_size=24, max_width=360)
        t2 = TextBlock(content="Subtitle", font_size=16, max_width=360)
        img = ImageBlock(src="image.jpg", width=360, height=200)

        ctr.add(t1).add(t2).add(img)
        ctr.arrange()

        assert t1.y == 20
        assert t2.y > t1.y + t1.height
        assert img.y > t2.y + t2.height

    def test_height_auto_calculated(self):
        ctr = VerticalContainer(width=400, padding=20, gap=10)
        t = TextBlock(content="Title", font_size=24, max_width=360)
        img = ImageBlock(src="image.jpg", width=360, height=200)
        ctr.add(t).add(img)
        ctr.arrange()
        expected_min = 20 + t.height + 10 + 200 + 20
        assert ctr.height >= expected_min

    def test_get_all_elements_flat(self):
        ctr = VerticalContainer(width=400)
        ctr.add(TextBlock(content="Test", font_size=16, max_width=360))
        ctr.add(ImageBlock(src="image.jpg", width=360, height=200))
        ctr.arrange()
        elems = ctr.get_all_elements()
        assert len(elems) == 2
        assert elems[0]["type"] == "text"
        assert elems[1]["type"] == "image"

    def test_shape_in_vertical_flow(self):
        """ShapeBlock 参与垂直流式布局"""
        ctr = VerticalContainer(width=400, padding=20, gap=10)
        t = TextBlock(content="Title", font_size=24, max_width=360)
        div = ShapeBlock(width=200, height=3, subtype="divider")
        t2 = TextBlock(content="Body", font_size=16, max_width=360)
        ctr.add(t).add(div).add(t2)
        ctr.arrange()

        assert div.y > t.y + t.height
        assert t2.y > div.y + div.height
        elems = ctr.get_all_elements()
        assert len(elems) == 3
        types = [e["type"] for e in elems]
        assert types == ["text", "rect", "text"]


class TestHorizontalContainer:
    def test_arrange_horizontal_layout(self):
        ctr = HorizontalContainer(x=0, y=0, width=600, padding=20, gap=10)
        i1 = ImageBlock(src="i1.png", width=80, height=80)
        i2 = ImageBlock(src="i2.png", width=80, height=80)
        ctr.add(i1).add(i2)
        ctr.arrange()
        assert i1.x == 20
        assert i2.x > i1.x + i1.width


class TestNestedContainers:
    def test_nested_and_flatten(self):
        main = VerticalContainer(width=600, padding=30, gap=20)
        header = VerticalContainer(width=540, padding=10, gap=5)
        header.add(TextBlock(content="Title", font_size=36, max_width=520))
        header.add(TextBlock(content="Sub", font_size=18, max_width=520))
        header.arrange()
        main.add(header)
        main.add(ImageBlock(src="main.jpg", width=540, height=400))
        main.arrange()

        elems = main.get_all_elements()
        assert len(elems) == 3


# ============================================================================
# 二、LayoutBuilder 集成测试
# ============================================================================

@needs_builder
class TestClassifyInstructions:
    def test_basic_classification(self):
        instrs = [
            {"command": "add_image", "src": "bg.jpg", "layer_type": "background"},
            {"command": "add_image", "src": "fg.png", "layer_type": "subject"},
            {"command": "add_overlay"},
            {"command": "add_title", "content": "Hello", "font_size": 64, "color": "#FFF"},
            {"command": "add_subtitle", "content": "World", "font_size": 28, "color": "#CCC"},
            {"command": "add_divider"},
            {"command": "add_cta", "content": "Click", "font_size": 24, "color": "#00F"},
        ]
        bg, subj, overlay, content, cta = _classify_instructions(instrs)
        assert len(bg) == 1
        assert len(subj) == 1
        assert len(overlay) == 1
        assert len(content) == 3  # title + subtitle + divider
        assert len(cta) == 1


@needs_builder
class TestLayoutBuilder:
    @pytest.fixture
    def builder(self):
        return LayoutBuilder()

    @pytest.fixture
    def basic_instructions(self):
        return [
            {"command": "add_image", "src": "bg.jpg", "layer_type": "background"},
            {"command": "add_overlay"},
            {"command": "add_title", "content": "海报标题", "font_size": 64, "color": "#FFFFFF"},
            {"command": "add_subtitle", "content": "副标题文字", "font_size": 28, "color": "#EEEEEE"},
            {"command": "add_cta", "content": "了解更多", "font_size": 24, "color": "#0066FF"},
        ]

    def test_all_strategies_produce_output(self, builder, basic_instructions):
        """每种策略都应该能正常产出元素列表"""
        for strategy_name in VALID_STRATEGIES:
            elements = builder.build(
                dsl_instructions=basic_instructions,
                layout_strategy=strategy_name,
                canvas_width=1080, canvas_height=1920,
            )
            assert len(elements) >= 3, f"strategy={strategy_name} 产出不足"
            types = [e["type"] for e in elements]
            assert "image" in types, f"strategy={strategy_name} 缺少背景图"
            assert "text" in types, f"strategy={strategy_name} 缺少文字"

    def test_background_always_fullscreen(self, builder, basic_instructions):
        elements = builder.build(
            dsl_instructions=basic_instructions,
            layout_strategy="centered",
            canvas_width=1080, canvas_height=1920,
        )
        bg = [e for e in elements if e.get("layer_type") == "background"]
        assert len(bg) == 1
        assert bg[0]["x"] == 0
        assert bg[0]["y"] == 0
        assert bg[0]["width"] == 1080
        assert bg[0]["height"] == 1920

    def test_overlay_between_bg_and_text(self, builder, basic_instructions):
        elements = builder.build(
            dsl_instructions=basic_instructions,
            layout_strategy="bottom_heavy",
            canvas_width=1080, canvas_height=1920,
        )
        types = [e.get("type") for e in elements]
        subtypes = [e.get("subtype") for e in elements]

        bg_idx = next(i for i, e in enumerate(elements) if e.get("layer_type") == "background")
        overlay_idx = next(i for i, s in enumerate(subtypes) if s == "overlay")
        text_idx = next(i for i, t in enumerate(types) if t == "text")

        assert bg_idx < overlay_idx < text_idx

    def test_no_element_outside_canvas(self, builder, basic_instructions):
        for strategy_name in VALID_STRATEGIES:
            elements = builder.build(
                dsl_instructions=basic_instructions,
                layout_strategy=strategy_name,
                canvas_width=1080, canvas_height=1920,
            )
            for elem in elements:
                if elem.get("layer_type") == "background":
                    continue
                if elem.get("subtype") == "overlay":
                    continue
                assert elem["x"] >= 0, f"x < 0: {elem}"
                assert elem["y"] >= 0, f"y < 0: {elem}"
                assert elem["x"] + elem["width"] <= 1080 + 40, f"超出右边界: {elem}"

    def test_centered_strategy_positions(self, builder, basic_instructions):
        elements = builder.build(
            dsl_instructions=basic_instructions,
            layout_strategy="centered",
            canvas_width=1080, canvas_height=1920,
        )
        text_elems = [e for e in elements if e["type"] == "text"]
        ys = [e["y"] for e in text_elems]

        for y in ys:
            assert 300 < y < 1600, f"centered 策略文字 y={y} 不在居中区域"

    def test_bottom_heavy_strategy_positions(self, builder, basic_instructions):
        elements = builder.build(
            dsl_instructions=basic_instructions,
            layout_strategy="bottom_heavy",
            canvas_width=1080, canvas_height=1920,
        )
        text_elems = [e for e in elements if e["type"] == "text"]
        ys = [e["y"] for e in text_elems]

        for y in ys:
            assert y > 800, f"bottom_heavy 策略文字 y={y} 不在底部区域"

    def test_top_text_strategy_positions(self, builder, basic_instructions):
        elements = builder.build(
            dsl_instructions=basic_instructions,
            layout_strategy="top_text",
            canvas_width=1080, canvas_height=1920,
        )
        text_elems = [e for e in elements if e["type"] == "text"]
        ys = [e["y"] for e in text_elems]

        for y in ys:
            assert y < 1200, f"top_text 策略文字 y={y} 不在顶部区域"

    def test_diagonal_cta_separation(self, builder):
        """对角线模式：CTA 应该在单独区域（下方）"""
        instrs = [
            {"command": "add_image", "src": "bg.jpg", "layer_type": "background"},
            {"command": "add_title", "content": "Title", "font_size": 64, "color": "#FFF"},
            {"command": "add_cta", "content": "Action", "font_size": 28, "color": "#FFF"},
        ]
        elements = builder.build(
            dsl_instructions=instrs,
            layout_strategy="diagonal",
            canvas_width=1080, canvas_height=1920,
        )
        text_elems = [e for e in elements if e["type"] == "text"]
        assert len(text_elems) >= 2

        title_y = text_elems[0]["y"]
        cta_y = text_elems[-1]["y"]
        assert cta_y > title_y + 400, "CTA 应远离标题（对角线分离）"

    def test_divider_in_flow(self, builder):
        instrs = [
            {"command": "add_title", "content": "Title", "font_size": 48, "color": "#FFF"},
            {"command": "add_divider"},
            {"command": "add_text", "content": "Body text", "font_size": 20, "color": "#DDD"},
        ]
        elements = builder.build(
            dsl_instructions=instrs,
            layout_strategy="centered",
            canvas_width=1080, canvas_height=1920,
        )
        types = [e["type"] for e in elements]
        assert types == ["text", "rect", "text"]

        ys = [e["y"] for e in elements]
        assert ys[0] < ys[1] < ys[2], "元素应按 DSL 顺序从上到下排列"

    def test_invalid_strategy_fallback(self, builder, basic_instructions):
        """无效策略名应回退到默认"""
        elements = builder.build(
            dsl_instructions=basic_instructions,
            layout_strategy="nonexistent_strategy",
            canvas_width=1080, canvas_height=1920,
        )
        assert len(elements) >= 3

    def test_empty_instructions(self, builder):
        elements = builder.build(
            dsl_instructions=[],
            layout_strategy="centered",
            canvas_width=1080, canvas_height=1920,
        )
        assert elements == []

    def test_text_height_auto_adapted(self, builder):
        """长文本应自动获得更大高度（OOP TextBlock 自动计算行数）"""
        short_instrs = [
            {"command": "add_text", "content": "短文本", "font_size": 24, "color": "#FFF"},
        ]
        long_instrs = [
            {"command": "add_text", "content": "这是一段非常非常长的正文文本内容，它应该会导致 TextBlock 自动计算出更多的行数，从而获得比短文本更大的高度值", "font_size": 24, "color": "#FFF"},
        ]
        short_elems = builder.build(short_instrs, "left_aligned", 1080, 1920)
        long_elems = builder.build(long_instrs, "left_aligned", 1080, 1920)

        short_h = short_elems[0]["height"]
        long_h = long_elems[0]["height"]
        assert long_h > short_h, f"长文本高度 {long_h} 应大于短文本高度 {short_h}"

    def test_schema_converter_compatibility(self, builder, basic_instructions):
        """输出格式应与 SchemaConverter 兼容"""
        elements = builder.build(
            dsl_instructions=basic_instructions,
            layout_strategy="centered",
            canvas_width=1080, canvas_height=1920,
        )
        for elem in elements:
            assert "type" in elem
            assert "x" in elem
            assert "y" in elem
            assert "width" in elem
            assert "height" in elem

            if elem["type"] == "text":
                assert "content" in elem
                assert "fontSize" in elem
                assert "fontFamily" in elem
                assert "color" in elem
            elif elem["type"] == "image":
                assert "src" in elem
            elif elem["type"] == "rect":
                assert "subtype" in elem
                assert "backgroundColor" in elem
