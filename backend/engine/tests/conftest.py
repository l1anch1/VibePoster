"""
Pytest 配置文件
提供测试用的 fixtures 和配置

注意：某些 fixtures 需要完整依赖（如 FastAPI），
核心模块测试（KG、RAG、Layout Engine）可以独立运行。
"""
import pytest
from unittest.mock import Mock, MagicMock
from typing import Generator

# 尝试导入 FastAPI 相关依赖（可能不可用）
try:
    from fastapi.testclient import TestClient
    from app.main import app
    from app.services import PosterService
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    TestClient = None
    app = None
    PosterService = None


@pytest.fixture
def client() -> Generator:
    """
    创建 FastAPI 测试客户端
    
    Yields:
        TestClient: FastAPI 测试客户端
    """
    if not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not available")
    
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_poster_service() -> Mock:
    """
    创建模拟的海报服务实例
    
    Returns:
        Mock: 模拟的 PosterService 实例
    """
    if not FASTAPI_AVAILABLE:
        pytest.skip("PosterService not available")
    
    service = Mock(spec=PosterService)
    service.generate_poster = MagicMock(return_value={
        "canvas": {
            "width": 1080,
            "height": 1920,
            "backgroundColor": "#FFFFFF"
        },
        "layers": []
    })
    return service


@pytest.fixture
def sample_poster_data() -> dict:
    """
    示例海报数据
    
    Returns:
        dict: 示例海报数据字典
    """
    return {
        "canvas": {
            "width": 1080,
            "height": 1920,
            "backgroundColor": "#FFFFFF"
        },
        "layers": [
            {
                "id": "bg",
                "type": "image",
                "src": "data:image/jpeg;base64,...",
                "x": 0,
                "y": 0,
                "width": 1080,
                "height": 1920,
                "z_index": 0
            },
            {
                "id": "title",
                "type": "text",
                "content": "测试标题",
                "x": 100,
                "y": 100,
                "width": 500,
                "height": 100,
                "fontSize": 48,
                "color": "#000000",
                "fontFamily": "Yuanti TC",
                "textAlign": "left",
                "fontWeight": "normal",
                "z_index": 2
            }
        ]
    }

