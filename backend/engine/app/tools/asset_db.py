"""
素材库工具 - 负责查询素材
支持 Pexels API 和本地占位符回退

注意：Planner Agent 会直接生成英文关键词（style_keywords），无需中英文转换。
关键词会直接组合成搜索词用于图片搜索。

搜索优先级：
1. Pexels API（最高优先级，如果配置了 PEXELS_API_KEY）
2. 本地占位符库（如果所有 API 都失败或未配置）
"""
import requests
from typing import Optional
from ..core.config import settings
from ..core.logger import get_logger

logger = get_logger(__name__)

# Pexels API 配置
PEXELS_API_KEY = settings.visual.PEXELS_API_KEY
PEXELS_API_URL = "https://api.pexels.com/v1/search"

# 本地占位符库（按颜色分类，作为回退）
ASSET_LIBRARY = {
    "red": [
        "https://placehold.co/1080x1920/FF0000/FFF?text=Red+1",
        "https://placehold.co/1080x1920/DC143C/FFF?text=Red+2",
        "https://placehold.co/1080x1920/B22222/FFF?text=Red+3",
    ],
    "orange": [
        "https://placehold.co/1080x1920/FF8C00/FFF?text=Orange+1",
        "https://placehold.co/1080x1920/FF7F50/FFF?text=Orange+2",
        "https://placehold.co/1080x1920/FF6347/FFF?text=Orange+3",
    ],
    "yellow": [
        "https://placehold.co/1080x1920/FFD700/000?text=Yellow+1",
        "https://placehold.co/1080x1920/FFFF00/000?text=Yellow+2",
        "https://placehold.co/1080x1920/FFE135/000?text=Yellow+3",
    ],
    "green": [
        "https://placehold.co/1080x1920/00FF00/000?text=Green+1",
        "https://placehold.co/1080x1920/228B22/FFF?text=Green+2",
        "https://placehold.co/1080x1920/32CD32/000?text=Green+3",
    ],
    "cyan": [
        "https://placehold.co/1080x1920/00FFFF/000?text=Cyan+1",
        "https://placehold.co/1080x1920/00CED1/FFF?text=Cyan+2",
        "https://placehold.co/1080x1920/48D1CC/000?text=Cyan+3",
    ],
    "blue": [
        "https://placehold.co/1080x1920/0000FF/FFF?text=Blue+1",
        "https://placehold.co/1080x1920/1E90FF/FFF?text=Blue+2",
        "https://placehold.co/1080x1920/4169E1/FFF?text=Blue+3",
    ],
    "purple": [
        "https://placehold.co/1080x1920/800080/FFF?text=Purple+1",
        "https://placehold.co/1080x1920/9370DB/FFF?text=Purple+2",
        "https://placehold.co/1080x1920/BA55D3/FFF?text=Purple+3",
    ],
    "pink": [
        "https://placehold.co/1080x1920/FF69B4/FFF?text=Pink+1",
        "https://placehold.co/1080x1920/FF1493/FFF?text=Pink+2",
        "https://placehold.co/1080x1920/FFC0CB/000?text=Pink+3",
    ],
    "brown": [
        "https://placehold.co/1080x1920/A52A2A/FFF?text=Brown+1",
        "https://placehold.co/1080x1920/8B4513/FFF?text=Brown+2",
        "https://placehold.co/1080x1920/D2691E/FFF?text=Brown+3",
    ],
    "black": [
        "https://placehold.co/1080x1920/000000/FFF?text=Black+1",
        "https://placehold.co/1080x1920/1C1C1C/FFF?text=Black+2",
        "https://placehold.co/1080x1920/2F2F2F/FFF?text=Black+3",
    ],
    "white": [
        "https://placehold.co/1080x1920/FFFFFF/000?text=White+1",
        "https://placehold.co/1080x1920/F5F5F5/000?text=White+2",
        "https://placehold.co/1080x1920/FAFAFA/000?text=White+3",
    ],
    "gray": [
        "https://placehold.co/1080x1920/808080/FFF?text=Gray+1",
        "https://placehold.co/1080x1920/696969/FFF?text=Gray+2",
        "https://placehold.co/1080x1920/A9A9A9/000?text=Gray+3",
    ],
    "navy": [
        "https://placehold.co/1080x1920/000080/FFF?text=Navy+1",
        "https://placehold.co/1080x1920/191970/FFF?text=Navy+2",
        "https://placehold.co/1080x1920/00008B/FFF?text=Navy+3",
    ],
    "teal": [
        "https://placehold.co/1080x1920/008080/FFF?text=Teal+1",
        "https://placehold.co/1080x1920/20B2AA/FFF?text=Teal+2",
        "https://placehold.co/1080x1920/40E0D0/000?text=Teal+3",
    ],
    "lime": [
        "https://placehold.co/1080x1920/00FF00/000?text=Lime+1",
        "https://placehold.co/1080x1920/32CD32/000?text=Lime+2",
        "https://placehold.co/1080x1920/ADFF2F/000?text=Lime+3",
    ],
    "maroon": [
        "https://placehold.co/1080x1920/800000/FFF?text=Maroon+1",
        "https://placehold.co/1080x1920/B03060/FFF?text=Maroon+2",
        "https://placehold.co/1080x1920/C71585/FFF?text=Maroon+3",
    ],
    "olive": [
        "https://placehold.co/1080x1920/808000/FFF?text=Olive+1",
        "https://placehold.co/1080x1920/6B8E23/FFF?text=Olive+2",
        "https://placehold.co/1080x1920/9ACD32/000?text=Olive+3",
    ],
    "gold": [
        "https://placehold.co/1080x1920/FFD700/000?text=Gold+1",
        "https://placehold.co/1080x1920/FFA500/000?text=Gold+2",
        "https://placehold.co/1080x1920/FFC125/000?text=Gold+3",
    ],
    "silver": [
        "https://placehold.co/1080x1920/C0C0C0/000?text=Silver+1",
        "https://placehold.co/1080x1920/D3D3D3/000?text=Silver+2",
        "https://placehold.co/1080x1920/E6E6E6/000?text=Silver+3",
    ],
    "coral": [
        "https://placehold.co/1080x1920/FF7F50/FFF?text=Coral+1",
        "https://placehold.co/1080x1920/FF6B6B/FFF?text=Coral+2",
        "https://placehold.co/1080x1920/FF8C69/FFF?text=Coral+3",
    ],
    "turquoise": [
        "https://placehold.co/1080x1920/40E0D0/000?text=Turquoise+1",
        "https://placehold.co/1080x1920/00CED1/FFF?text=Turquoise+2",
        "https://placehold.co/1080x1920/48D1CC/000?text=Turquoise+3",
    ],
    "indigo": [
        "https://placehold.co/1080x1920/4B0082/FFF?text=Indigo+1",
        "https://placehold.co/1080x1920/6A0DAD/FFF?text=Indigo+2",
        "https://placehold.co/1080x1920/8A2BE2/FFF?text=Indigo+3",
    ],
    "magenta": [
        "https://placehold.co/1080x1920/FF00FF/FFF?text=Magenta+1",
        "https://placehold.co/1080x1920/FF1493/FFF?text=Magenta+2",
        "https://placehold.co/1080x1920/DA70D6/FFF?text=Magenta+3",
    ],
    "default": ["https://placehold.co/1080x1920/333333/FFF?text=Default+Background"],
}


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
        "per_page": 1,  # 只取第一张
        "size": "large"  # 获取大尺寸图片
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
            
            # 获取图片 URL
            photo = data["photos"][0]
            # Pexels 提供多种尺寸，优先使用 large 或 original
            image_url = (
                photo.get("src", {}).get("large") or
                photo.get("src", {}).get("original") or
                photo.get("src", {}).get("large2x")
            )
            
            if not image_url:
                logger.warning(f"⚠️ Pexels 返回的图片没有 URL")
                return None
            
            # 下载图片并转换为 base64，避免前端直接访问外部 URL 时的连接问题
            try:
                logger.info(f"📥 正在下载 Pexels 图片...")
                img_response = requests.get(image_url, timeout=15, headers={"User-Agent": "VibePoster/1.0"})
                img_response.raise_for_status()
                image_data = img_response.content
                
                # 转换为 base64
                from ..tools.vision import image_to_base64
                # 根据 URL 判断图片格式
                mime_type = "image/jpeg"  # Pexels 默认是 JPEG
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
                # 如果下载失败，返回 None
                return None
            
        except requests.exceptions.ConnectionError as e:
            # 连接错误（包括 Connection refused）
            if attempt < max_retries:
                logger.warning(f"⚠️ Pexels API 连接失败 (尝试 {attempt + 1}/{max_retries + 1}): {e}")
                import time
                time.sleep(1)  # 等待 1 秒后重试
                continue
            else:
                logger.error(f"⚠️ Pexels API 连接失败 (网络错误，已重试 {max_retries + 1} 次): {e}")
                return None
        except requests.exceptions.Timeout as e:
            # 超时错误
            if attempt < max_retries:
                logger.warning(f"⚠️ Pexels API 请求超时 (尝试 {attempt + 1}/{max_retries + 1}): {e}")
                import time
                time.sleep(1)
                continue
            else:
                logger.error(f"⚠️ Pexels API 请求超时 (已重试 {max_retries + 1} 次): {e}")
                return None
        except requests.exceptions.RequestException as e:
            # 其他请求错误（如 4xx, 5xx）
            logger.error(f"⚠️ Pexels API 调用失败 (HTTP 错误): {e}")
            return None
        except Exception as e:
            # 其他未知错误
            logger.error(f"⚠️ Pexels API 调用失败: {type(e).__name__}: {e}")
            return None
    
    return None


def combine_keywords(keywords: list) -> str:
    """
    将关键词列表组合成搜索词
    Planner Agent 已经生成英文关键词，直接组合即可
    
    Args:
        keywords: 英文关键词列表（由 Planner Agent 生成）
        
    Returns:
        组合后的搜索词
    """
    if not keywords:
        return "background"
    
    # 如果只有一个关键词，直接返回
    if len(keywords) == 1:
        return keywords[0]
    
    # 多个关键词组合，最多取前3个
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

    # Planner Agent 已经生成英文关键词，直接组合成搜索词
    search_query = combine_keywords(keywords)

    # 1. 优先尝试 Pexels API（最高优先级）
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

    # 回退到本地占位符库（按颜色匹配）
    logger.info("📦 使用本地占位符库")
    
    # 颜色关键词映射（用于匹配 ASSET_LIBRARY 的键）
    color_keywords = {
        "red": ["红", "red"],
        "orange": ["橙", "orange"],
        "yellow": ["黄", "yellow", "金", "gold"],
        "green": ["绿", "green"],
        "cyan": ["青", "cyan"],
        "blue": ["蓝", "blue"],
        "navy": ["海军蓝", "navy", "深蓝"],
        "purple": ["紫", "purple"],
        "pink": ["粉", "pink"],
        "brown": ["棕", "brown"],
        "black": ["黑", "black"],
        "white": ["白", "white"],
        "gray": ["灰", "gray", "grey"],
        "teal": ["青绿", "teal"],
        "lime": ["青柠", "lime"],
        "maroon": ["栗", "maroon"],
        "olive": ["橄榄", "olive"],
        "gold": ["金", "gold"],
        "silver": ["银", "silver"],
        "coral": ["珊瑚", "coral"],
        "turquoise": ["青绿", "turquoise"],
        "indigo": ["靛", "indigo"],
        "magenta": ["品红", "magenta"],
    }
    
    # 尝试匹配颜色
    for kw in keywords:
        key = kw.lower()
        for color_name, color_kws in color_keywords.items():
            if color_name in ASSET_LIBRARY:
                for color_kw in color_kws:
                    if color_kw in key:
                        import random
                        return random.choice(ASSET_LIBRARY[color_name])
    
    # 如果没有匹配到颜色，使用默认
    return ASSET_LIBRARY["default"][0]

