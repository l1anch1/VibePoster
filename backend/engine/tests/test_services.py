"""
Service 层测试
测试业务逻辑层
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any

from app.services import PosterService


class TestPosterService:
    """海报服务测试类"""
    
    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return PosterService()
    
    def test_process_user_images_with_both(self, service):
        """测试处理两张图片"""
        image_person = b"person_image_data"
        image_bg = b"bg_image_data"
        
        result = service.process_user_images(
            image_person=image_person,
            image_bg=image_bg
        )
        
        assert result is not None
        assert len(result) == 2
        assert result[0]["type"] == "background"
        assert result[1]["type"] == "person"
    
    def test_process_user_images_with_person_only(self, service):
        """测试只处理人物图片"""
        image_person = b"person_image_data"
        
        result = service.process_user_images(
            image_person=image_person,
            image_bg=None
        )
        
        assert result is not None
        assert len(result) == 1
        assert result[0]["type"] == "person"
    
    def test_process_user_images_with_bg_only(self, service):
        """测试只处理背景图片"""
        image_bg = b"bg_image_data"
        
        result = service.process_user_images(
            image_person=None,
            image_bg=image_bg
        )
        
        assert result is not None
        assert len(result) == 1
        assert result[0]["type"] == "background"
    
    def test_process_user_images_with_none(self, service):
        """测试不处理任何图片"""
        result = service.process_user_images(
            image_person=None,
            image_bg=None
        )
        
        assert result is None
    
    def test_build_initial_state(self, service):
        """测试构建初始状态"""
        state = service.build_initial_state(
            prompt="测试提示词",
            canvas_width=1080,
            canvas_height=1920,
            user_images=None,
            chat_history=None
        )
        
        assert state["user_prompt"] == "测试提示词"
        assert state["canvas_width"] == 1080
        assert state["canvas_height"] == 1920
        assert state["user_images"] is None
        assert state["chat_history"] is None
        assert state["design_brief"] == {}
        assert state["_retry_count"] == 0
    
        assert "canvas" in result
        assert "layers" in result
        mock_workflow.invoke.assert_called_once()
        mock_search_assets.assert_called_once()

