"""
step_assets 路由集成测试

Mock 外部服务（LLM API、Pexels/Flux），保留内部逻辑。
覆盖三种模式：Text Only / Style Reference / With Material。
"""

import io
import json
import pytest
from unittest.mock import patch, MagicMock

try:
    from fastapi.testclient import TestClient
    from app.main import app

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

pytestmark = pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_design_brief():
    return {
        "title": "Test Poster",
        "subtitle": "Subtitle",
        "main_color": "#FF0000",
        "background_color": "#FFFFFF",
        "style_keywords": ["tech", "modern"],
        "intent": "promotion",
        "user_prompt": "Make a tech poster",
    }


@pytest.fixture
def sample_png_bytes():
    """生成最小有效 PNG 图片"""
    try:
        from PIL import Image

        img = Image.new("RGB", (100, 100), color="red")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except ImportError:
        pytest.skip("Pillow not available")


# ============================================================================
# Test: Text Only 模式
# ============================================================================


class TestStepAssetsTextOnly:
    """Text Only: 无图片上传，直接搜索背景"""

    @patch("app.services.asset_service.search_assets_multiple")
    def test_returns_candidates(self, mock_search, client, sample_design_brief):
        mock_search.return_value = [
            "https://example.com/bg1.jpg",
            "https://example.com/bg2.jpg",
        ]

        resp = client.post(
            "/api/step/assets",
            data={
                "design_brief_json": json.dumps(sample_design_brief),
                "canvas_width": "1080",
                "canvas_height": "1920",
                "count": "2",
            },
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["step"] == "assets"
        assert len(body["candidates"]) == 2
        assert body["keywords_used"] == ["tech", "modern"]
        mock_search.assert_called_once()


# ============================================================================
# Test: Style Reference 模式
# ============================================================================


class TestStepAssetsStyleReference:
    """Style Reference: 上传背景参考图，分析后搜索匹配背景"""

    @patch("app.services.asset_service.search_assets_multiple")
    @patch("app.services.asset_service.understand_image")
    def test_enriches_design_brief(
        self, mock_understand, mock_search, client, sample_design_brief, sample_png_bytes
    ):
        mock_understand.return_value = {
            "understanding": {
                "style": "futuristic",
                "color_palette": ["#0000FF", "#00FF00"],
                "mood": "Professional",
                "theme": "Tech",
                "description": "A futuristic tech scene",
                "layout_hints": {"text_position": "center"},
            },
            "suggestions": {
                "color_scheme": {"primary": "#0000FF"},
            },
        }
        mock_search.return_value = ["https://example.com/matched.jpg"]

        resp = client.post(
            "/api/step/assets",
            data={
                "design_brief_json": json.dumps(sample_design_brief),
                "canvas_width": "1080",
                "canvas_height": "1920",
                "count": "1",
            },
            files={"image_bg": ("bg.png", sample_png_bytes, "image/png")},
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["step"] == "assets"

        # 参考图分析应注入 design_brief
        brief = body.get("design_brief", {})
        assert brief.get("reference_mood") == "Professional"
        assert brief.get("reference_theme") == "Tech"
        assert "futuristic" in brief.get("style_keywords", [])

        # 应有背景分析条目
        analyses = body.get("image_analyses", [])
        assert any(a.get("type") == "background" for a in analyses)


# ============================================================================
# Test: With Material 模式
# ============================================================================


class TestStepAssetsWithMaterial:
    """With Material: 上传主体素材"""

    @patch("app.services.asset_service.search_assets_multiple")
    @patch("app.services.asset_service.understand_image")
    def test_returns_subject_info(
        self, mock_understand, mock_search, client, sample_design_brief, sample_png_bytes
    ):
        mock_understand.return_value = {
            "understanding": {
                "description": "A red product",
                "main_color": "#FF0000",
                "color_palette": ["#FF0000"],
                "layout_hints": {"text_color_suggestion": "#FFFFFF"},
            },
            "suggestions": {},
        }
        mock_search.return_value = ["https://example.com/bg1.jpg"]

        resp = client.post(
            "/api/step/assets",
            data={
                "design_brief_json": json.dumps(sample_design_brief),
                "canvas_width": "1080",
                "canvas_height": "1920",
                "count": "1",
            },
            files={"image_subject": ("subject.png", sample_png_bytes, "image/png")},
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["step"] == "assets"
        assert body.get("subject_url") is not None
        assert body.get("subject_width") == 100
        assert body.get("subject_height") == 100
        assert body.get("color_suggestions") is not None

    @patch("app.services.asset_service.understand_image")
    def test_with_user_bg_skips_search(
        self, mock_understand, client, sample_design_brief, sample_png_bytes
    ):
        """上传主体 + 背景：不搜索，直接使用用户背景"""
        mock_understand.return_value = {
            "understanding": {
                "description": "A red product",
                "main_color": "#FF0000",
                "color_palette": [],
                "layout_hints": {},
            },
            "suggestions": {},
        }

        resp = client.post(
            "/api/step/assets",
            data={
                "design_brief_json": json.dumps(sample_design_brief),
                "canvas_width": "1080",
                "canvas_height": "1920",
                "count": "1",
            },
            files={
                "image_subject": ("subject.png", sample_png_bytes, "image/png"),
                "image_bg": ("bg.png", sample_png_bytes, "image/png"),
            },
        )

        assert resp.status_code == 200
        body = resp.json()
        # 候选列表应只有一个（用户上传的背景 base64）
        assert len(body["candidates"]) == 1
        assert body["candidates"][0].startswith("data:image")
