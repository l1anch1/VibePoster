"""
Core Schema 测试
测试核心数据模型
"""
import pytest
from pydantic import ValidationError

from app.core.schemas import (
    Canvas,
    TextLayer,
    ImageLayer,
    ShapeLayer,
    PosterData,
)


class TestCanvas:
    """画布模型测试"""
    
    def test_valid_canvas(self):
        """测试有效画布"""
        canvas = Canvas(
            width=1080,
            height=1920,
            backgroundColor="#FFFFFF"
        )
        
        assert canvas.width == 1080
        assert canvas.height == 1920
        assert canvas.backgroundColor == "#FFFFFF"
    
    def test_default_values(self):
        """测试默认值"""
        canvas = Canvas()
        
        assert canvas.width == 1080
        assert canvas.height == 1920
        assert canvas.backgroundColor == "#FFFFFF"


class TestTextLayer:
    """文本图层模型测试"""
    
    def test_valid_text_layer(self):
        """测试有效文本图层"""
        layer = TextLayer(
            id="title",
            type="text",
            content="测试标题",
            x=100,
            y=100,
            width=500,
            height=100,
            fontSize=48,
            color="#000000"
        )
        
        assert layer.id == "title"
        assert layer.type == "text"
        assert layer.content == "测试标题"
        assert layer.fontSize == 48
    
    def test_default_values(self):
        """测试默认值"""
        layer = TextLayer(
            id="title",
            type="text",
            content="测试"
        )
        
        assert layer.x == 0
        assert layer.y == 0
        assert layer.width == 0
        assert layer.height == 0
        assert layer.fontSize == 24
        assert layer.color == "#000000"
        assert layer.fontFamily == "Yuanti TC"


class TestImageLayer:
    """图片图层模型测试"""
    
    def test_valid_image_layer(self):
        """测试有效图片图层"""
        layer = ImageLayer(
            id="bg",
            type="image",
            src="data:image/jpeg;base64,...",
            x=0,
            y=0,
            width=1080,
            height=1920
        )
        
        assert layer.id == "bg"
        assert layer.type == "image"
        assert layer.src == "data:image/jpeg;base64,..."
    
    def test_default_values(self):
        """测试默认值"""
        layer = ImageLayer(
            id="bg",
            type="image"
        )
        
        assert layer.src == ""
        assert layer.x == 0
        assert layer.y == 0


class TestPosterData:
    """海报数据模型测试"""
    
    def test_valid_poster_data(self):
        """测试有效海报数据"""
        canvas = Canvas(width=1080, height=1920)
        text_layer = TextLayer(
            id="title",
            type="text",
            content="测试"
        )
        
        poster = PosterData(
            canvas=canvas,
            layers=[text_layer]
        )
        
        assert poster.canvas == canvas
        assert len(poster.layers) == 1
        assert poster.layers[0] == text_layer
    
    def test_mixed_layers(self):
        """测试混合图层类型"""
        canvas = Canvas(width=1080, height=1920)
        text_layer = TextLayer(
            id="title",
            type="text",
            content="测试"
        )
        image_layer = ImageLayer(
            id="bg",
            type="image",
            src="data:image/jpeg;base64,..."
        )
        
        poster = PosterData(
            canvas=canvas,
            layers=[text_layer, image_layer]
        )
        
        assert len(poster.layers) == 2

