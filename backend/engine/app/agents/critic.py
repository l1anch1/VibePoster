"""
Critic Agent - 双路审核（JSON 结构审核 + 视觉审核）

Path 1: 基于 poster JSON 数据做结构合理性检查（快、省 token）
Path 2: 调用渲染服务生成图片，通过 Vision LLM 做视觉质量检查

级联策略：Path 1 通过后才执行 Path 2，任一路 REJECT 则最终 REJECT。
"""

import json
import base64
from typing import Dict, Any, Optional
from ..core.config import settings, ERROR_FALLBACKS
from ..core.llm import LLMClientFactory
from ..core.logger import get_logger
from ..core.utils import parse_llm_json_response
from ..prompts import critic as critic_prompt
from .base import BaseAgent

logger = get_logger(__name__)


class CriticAgent(BaseAgent):
    """Critic Agent 实现类（用于 Path 1 JSON 结构审核）"""

    def _create_client(self):
        return LLMClientFactory.get_client(
            provider=self.config.get("provider", "deepseek"),
            api_key=self.config.get("api_key"),
            base_url=self.config.get("base_url"),
        )

    def invoke(self, messages: list, **kwargs) -> Dict[str, Any]:
        """调用 Critic Agent"""
        response = self.client.chat.completions.create(
            model=self.config["model"],
            messages=messages,
            temperature=self.config["temperature"],
            response_format=self.config.get("response_format"),
            **kwargs,
        )
        return response


# =============================================================================
# Path 1: JSON 结构审核
# =============================================================================

def _run_json_review(
    poster_data: Dict[str, Any],
    design_brief: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Path 1 —— 基于 JSON 数据的结构审核。
    """
    prompts = critic_prompt.get_prompt(poster_data, design_brief=design_brief)

    from .base import AgentFactory
    agent = AgentFactory.get_critic_agent()

    response = agent.invoke(
        messages=[
            {"role": "system", "content": prompts["system"]},
            {"role": "user", "content": prompts["user"]},
        ]
    )

    content = response.choices[0].message.content
    if "```json" in content:
        content = content.replace("```json", "").replace("```", "")

    feedback = json.loads(content)

    feedback.setdefault("status", settings.critic.DEFAULT_STATUS)
    feedback.setdefault("feedback", "审核通过")
    feedback.setdefault("issues", [])

    return feedback


# =============================================================================
# Path 2: 视觉审核（渲染图片 + Vision LLM）
# =============================================================================

VISION_LLM_TIMEOUT = 45.0


def _run_visual_review(poster_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Path 2 —— 调用渲染服务生成图片，再用 Vision LLM 审核。

    Returns:
        与 Path 1 格式一致的审核字典 {status, feedback, issues}
    """
    from ..tools.render_client import render_poster_to_image

    logger.info("🖼️ [Path 2] 开始视觉审核：调用渲染服务...")
    image_bytes = render_poster_to_image(poster_data)

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    prompts = critic_prompt.get_visual_prompt()

    vision_provider = (settings.critic.VISION_PROVIDER or settings.critic.PROVIDER).value
    vision_api_key = settings.critic.VISION_API_KEY or settings.critic.API_KEY
    vision_base_url = settings.critic.VISION_BASE_URL or settings.critic.BASE_URL

    client = LLMClientFactory.get_client(
        provider=vision_provider,
        api_key=vision_api_key,
        base_url=vision_base_url,
    )

    logger.info(f"👁️ [Path 2] 调用 Vision LLM ({settings.critic.VISION_MODEL} @ {vision_provider})...")

    vision_messages = [
        {"role": "system", "content": prompts["system"]},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompts["user"]},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_b64}",
                    },
                },
            ],
        },
    ]

    try:
        response = client.chat.completions.create(
            model=settings.critic.VISION_MODEL,
            messages=vision_messages,
            temperature=0.0,
            response_format={"type": "json_object"},
            timeout=VISION_LLM_TIMEOUT,
        )
    except Exception as e:
        logger.warning(f"⚠️ [Path 2] json_object 模式失败 ({type(e).__name__}), 降级重试...")
        try:
            response = client.chat.completions.create(
                model=settings.critic.VISION_MODEL,
                messages=vision_messages,
                temperature=0.0,
                timeout=VISION_LLM_TIMEOUT,
            )
        except Exception as e2:
            logger.warning(f"⚠️ [Path 2] Vision LLM 调用失败: {type(e2).__name__}: {e2}")
            return {"status": "PASS", "feedback": f"Vision LLM 超时/失败，跳过视觉审核", "issues": []}

    content = response.choices[0].message.content
    logger.info(f"📝 [Path 2] Vision LLM 原始响应 (前300字): {content[:300] if content else '(empty)'}")

    fallback = {"status": "PASS", "feedback": "视觉审核无法解析，默认通过", "issues": []}
    feedback = parse_llm_json_response(content, fallback=fallback, context="视觉审核")

    feedback.setdefault("status", "PASS")
    feedback.setdefault("feedback", "视觉审核通过")
    feedback.setdefault("issues", [])

    return feedback


# =============================================================================
# 合并逻辑
# =============================================================================

def _merge_reviews(
    json_review: Dict[str, Any],
    visual_review: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    合并双路审核结果。任一路 REJECT 则最终 REJECT。
    """
    if visual_review is None:
        json_review["review_path"] = "json_only"
        return json_review

    all_issues = json_review.get("issues", []) + visual_review.get("issues", [])

    json_pass = json_review.get("status") == "PASS"
    visual_pass = visual_review.get("status") == "PASS"

    if json_pass and visual_pass:
        status = "PASS"
        parts = []
        if json_review.get("feedback"):
            parts.append(f"[结构] {json_review['feedback']}")
        if visual_review.get("feedback"):
            parts.append(f"[视觉] {visual_review['feedback']}")
        feedback = " | ".join(parts) or "双路审核通过"
    else:
        status = "REJECT"
        reject_parts = []
        if not json_pass:
            reject_parts.append(f"[结构] {json_review.get('feedback', '')}")
        if not visual_pass:
            reject_parts.append(f"[视觉] {visual_review.get('feedback', '')}")
        feedback = " | ".join(reject_parts)

    return {
        "status": status,
        "feedback": feedback,
        "issues": all_issues,
        "review_path": "dual",
    }


# =============================================================================
# 对外统一入口
# =============================================================================

def run_critic_agent(
    poster_data: Dict[str, Any],
    design_brief: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    运行 Critic Agent（双路审核）。

    1. Path 1: JSON 结构审核（含设计意图对照）
    2. 如果 Path 1 PASS 且启用了视觉审核，执行 Path 2
    3. 合并两路结果返回
    """
    logger.info("⚖️ Critic Agent 正在审核海报质量（双路审核）...")

    try:
        # ---- Path 1: JSON 结构审核 ----
        logger.info("📋 [Path 1] JSON 结构审核...")
        json_review = _run_json_review(poster_data, design_brief=design_brief)

        status_emoji = "✅" if json_review["status"] == "PASS" else "❌"
        logger.info(f"{status_emoji} [Path 1] 结构审核: {json_review['status']} - {json_review.get('feedback', '')}")

        visual_review = None

        # ---- Path 2: 视觉审核（仅在 Path 1 通过时执行） ----
        if json_review["status"] == "REJECT":
            logger.info("⏭️ [Path 2] 跳过视觉审核（结构审核已 REJECT）")
        elif not settings.critic.ENABLE_VISUAL_REVIEW:
            logger.info("⏭️ [Path 2] 视觉审核已关闭（ENABLE_VISUAL_REVIEW=False）")
        else:
            try:
                visual_review = _run_visual_review(poster_data)
                ve = "✅" if visual_review["status"] == "PASS" else "❌"
                logger.info(f"{ve} [Path 2] 视觉审核: {visual_review['status']} - {visual_review.get('feedback', '')}")
            except Exception as e:
                logger.warning(f"⚠️ [Path 2] 视觉审核失败，降级为 PASS: {e}")
                visual_review = None

        # ---- 合并结果 ----
        merged = _merge_reviews(json_review, visual_review)

        final_emoji = "✅" if merged["status"] == "PASS" else "❌"
        logger.info(f"{final_emoji} 最终审核结果 ({merged.get('review_path', 'unknown')}): {merged['status']} - {merged['feedback']}")

        if merged.get("issues"):
            logger.info(f"📋 问题列表: {', '.join(merged['issues'])}")

        return merged

    except Exception as e:
        logger.error(f"❌ Critic Agent 出错: {e}")
        return ERROR_FALLBACKS["critic"]


def critic_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Critic Agent 工作流节点（对上下游透明，签名不变）。
    """
    final_poster = state.get("final_poster", {})
    design_brief = state.get("design_brief")

    current_retry_count = state.get("_retry_count", 0)

    review_feedback = run_critic_agent(final_poster, design_brief=design_brief)

    new_retry_count = current_retry_count
    if review_feedback.get("status") == "REJECT":
        new_retry_count = current_retry_count + 1
        max_retry = settings.critic.MAX_RETRY_COUNT
        logger.info(f"📊 当前重试计数: {new_retry_count}/{max_retry} (之前: {current_retry_count})")

    return {"review_feedback": review_feedback, "_retry_count": new_retry_count}


def should_retry_layout(state: Dict[str, Any]) -> str:
    """
    判断是否应该重新进行 Layout（条件边函数）。
    """
    review_feedback = state.get("review_feedback", {})
    status = review_feedback.get("status", "PASS")
    retry_count = state.get("_retry_count", 0)

    if status == "REJECT":
        max_retry = settings.critic.MAX_RETRY_COUNT
        if retry_count <= max_retry:
            logger.info(f"🔄 审核不通过，准备重试 Layout (第 {retry_count} 次重试，最多{max_retry}次)...")
            return "retry"
        else:
            logger.warning(f"⚠️ 已达到最大重试次数 ({retry_count}/{max_retry})，结束工作流")
            return "end"

    logger.info("✅ 审核通过，结束工作流")
    return "end"
