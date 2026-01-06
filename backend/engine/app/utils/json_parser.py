"""
JSON 解析工具 - 处理 LLM 返回的 JSON 数据
"""
import json
import re
from typing import Dict, Any, Optional
from ..core.logger import get_logger

logger = get_logger(__name__)


def parse_llm_json_response(
    content: str,
    fallback: Optional[Dict[str, Any]] = None,
    context: str = ""
) -> Dict[str, Any]:
    """
    解析 LLM 返回的 JSON（自动处理 markdown 代码块）
    
    Args:
        content: LLM 返回的原始内容
        fallback: 解析失败时的回退值（可选）
        context: 上下文信息，用于日志记录（如 "OCR", "图像理解"）
        
    Returns:
        解析后的 JSON 字典
        
    Raises:
        json.JSONDecodeError: 如果解析失败且没有提供 fallback
    """
    # 移除可能的 markdown 代码块标记
    content = re.sub(r'```json\s*', '', content)
    content = re.sub(r'```\s*', '', content)
    content = content.strip()
    
    try:
        result = json.loads(content)
        return result
    except json.JSONDecodeError as e:
        logger.warning(f"⚠️ {context} JSON 解析失败: {e}")
        logger.debug(f"原始内容: {content[:200]}...")
        
        if fallback is not None:
            logger.info(f"使用回退值")
            return fallback
        
        # 尝试提取部分内容
        try:
            # 尝试提取 JSON 对象（查找 { ... }）
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
            if json_match:
                extracted = json_match.group(0)
                return json.loads(extracted)
        except:
            pass
        
        # 如果没有 fallback 且提取失败，抛出异常
        raise


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    从文本中提取 JSON 对象（尽力尝试）
    
    Args:
        text: 包含 JSON 的文本
        
    Returns:
        提取到的 JSON 字典，失败返回 None
    """
    try:
        # 尝试直接解析
        return json.loads(text)
    except:
        pass
    
    # 尝试查找 JSON 对象
    try:
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
    except:
        pass
    
    return None

