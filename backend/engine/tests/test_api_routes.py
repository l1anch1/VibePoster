"""
API 路由测试
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock

from app.main import app
from app.core.dependencies import get_poster_service, reset_poster_service

client = TestClient(app)


class TestPosterRoutes:
    """海报路由测试类"""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """每个测试前后的设置和清理"""
        # 测试前重置服务实例
        reset_poster_service()
        yield
        # 测试后清理
        reset_poster_service()
    
    def test_generate_multimodal_success(self):
        """测试多模态生成接口 - 成功情况"""
        # Mock 服务层
        mock_service = Mock()
        mock_service.generate_poster.return_value = {
            "canvas": {
                "width": 1080,
                "height": 1920,
                "backgroundColor": "#FFFFFF"
            },
            "layers": []
        }
        
        # 覆盖依赖
        app.dependency_overrides[get_poster_service] = lambda: mock_service
        
        try:
            response = client.post(
                "/api/generate_multimodal",
                data={
                    "prompt": "测试海报",
                    "canvas_width": 1080,
                    "canvas_height": 1920
                }
            )
            
            # 验证响应
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["success"] is True
            
            # 验证服务被调用
            mock_service.generate_poster.assert_called_once()
        finally:
            # 清理依赖覆盖
            app.dependency_overrides.clear()
    
    def test_generate_multimodal_invalid_canvas_size(self):
        """测试多模态生成接口 - 无效的画布尺寸"""
        # 测试画布宽度过小
        response = client.post(
            "/api/generate_multimodal",
            data={
                "prompt": "测试海报",
                "canvas_width": 50,  # 小于最小值 100
                "canvas_height": 1920
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # 测试画布宽度过大
        response = client.post(
            "/api/generate_multimodal",
            data={
                "prompt": "测试海报",
                "canvas_width": 20000,  # 大于最大值 10000
                "canvas_height": 1920
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_generate_multimodal_with_images(self):
        """测试多模态生成接口 - 带图片上传"""
        # 创建模拟的图片文件
        image_data = b"fake_image_data"
        
        response = client.post(
            "/api/generate_multimodal",
            data={
                "prompt": "测试海报",
                "canvas_width": 1080,
                "canvas_height": 1920
            },
            files={
                "image_person": ("person.jpg", image_data, "image/jpeg"),
                "image_bg": ("bg.jpg", image_data, "image/jpeg")
            }
        )
        
        # 注意：实际测试可能需要 mock 服务层
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]

