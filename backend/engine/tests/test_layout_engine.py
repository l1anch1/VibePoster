"""
OOP Layout Engine 测试
测试动态布局引擎
"""
import pytest
from app.core.layout import (
    Element,
    TextBlock,
    ImageBlock,
    Container,
    VerticalContainer,
    HorizontalContainer,
    Style,
)


class TestStyle:
    """样式配置测试"""
    
    def test_default_values(self):
        """测试默认值"""
        style = Style()
        
        assert style.font_size == 16
        assert style.font_family == "Arial"
        assert style.font_weight == "normal"
        assert style.color == "#000000"
        assert style.text_align == "left"
        assert style.opacity == 1.0
        assert style.rotation == 0.0
    
    def test_custom_values(self):
        """测试自定义值"""
        style = Style(
            font_size=24,
            font_family="Helvetica",
            font_weight="bold",
            color="#FF0000"
        )
        
        assert style.font_size == 24
        assert style.font_family == "Helvetica"
        assert style.font_weight == "bold"
        assert style.color == "#FF0000"


class TestTextBlock:
    """文本块测试"""
    
    def test_basic_creation(self):
        """测试基本创建"""
        text = TextBlock(
            content="Hello World",
            font_size=24,
            max_width=400
        )
        
        assert text.content == "Hello World"
        assert text.font_size == 24
        assert text.max_width == 400
        assert text.width == 400
    
    def test_auto_height_calculation(self):
        """测试自动高度计算"""
        # 短文本
        short_text = TextBlock(
            content="短文本",
            font_size=16,
            max_width=400
        )
        
        # 长文本
        long_text = TextBlock(
            content="这是一段非常长的文本，用于测试自动换行和高度计算功能，应该会占用多行",
            font_size=16,
            max_width=200
        )
        
        # 长文本的高度应该大于短文本
        assert long_text.height > short_text.height
    
    def test_render_output(self):
        """测试渲染输出"""
        text = TextBlock(
            content="Test",
            font_size=24,
            max_width=400,
            x=100,
            y=200
        )
        
        output = text.render()
        
        assert output["type"] == "text"
        assert output["content"] == "Test"
        assert output["x"] == 100
        assert output["y"] == 200
        assert output["width"] == 400
        assert "height" in output
        assert "fontSize" in output
    
    def test_update_content(self):
        """测试内容更新"""
        text = TextBlock(
            content="Short",
            font_size=16,
            max_width=400
        )
        
        initial_height = text.height
        
        text.update_content("这是一段更长的文本，应该会导致高度增加")
        
        # 高度应该增加
        assert text.height >= initial_height
        assert text.content == "这是一段更长的文本，应该会导致高度增加"


class TestImageBlock:
    """图片块测试"""
    
    def test_basic_creation(self):
        """测试基本创建"""
        image = ImageBlock(
            src="https://example.com/image.jpg",
            width=400,
            height=300
        )
        
        assert image.src == "https://example.com/image.jpg"
        assert image.width == 400
        assert image.height == 300
    
    def test_render_output(self):
        """测试渲染输出"""
        image = ImageBlock(
            src="data:image/png;base64,...",
            width=400,
            height=300,
            x=100,
            y=200
        )
        
        output = image.render()
        
        assert output["type"] == "image"
        assert output["src"] == "data:image/png;base64,..."
        assert output["x"] == 100
        assert output["y"] == 200
        assert output["width"] == 400
        assert output["height"] == 300
    
    def test_resize_with_aspect_ratio(self):
        """测试保持宽高比缩放"""
        image = ImageBlock(
            src="image.jpg",
            width=400,
            height=300,
            maintain_aspect_ratio=True
        )
        
        image.resize(200)  # 只提供新宽度
        
        assert image.width == 200
        assert image.height == 150  # 保持 4:3 比例


class TestVerticalContainer:
    """垂直容器测试"""
    
    def test_basic_creation(self):
        """测试基本创建"""
        container = VerticalContainer(
            x=0,
            y=0,
            width=400,
            padding=20,
            gap=10
        )
        
        assert container.width == 400
        assert container.padding == 20
        assert container.gap == 10
        assert len(container.elements) == 0
    
    def test_add_element(self):
        """测试添加元素"""
        container = VerticalContainer(width=400)
        text = TextBlock(content="Test", font_size=16, max_width=360)
        
        container.add(text)
        
        assert len(container.elements) == 1
        assert text._parent == container
    
    def test_chain_add(self):
        """测试链式添加"""
        container = VerticalContainer(width=400)
        text1 = TextBlock(content="Text1", font_size=16, max_width=360)
        text2 = TextBlock(content="Text2", font_size=16, max_width=360)
        
        container.add(text1).add(text2)
        
        assert len(container.elements) == 2
    
    def test_arrange_vertical_layout(self):
        """测试垂直排列"""
        container = VerticalContainer(
            x=0,
            y=0,
            width=400,
            padding=20,
            gap=10
        )
        
        text1 = TextBlock(content="Title", font_size=24, max_width=360)
        text2 = TextBlock(content="Subtitle", font_size=16, max_width=360)
        image = ImageBlock(src="image.jpg", width=360, height=200)
        
        container.add(text1).add(text2).add(image)
        container.arrange()
        
        # 验证垂直排列：每个元素的 y 应该递增
        assert text1.y == 20  # padding
        assert text2.y > text1.y + text1.height  # text1 下方
        assert image.y > text2.y + text2.height  # text2 下方
    
    def test_container_height_auto_calculate(self):
        """测试容器高度自动计算"""
        container = VerticalContainer(
            width=400,
            padding=20,
            gap=10
        )
        
        text1 = TextBlock(content="Title", font_size=24, max_width=360)
        image = ImageBlock(src="image.jpg", width=360, height=200)
        
        container.add(text1).add(image)
        container.arrange()
        
        # 容器高度应该等于 padding + text1.height + gap + image.height + padding
        expected_min_height = 20 + text1.height + 10 + 200 + 20
        assert container.height >= expected_min_height
    
    def test_get_all_elements(self):
        """测试获取所有元素"""
        container = VerticalContainer(width=400)
        text = TextBlock(content="Test", font_size=16, max_width=360)
        image = ImageBlock(src="image.jpg", width=360, height=200)
        
        container.add(text).add(image)
        container.arrange()
        
        elements = container.get_all_elements()
        
        assert len(elements) == 2
        assert elements[0]["type"] == "text"
        assert elements[1]["type"] == "image"


class TestHorizontalContainer:
    """水平容器测试"""
    
    def test_arrange_horizontal_layout(self):
        """测试水平排列"""
        container = HorizontalContainer(
            x=0,
            y=0,
            width=600,
            padding=20,
            gap=10
        )
        
        icon1 = ImageBlock(src="icon1.png", width=80, height=80)
        icon2 = ImageBlock(src="icon2.png", width=80, height=80)
        icon3 = ImageBlock(src="icon3.png", width=80, height=80)
        
        container.add(icon1).add(icon2).add(icon3)
        container.arrange()
        
        # 验证水平排列：每个元素的 x 应该递增
        assert icon1.x == 20  # padding
        assert icon2.x > icon1.x + icon1.width  # icon1 右侧
        assert icon3.x > icon2.x + icon2.width  # icon2 右侧


class TestNestedContainers:
    """嵌套容器测试"""
    
    def test_nested_vertical_containers(self):
        """测试嵌套垂直容器"""
        main_container = VerticalContainer(width=600, padding=30, gap=20)
        
        header = VerticalContainer(width=540, padding=10, gap=5)
        title = TextBlock(content="Title", font_size=36, max_width=520)
        subtitle = TextBlock(content="Subtitle", font_size=18, max_width=520)
        
        header.add(title).add(subtitle)
        header.arrange()
        
        image = ImageBlock(src="main.jpg", width=540, height=400)
        
        main_container.add(header).add(image)
        main_container.arrange()
        
        # 验证嵌套布局
        assert header.y == 30  # main padding
        assert image.y > header.y + header.height
    
    def test_get_all_elements_nested(self):
        """测试嵌套容器获取所有元素"""
        main_container = VerticalContainer(width=600)
        
        header = VerticalContainer(width=540)
        title = TextBlock(content="Title", font_size=36, max_width=520)
        subtitle = TextBlock(content="Subtitle", font_size=18, max_width=520)
        
        header.add(title).add(subtitle)
        header.arrange()
        
        image = ImageBlock(src="main.jpg", width=540, height=400)
        
        main_container.add(header).add(image)
        main_container.arrange()
        
        # 获取所有元素（扁平化）
        elements = main_container.get_all_elements()
        
        # 应该包含 title, subtitle, image
        assert len(elements) == 3

