"""
Service 层测试
测试业务逻辑层
"""
import pytest
from unittest.mock import Mock, patch

from app.services.poster_service import PosterService


class TestPosterService:
    """海报服务测试类"""

    @pytest.fixture
    def service(self):
        return PosterService()

    def test_process_user_images_with_subject_only(self, service):
        result = service.process_user_images(
            image_subject=b"subject_image_data",
            image_bg=None,
        )
        assert result is not None
        assert len(result) == 1
        assert result[0]["type"] == "subject"

    def test_process_user_images_with_bg_only(self, service):
        result = service.process_user_images(
            image_subject=None,
            image_bg=b"bg_image_data",
        )
        assert result is not None
        assert len(result) == 1
        assert result[0]["type"] == "background"

    def test_process_user_images_with_none(self, service):
        result = service.process_user_images(
            image_subject=None,
            image_bg=None,
        )
        assert result is None

    def test_build_initial_state(self, service):
        state = service.build_initial_state(
            prompt="测试提示词",
            canvas_width=1080,
            canvas_height=1920,
            user_images=None,
            chat_history=None,
        )
        assert state["user_prompt"] == "测试提示词"
        assert state["canvas_width"] == 1080
        assert state["canvas_height"] == 1920
        assert state["user_images"] is None
        assert state["design_brief"] == {}
        assert state["_retry_count"] == 0
