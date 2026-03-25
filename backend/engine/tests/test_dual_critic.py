"""
双路审核（Dual-Path Critic Review）测试

覆盖范围：
- Prompt 构造函数
- 渲染客户端 (render_client)
- 合并逻辑 (_merge_reviews)
- 级联流程 (run_critic_agent)
- 工作流节点 (critic_node / should_retry_layout)
"""
import json
import pytest
from unittest.mock import patch, MagicMock, Mock


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_poster():
    """最小可用海报数据"""
    return {
        "canvas": {"width": 1080, "height": 1920, "backgroundColor": "#FFFFFF"},
        "layers": [
            {
                "id": "bg",
                "type": "image",
                "src": "data:image/png;base64,abc",
                "x": 0, "y": 0,
                "width": 1080, "height": 1920,
            },
            {
                "id": "title",
                "type": "text",
                "content": "Hello",
                "x": 100, "y": 100,
                "width": 400, "height": 80,
                "fontSize": 48,
                "color": "#000000",
                "fontFamily": "Arial",
                "textAlign": "left",
                "fontWeight": "bold",
            },
        ],
    }


@pytest.fixture
def pass_review():
    return {"status": "PASS", "feedback": "没有问题", "issues": []}


@pytest.fixture
def reject_review():
    return {
        "status": "REJECT",
        "feedback": "文字超出画布",
        "issues": ["text overflow"],
    }


FAKE_PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100


# ============================================================================
# 1. Prompt 构造
# ============================================================================

class TestCriticPrompts:
    """critic prompt 模块测试"""

    def test_get_prompt_returns_system_and_user(self, sample_poster):
        from app.prompts.critic import get_prompt

        result = get_prompt(sample_poster)

        assert "system" in result
        assert "user" in result
        assert "PASS" in result["system"]
        assert "Hello" in result["user"]

    def test_get_visual_prompt_returns_system_and_user(self):
        from app.prompts.critic import get_visual_prompt

        result = get_visual_prompt()

        assert "system" in result
        assert "user" in result
        assert "视觉" in result["system"] or "审核" in result["system"]

    def test_get_prompt_contains_poster_json(self, sample_poster):
        from app.prompts.critic import get_prompt

        result = get_prompt(sample_poster)
        assert "1080" in result["user"]
        assert "1920" in result["user"]


# ============================================================================
# 2. 渲染客户端
# ============================================================================

class TestRenderClient:
    """render_client 模块测试"""

    @patch("app.tools.render_client.httpx.Client")
    def test_render_success(self, mock_client_cls, sample_poster):
        from app.tools.render_client import render_poster_to_image

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "image/png"}
        mock_response.content = FAKE_PNG

        mock_ctx = MagicMock()
        mock_ctx.__enter__ = Mock(return_value=MagicMock(post=Mock(return_value=mock_response)))
        mock_ctx.__exit__ = Mock(return_value=False)
        mock_client_cls.return_value = mock_ctx

        result = render_poster_to_image(sample_poster)

        assert result == FAKE_PNG

    @patch("app.tools.render_client.httpx.Client")
    def test_render_non_200_raises(self, mock_client_cls, sample_poster):
        from app.tools.render_client import render_poster_to_image

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        mock_ctx = MagicMock()
        mock_ctx.__enter__ = Mock(return_value=MagicMock(post=Mock(return_value=mock_response)))
        mock_ctx.__exit__ = Mock(return_value=False)
        mock_client_cls.return_value = mock_ctx

        with pytest.raises(RuntimeError, match="渲染服务返回 500"):
            render_poster_to_image(sample_poster)

    @patch("app.tools.render_client.httpx.Client")
    def test_render_non_image_content_type_raises(self, mock_client_cls, sample_poster):
        from app.tools.render_client import render_poster_to_image

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.content = b"{}"

        mock_ctx = MagicMock()
        mock_ctx.__enter__ = Mock(return_value=MagicMock(post=Mock(return_value=mock_response)))
        mock_ctx.__exit__ = Mock(return_value=False)
        mock_client_cls.return_value = mock_ctx

        with pytest.raises(RuntimeError, match="非图片类型"):
            render_poster_to_image(sample_poster)

    @patch("app.tools.render_client.httpx.Client")
    def test_render_connect_error(self, mock_client_cls, sample_poster):
        import httpx
        from app.tools.render_client import render_poster_to_image

        mock_ctx = MagicMock()
        mock_ctx.__enter__ = Mock(
            return_value=MagicMock(post=Mock(side_effect=httpx.ConnectError("refused")))
        )
        mock_ctx.__exit__ = Mock(return_value=False)
        mock_client_cls.return_value = mock_ctx

        with pytest.raises(RuntimeError, match="无法连接渲染服务"):
            render_poster_to_image(sample_poster)

    @patch("app.tools.render_client.httpx.Client")
    def test_render_timeout(self, mock_client_cls, sample_poster):
        import httpx
        from app.tools.render_client import render_poster_to_image

        mock_ctx = MagicMock()
        mock_ctx.__enter__ = Mock(
            return_value=MagicMock(post=Mock(side_effect=httpx.TimeoutException("timeout")))
        )
        mock_ctx.__exit__ = Mock(return_value=False)
        mock_client_cls.return_value = mock_ctx

        with pytest.raises(RuntimeError, match="渲染服务超时"):
            render_poster_to_image(sample_poster)


# ============================================================================
# 3. 合并逻辑
# ============================================================================

class TestMergeReviews:
    """_merge_reviews 测试"""

    def test_json_only_when_visual_is_none(self, pass_review):
        from app.agents.critic import _merge_reviews

        result = _merge_reviews(pass_review, None)

        assert result["status"] == "PASS"
        assert result["review_path"] == "json_only"

    def test_both_pass(self, pass_review):
        from app.agents.critic import _merge_reviews

        visual = {"status": "PASS", "feedback": "视觉OK", "issues": []}
        result = _merge_reviews(pass_review, visual)

        assert result["status"] == "PASS"
        assert result["review_path"] == "dual"
        assert "[结构]" in result["feedback"]
        assert "[视觉]" in result["feedback"]

    def test_json_reject_visual_pass(self, reject_review):
        from app.agents.critic import _merge_reviews

        visual = {"status": "PASS", "feedback": "视觉OK", "issues": []}
        result = _merge_reviews(reject_review, visual)

        assert result["status"] == "REJECT"
        assert result["review_path"] == "dual"
        assert "[结构]" in result["feedback"]

    def test_json_pass_visual_reject(self, pass_review):
        from app.agents.critic import _merge_reviews

        visual = {"status": "REJECT", "feedback": "文字不可读", "issues": ["low contrast"]}
        result = _merge_reviews(pass_review, visual)

        assert result["status"] == "REJECT"
        assert "[视觉]" in result["feedback"]
        assert "low contrast" in result["issues"]

    def test_both_reject(self, reject_review):
        from app.agents.critic import _merge_reviews

        visual = {"status": "REJECT", "feedback": "渲染异常", "issues": ["blank"]}
        result = _merge_reviews(reject_review, visual)

        assert result["status"] == "REJECT"
        assert len(result["issues"]) == 2

    def test_issues_merged(self):
        from app.agents.critic import _merge_reviews

        j = {"status": "PASS", "feedback": "ok", "issues": ["a"]}
        v = {"status": "PASS", "feedback": "ok", "issues": ["b"]}
        result = _merge_reviews(j, v)

        assert result["issues"] == ["a", "b"]


# ============================================================================
# 4. 级联流程（run_critic_agent）
# ============================================================================

class TestRunCriticAgent:
    """run_critic_agent 整体流程测试（mock 掉 LLM 和渲染服务）"""

    def _mock_json_review(self, return_value):
        return patch("app.agents.critic._run_json_review", return_value=return_value)

    def _mock_visual_review(self, return_value=None, side_effect=None):
        return patch(
            "app.agents.critic._run_visual_review",
            return_value=return_value,
            side_effect=side_effect,
        )

    def _mock_visual_enabled(self, enabled=True):
        return patch("app.agents.critic.settings.critic.ENABLE_VISUAL_REVIEW", enabled)

    def test_json_pass_visual_pass(self, sample_poster):
        from app.agents.critic import run_critic_agent

        json_r = {"status": "PASS", "feedback": "结构OK", "issues": []}
        visual_r = {"status": "PASS", "feedback": "视觉OK", "issues": []}

        with self._mock_json_review(json_r), \
             self._mock_visual_review(visual_r), \
             self._mock_visual_enabled(True):
            result = run_critic_agent(sample_poster)

        assert result["status"] == "PASS"
        assert result["review_path"] == "dual"

    def test_json_reject_skips_visual(self, sample_poster):
        from app.agents.critic import run_critic_agent

        json_r = {"status": "REJECT", "feedback": "文字溢出", "issues": ["overflow"]}

        with self._mock_json_review(json_r) as _, \
             self._mock_visual_review() as mock_vis, \
             self._mock_visual_enabled(True):
            result = run_critic_agent(sample_poster)

        assert result["status"] == "REJECT"
        assert result["review_path"] == "json_only"
        mock_vis.assert_not_called()

    def test_visual_disabled_skips_path2(self, sample_poster):
        from app.agents.critic import run_critic_agent

        json_r = {"status": "PASS", "feedback": "OK", "issues": []}

        with self._mock_json_review(json_r), \
             self._mock_visual_review() as mock_vis, \
             self._mock_visual_enabled(False):
            result = run_critic_agent(sample_poster)

        assert result["status"] == "PASS"
        assert result["review_path"] == "json_only"
        mock_vis.assert_not_called()

    def test_visual_error_degrades_to_pass(self, sample_poster):
        from app.agents.critic import run_critic_agent

        json_r = {"status": "PASS", "feedback": "OK", "issues": []}

        with self._mock_json_review(json_r), \
             self._mock_visual_review(side_effect=RuntimeError("render down")), \
             self._mock_visual_enabled(True):
            result = run_critic_agent(sample_poster)

        assert result["status"] == "PASS"
        assert result["review_path"] == "json_only"

    def test_visual_reject_overrides_final(self, sample_poster):
        from app.agents.critic import run_critic_agent

        json_r = {"status": "PASS", "feedback": "结构OK", "issues": []}
        visual_r = {"status": "REJECT", "feedback": "不可读", "issues": ["contrast"]}

        with self._mock_json_review(json_r), \
             self._mock_visual_review(visual_r), \
             self._mock_visual_enabled(True):
            result = run_critic_agent(sample_poster)

        assert result["status"] == "REJECT"
        assert result["review_path"] == "dual"

    @patch("app.agents.critic._run_json_review", side_effect=Exception("boom"))
    def test_exception_returns_fallback(self, mock_jr, sample_poster):
        from app.agents.critic import run_critic_agent

        result = run_critic_agent(sample_poster)

        assert result["status"] == "PASS"
        assert "issues" in result


# ============================================================================
# 5. 工作流节点
# ============================================================================

class TestCriticNode:
    """critic_node / should_retry_layout 测试"""

    @patch("app.agents.critic.run_critic_agent")
    def test_critic_node_pass(self, mock_run, sample_poster):
        from app.agents.critic import critic_node

        mock_run.return_value = {"status": "PASS", "feedback": "OK", "issues": []}
        state = {"final_poster": sample_poster, "_retry_count": 0}

        result = critic_node(state)

        assert result["review_feedback"]["status"] == "PASS"
        assert result["_retry_count"] == 0

    @patch("app.agents.critic.run_critic_agent")
    def test_critic_node_reject_increments_retry(self, mock_run, sample_poster):
        from app.agents.critic import critic_node

        mock_run.return_value = {"status": "REJECT", "feedback": "bad", "issues": ["x"]}
        state = {"final_poster": sample_poster, "_retry_count": 0}

        result = critic_node(state)

        assert result["review_feedback"]["status"] == "REJECT"
        assert result["_retry_count"] == 1

    @patch("app.agents.critic.run_critic_agent")
    def test_critic_node_preserves_existing_count(self, mock_run, sample_poster):
        from app.agents.critic import critic_node

        mock_run.return_value = {"status": "REJECT", "feedback": "bad", "issues": []}
        state = {"final_poster": sample_poster, "_retry_count": 1}

        result = critic_node(state)
        assert result["_retry_count"] == 2

    def test_should_retry_on_reject_within_limit(self):
        from app.agents.critic import should_retry_layout

        state = {
            "review_feedback": {"status": "REJECT"},
            "_retry_count": 1,
        }
        assert should_retry_layout(state) == "retry"

    def test_should_end_on_pass(self):
        from app.agents.critic import should_retry_layout

        state = {
            "review_feedback": {"status": "PASS"},
            "_retry_count": 0,
        }
        assert should_retry_layout(state) == "end"

    def test_should_end_when_max_retries_exceeded(self):
        from app.agents.critic import should_retry_layout

        state = {
            "review_feedback": {"status": "REJECT"},
            "_retry_count": 10,
        }
        assert should_retry_layout(state) == "end"

    def test_should_end_on_missing_feedback(self):
        from app.agents.critic import should_retry_layout

        state = {"review_feedback": {}, "_retry_count": 0}
        assert should_retry_layout(state) == "end"
