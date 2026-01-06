"""
API Schema 测试
测试请求/响应模型验证
"""
import pytest
from pydantic import ValidationError

from app.api.schemas import (
    PosterGenerateRequest,
    PosterGenerateSimpleRequest,
    PosterGenerateResponse,
    ErrorResponse,
)
from app.core.schemas import PosterData, Canvas


class TestPosterGenerateRequest:
    """海报生成请求模型测试"""
    
    def test_valid_request(self):
        """测试有效请求"""
        request = PosterGenerateRequest(
            prompt="测试海报",
            canvas_width=1080,
            canvas_height=1920
        )
        
        assert request.prompt == "测试海报"
        assert request.canvas_width == 1080
        assert request.canvas_height == 1920
    
    def test_prompt_trimming(self):
        """测试提示词自动去除首尾空格"""
        request = PosterGenerateRequest(
            prompt="  测试海报  ",
            canvas_width=1080,
            canvas_height=1920
        )
        
        assert request.prompt == "测试海报"
    
    def test_empty_prompt(self):
        """测试空提示词"""
        with pytest.raises(ValidationError):
            PosterGenerateRequest(
                prompt="",
                canvas_width=1080,
                canvas_height=1920
            )
    
    def test_prompt_too_long(self):
        """测试提示词过长"""
        long_prompt = "a" * 1001  # 超过 1000 字符限制
        
        with pytest.raises(ValidationError):
            PosterGenerateRequest(
                prompt=long_prompt,
                canvas_width=1080,
                canvas_height=1920
            )
    
    def test_canvas_width_too_small(self):
        """测试画布宽度过小"""
        with pytest.raises(ValidationError):
            PosterGenerateRequest(
                prompt="测试",
                canvas_width=50,  # 小于最小值 100
                canvas_height=1920
            )
    
    def test_canvas_width_too_large(self):
        """测试画布宽度过大"""
        with pytest.raises(ValidationError):
            PosterGenerateRequest(
                prompt="测试",
                canvas_width=20000,  # 大于最大值 10000
                canvas_height=1920
            )


class TestPosterGenerateSimpleRequest:
    """简化海报生成请求模型测试"""
    
    def test_valid_request(self):
        """测试有效请求"""
        request = PosterGenerateSimpleRequest(prompt="测试海报")
        
        assert request.prompt == "测试海报"
    
    def test_empty_prompt(self):
        """测试空提示词"""
        with pytest.raises(ValidationError):
            PosterGenerateSimpleRequest(prompt="")


class TestPosterGenerateResponse:
    """海报生成响应模型测试"""
    
    def test_valid_response(self):
        """测试有效响应"""
        canvas = Canvas(width=1080, height=1920, backgroundColor="#FFFFFF")
        poster_data = PosterData(canvas=canvas, layers=[])
        
        response = PosterGenerateResponse(
            success=True,
            data=poster_data,
            message="海报生成成功"
        )
        
        assert response.success is True
        assert response.data == poster_data
        assert response.message == "海报生成成功"
    
    def test_default_values(self):
        """测试默认值"""
        canvas = Canvas(width=1080, height=1920)
        poster_data = PosterData(canvas=canvas, layers=[])
        
        response = PosterGenerateResponse(data=poster_data)
        
        assert response.success is True
        assert response.message == "海报生成成功"


class TestErrorResponse:
    """错误响应模型测试"""
    
    def test_valid_error_response(self):
        """测试有效错误响应"""
        response = ErrorResponse(
            error="请求参数错误",
            detail={"field": "prompt", "message": "不能为空"}
        )
        
        assert response.success is False
        assert response.error == "请求参数错误"
        assert response.detail is not None
    
    def test_default_values(self):
        """测试默认值"""
        response = ErrorResponse(error="错误信息")
        
        assert response.success is False
        assert response.detail is None

