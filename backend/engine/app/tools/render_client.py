"""
渲染服务客户端 - 调用 Node.js Render Service 生成海报图片

用于 Critic Agent 双路审核中的视觉审核路径：
将 poster JSON 发送到渲染服务，获取渲染后的 PNG 图片。
"""
import httpx
from typing import Dict, Any

from ..core.config import settings
from ..core.logger import get_logger

logger = get_logger(__name__)

RENDER_TIMEOUT = 30.0


def render_poster_to_image(poster_data: Dict[str, Any]) -> bytes:
    """
    调用 Node.js 渲染服务，将 poster JSON 渲染为 PNG 图片。

    Args:
        poster_data: 包含 canvas 和 layers 的海报数据

    Returns:
        PNG 图片的二进制数据

    Raises:
        RuntimeError: 渲染服务不可用或返回错误
    """
    url = f"{settings.critic.RENDER_SERVICE_URL}/api/render/image?format=png"

    logger.info(f"🖼️ 调用渲染服务: {settings.critic.RENDER_SERVICE_URL}")

    try:
        with httpx.Client(timeout=RENDER_TIMEOUT) as client:
            response = client.post(url, json=poster_data)

        if response.status_code != 200:
            error_detail = response.text[:200]
            raise RuntimeError(
                f"渲染服务返回 {response.status_code}: {error_detail}"
            )

        content_type = response.headers.get("content-type", "")
        if "image" not in content_type:
            raise RuntimeError(
                f"渲染服务返回非图片类型: {content_type}"
            )

        image_bytes = response.content
        logger.info(f"✅ 渲染成功，图片大小: {len(image_bytes)} bytes")
        return image_bytes

    except httpx.ConnectError:
        raise RuntimeError(
            f"无法连接渲染服务 ({settings.critic.RENDER_SERVICE_URL})，请确认服务已启动"
        )
    except httpx.TimeoutException:
        raise RuntimeError(
            f"渲染服务超时 ({RENDER_TIMEOUT}s)"
        )
