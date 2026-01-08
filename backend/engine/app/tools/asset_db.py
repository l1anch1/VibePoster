"""
素材库工具 - 负责查询素材
支持 Pexels API 和本地占位符回退

注意：Planner Agent 会直接生成英文关键词（style_keywords），无需中英文转换。
关键词会直接组合成搜索词用于图片搜索。

搜索优先级：
1. Pexels API（最高优先级，如果配置了 PEXELS_API_KEY）
2. 本地占位符库（如果所有 API 都失败或未配置）
"""
import json
import random
import requests
from pathlib import Path
from typing import Optional, Dict, List
from ..core.config import settings
from ..core.logger import get_logger

logger = get_logger(__name__)

# Pexels API 配置
PEXELS_API_KEY = settings.visual.PEXELS_API_KEY
PEXELS_API_URL = "https://api.pexels.com/v1/search"

# 数据文件路径
DATA_FILE = Path(__file__).parent / "data" / "asset_library.json"


def _load_asset_library() -> Dict:
    """加载素材库数据"""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"⚠️ 素材库文件不存在: {DATA_FILE}")
        return {"placeholders": {"default": []}, "color_keywords": {}}
    except json.JSONDecodeError as e:
        logger.error(f"❌ 素材库文件解析失败: {e}")
        return {"placeholders": {"default": []}, "color_keywords": {}}


# 延迟加载素材库数据
_asset_data: Optional[Dict] = None


def get_asset_library() -> Dict[str, List[str]]:
    """获取占位符素材库"""
    global _asset_data
    if _asset_data is None:
        _asset_data = _load_asset_library()
    return _asset_data.get("placeholders", {})


def get_color_keywords() -> Dict[str, List[str]]:
    """获取颜色关键词映射"""
    global _asset_data
    if _asset_data is None:
        _asset_data = _load_asset_library()
    return _asset_data.get("color_keywords", {})


def search_pexels(query: str, orientation: str = "portrait", max_retries: int = 2) -> Optional[str]:
    """
    从 Pexels API 搜索图片
    
    Args:
        query: 搜索关键词
        orientation: 图片方向 (portrait/landscape/square)
        max_retries: 最大重试次数（默认 2 次）
        
    Returns:
        图片 URL 或 None
    """
    if not PEXELS_API_KEY:
        return None
    
    # Pexels 的 orientation 参数映射
    orientation_map = {
        "portrait": "portrait",
        "landscape": "landscape",
        "square": "square"
    }
    pexels_orientation = orientation_map.get(orientation, "portrait")
    
    params = {
        "query": query,
        "orientation": pexels_orientation,
        "per_page": 1,
        "size": "large"
    }
    
    headers = {
        "Authorization": PEXELS_API_KEY,
        "User-Agent": "VibePoster/1.0"
    }
    
    # 重试机制
    for attempt in range(max_retries + 1):
        try:
            response = requests.get(
                PEXELS_API_URL,
                params=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            if not data.get("photos") or len(data["photos"]) == 0:
                logger.warning(f"⚠️ Pexels 搜索 '{query}' 没有找到结果")
                return None
            
            photo = data["photos"][0]
            image_url = (
                photo.get("src", {}).get("large") or
                photo.get("src", {}).get("original") or
                photo.get("src", {}).get("large2x")
            )
            
            if not image_url:
                logger.warning(f"⚠️ Pexels 返回的图片没有 URL")
                return None
            
            # 下载图片并转换为 base64
            try:
                logger.info(f"📥 正在下载 Pexels 图片...")
                img_response = requests.get(image_url, timeout=15, headers={"User-Agent": "VibePoster/1.0"})
                img_response.raise_for_status()
                image_data = img_response.content
                
                from ..tools.vision import image_to_base64
                mime_type = "image/jpeg"
                if ".png" in image_url.lower():
                    mime_type = "image/png"
                elif ".webp" in image_url.lower():
                    mime_type = "image/webp"
                
                base64_url = image_to_base64(image_data, mime_type)
                
                photo_desc = photo.get("alt") or query
                photographer = photo.get("photographer", "")
                logger.info(f"✅ 从 Pexels 找到图片: {photo_desc}")
                if photographer:
                    logger.debug(f"   摄影师: {photographer}")
                logger.debug(f"   图片已转换为 base64，大小: {len(image_data) / 1024:.1f} KB")
                return base64_url
            except Exception as e:
                logger.warning(f"⚠️ 下载 Pexels 图片失败: {e}")
                return None
            
        except requests.exceptions.ConnectionError as e:
            if attempt < max_retries:
                logger.warning(f"⚠️ Pexels API 连接失败 (尝试 {attempt + 1}/{max_retries + 1}): {e}")
                import time
                time.sleep(1)
                continue
            else:
                logger.error(f"⚠️ Pexels API 连接失败 (网络错误，已重试 {max_retries + 1} 次): {e}")
                return None
        except requests.exceptions.Timeout as e:
            if attempt < max_retries:
                logger.warning(f"⚠️ Pexels API 请求超时 (尝试 {attempt + 1}/{max_retries + 1}): {e}")
                import time
                time.sleep(1)
                continue
            else:
                logger.error(f"⚠️ Pexels API 请求超时 (已重试 {max_retries + 1} 次): {e}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"⚠️ Pexels API 调用失败 (HTTP 错误): {e}")
            return None
        except Exception as e:
            logger.error(f"⚠️ Pexels API 调用失败: {type(e).__name__}: {e}")
            return None
    
    return None


def combine_keywords(keywords: list) -> str:
    """
    将关键词列表组合成搜索词
    
    Args:
        keywords: 英文关键词列表（由 Planner Agent 生成）
        
    Returns:
        组合后的搜索词
    """
    if not keywords:
        return "background"
    
    if len(keywords) == 1:
        return keywords[0]
    
    return " ".join(keywords[:3])


def search_assets(keywords: list) -> str:
    """
    根据关键词在素材库里找图片
    优先使用 Pexels API，失败则回退到本地占位符
    
    Args:
        keywords: 风格关键词列表
        
    Returns:
        素材 URL
    """
    logger.info(f"📚 正在检索素材库，关键词: {keywords}")

    search_query = combine_keywords(keywords)

    # 1. 优先尝试 Pexels API
    if PEXELS_API_KEY:
        logger.info(f"🔍 使用 Pexels 搜索: {search_query}")
        image_url = search_pexels(search_query, orientation="portrait")
        if image_url:
            logger.info(f"✅ 成功从 Pexels 获取图片，返回 URL")
            return image_url
        else:
            logger.warning("⚠️ Pexels 搜索未返回图片，使用本地占位符")
    else:
        logger.warning("⚠️ 未配置 PEXELS_API_KEY，使用本地占位符")

    # 2. 回退到本地占位符库
    logger.info("📦 使用本地占位符库")
    
    asset_library = get_asset_library()
    color_keywords = get_color_keywords()
    
    # 尝试匹配颜色
    for kw in keywords:
        key = kw.lower()
        for color_name, color_kws in color_keywords.items():
            if color_name in asset_library:
                for color_kw in color_kws:
                    if color_kw in key:
                        return random.choice(asset_library[color_name])
    
    # 如果没有匹配到颜色，使用默认
    default_assets = asset_library.get("default", [])
    if default_assets:
        return default_assets[0]
    
    return "https://placehold.co/1080x1920/333333/FFF?text=Default+Background"
