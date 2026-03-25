"""
API Schema 测试
测试请求/响应模型验证
"""
import pytest
from pydantic import ValidationError

from app.models.response import ErrorResponse
from app.models.poster import PosterData, Canvas
from app.api.routes.steps import PlanRequest


class TestPlanRequest:
    """分步生成 Plan 请求模型测试"""

    def test_valid_request(self):
        req = PlanRequest(
            prompt="测试海报",
            canvas_width=1080,
            canvas_height=1920,
        )
        assert req.prompt == "测试海报"
        assert req.canvas_width == 1080
        assert req.canvas_height == 1920
        assert req.brand_name is None

    def test_with_brand_name(self):
        req = PlanRequest(
            prompt="星巴克促销海报",
            canvas_width=1080,
            canvas_height=1920,
            brand_name="Starbucks",
        )
        assert req.brand_name == "Starbucks"

    def test_empty_prompt(self):
        with pytest.raises(ValidationError):
            PlanRequest(prompt="", canvas_width=1080, canvas_height=1920)

    def test_prompt_too_long(self):
        with pytest.raises(ValidationError):
            PlanRequest(prompt="a" * 2001, canvas_width=1080, canvas_height=1920)

    def test_canvas_width_too_small(self):
        with pytest.raises(ValidationError):
            PlanRequest(prompt="测试", canvas_width=50, canvas_height=1920)

    def test_canvas_width_too_large(self):
        with pytest.raises(ValidationError):
            PlanRequest(prompt="测试", canvas_width=20000, canvas_height=1920)


class TestErrorResponse:
    """错误响应模型测试"""

    def test_valid_error_response(self):
        response = ErrorResponse(
            error="请求参数错误",
            detail={"field": "prompt", "message": "不能为空"},
        )
        assert response.success is False
        assert response.error == "请求参数错误"
        assert response.detail is not None

    def test_default_values(self):
        response = ErrorResponse(error="错误信息")
        assert response.success is False
        assert response.detail is None
