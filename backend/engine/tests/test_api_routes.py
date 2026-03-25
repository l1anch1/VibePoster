"""
API 路由测试 — 分步生成 (Step Wizard)
"""
import json
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.main import app

client = TestClient(app)


class TestStepPlanRoute:
    """Step 1: /api/step/plan 路由测试"""

    @patch("app.api.routes.steps.run_planner_agent")
    def test_plan_success(self, mock_planner):
        mock_planner.return_value = {
            "title": "测试海报",
            "subtitle": "副标题",
            "main_color": "#6C5CE7",
            "background_color": "#FFFFFF",
            "style_keywords": ["modern", "minimal"],
        }

        response = client.post(
            "/api/step/plan",
            json={
                "prompt": "科技公司宣传海报",
                "canvas_width": 1080,
                "canvas_height": 1920,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["step"] == "plan"
        assert "design_brief" in data
        assert data["design_brief"]["title"] == "测试海报"
        mock_planner.assert_called_once()

    def test_plan_empty_prompt(self):
        response = client.post(
            "/api/step/plan",
            json={"prompt": "", "canvas_width": 1080, "canvas_height": 1920},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestStepAssetsRoute:
    """Step 2: /api/step/assets 路由测试"""

    @patch("app.api.routes.steps.search_assets_multiple")
    def test_assets_text_only(self, mock_search):
        mock_search.return_value = [
            "https://example.com/bg1.jpg",
            "https://example.com/bg2.jpg",
        ]

        brief = {"title": "Test", "style_keywords": ["modern"]}
        response = client.post(
            "/api/step/assets",
            data={
                "design_brief_json": json.dumps(brief),
                "canvas_width": "1080",
                "canvas_height": "1920",
                "count": "2",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["step"] == "assets"
        assert len(data["candidates"]) == 2
        mock_search.assert_called_once()


class TestStepLayoutsRoute:
    """Step 3: /api/step/layouts 路由测试"""

    @patch("app.api.routes.steps.run_layout_agent")
    def test_layouts_success(self, mock_layout):
        mock_layout.return_value = {
            "canvas": {"width": 1080, "height": 1920, "backgroundColor": "#FFFFFF"},
            "layers": [],
        }

        response = client.post(
            "/api/step/layouts",
            json={
                "design_brief": {"title": "Test"},
                "selected_asset_url": "https://example.com/bg.jpg",
                "canvas_width": 1080,
                "canvas_height": 1920,
                "count": 2,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["step"] == "layouts"
        assert len(data["layouts"]) == 2
        assert mock_layout.call_count == 2


class TestStepFinalizeRoute:
    """Step 4: /api/step/finalize 路由测试"""

    @patch("app.api.routes.steps.run_critic_agent")
    def test_finalize_pass(self, mock_critic):
        mock_critic.return_value = {"status": "PASS", "feedback": ""}

        poster = {
            "canvas": {"width": 1080, "height": 1920, "backgroundColor": "#FFF"},
            "layers": [],
        }

        response = client.post(
            "/api/step/finalize",
            json={"poster_data": poster},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["step"] == "finalize"
        assert data["review"]["status"] == "PASS"


class TestHealthCheck:
    """健康检查测试"""

    def test_health(self):
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "ok"
