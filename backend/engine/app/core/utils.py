"""
通用工具函数

包含 JSON 解析、文本处理等工具函数。

Author: VibePoster Team
Date: 2025-01
"""

import json
import re
from typing import Dict, Any, Optional

from .logger import get_logger

logger = get_logger(__name__)


def parse_llm_json_response(
    content: str,
    fallback: Optional[Dict[str, Any]] = None,
    context: str = ""
) -> Dict[str, Any]:
    """
    解析 LLM 返回的 JSON（自动处理 markdown 代码块、单引号等常见问题）
    
    Args:
        content: LLM 返回的原始内容
        fallback: 解析失败时的回退值（可选）
        context: 上下文信息，用于日志记录（如 "OCR", "图像理解"）
        
    Returns:
        解析后的 JSON 字典
        
    Raises:
        json.JSONDecodeError: 如果解析失败且没有提供 fallback
    """
    original = content

    if not content or not content.strip():
        logger.warning(f"⚠️ {context} 返回内容为空")
        if fallback is not None:
            return fallback
        raise json.JSONDecodeError("Empty content", "", 0)

    content = re.sub(r'```json\s*', '', content)
    content = re.sub(r'```\s*', '', content)
    content = content.strip()
    
    # 1) 直接解析
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # 2) 用正则提取最外层 { ... }
    json_match = None
    try:
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            extracted = json_match.group(0)
            return json.loads(extracted)
    except json.JSONDecodeError:
        pass

    # 3) 尝试把单引号替换成双引号
    try:
        fixed = content.replace("'", '"')
        return json.loads(fixed)
    except (json.JSONDecodeError, ValueError):
        pass

    # 4) 对提取的片段也做单引号修复
    try:
        if json_match:
            fixed = json_match.group(0).replace("'", '"')
            return json.loads(fixed)
    except (json.JSONDecodeError, ValueError, UnboundLocalError):
        pass

    # 5) 尝试移除尾部逗号（LLM 常见错误）
    try:
        if json_match:
            cleaned = re.sub(r',\s*([}\]])', r'\1', json_match.group(0))
            return json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        pass

    logger.warning(f"⚠️ {context} JSON 解析失败（所有策略均失败）")
    logger.warning(f"原始内容 (前500字): {original[:500]}")

    if fallback is not None:
        logger.info(f"使用回退值")
        return fallback

    raise json.JSONDecodeError("All parsing strategies failed", content, 0)



