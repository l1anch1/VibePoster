"""
素材库工具 - 负责查询素材
支持 Unsplash API 和本地占位符回退
"""
import os
import requests
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Unsplash API 配置
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"

# 本地占位符库（作为回退）
ASSET_LIBRARY = {
    "tech": [
        "https://placehold.co/1080x1920/000033/FFF?text=Tech+Bg+1",
        "https://placehold.co/1080x1920/000088/FFF?text=Cyber+Circuit",
    ],
    "festive": [
        "https://placehold.co/1080x1920/AA0000/FFF?text=Red+Lanterns",
        "https://placehold.co/1080x1920/FF0000/FFD700?text=Festive+Background",
    ],
    "minimalist": [
        "https://placehold.co/1080x1920/F0F0F0/333?text=Clean+White",
        "https://placehold.co/1080x1920/EFEFEF/999?text=Minimal+Gray",
    ],
    "default": ["https://placehold.co/1080x1920/333333/FFF?text=Default+Background"],
}


def search_unsplash(query: str, orientation: str = "portrait") -> Optional[str]:
    """
    从 Unsplash API 搜索图片
    
    Args:
        query: 搜索关键词
        orientation: 图片方向 (portrait/landscape/square)
        
    Returns:
        图片 URL 或 None
    """
    if not UNSPLASH_ACCESS_KEY:
        return None
    
    try:
        params = {
            "query": query,
            "orientation": orientation,
            "per_page": 1,  # 只取第一张
            "client_id": UNSPLASH_ACCESS_KEY,
        }
        
        response = requests.get(UNSPLASH_API_URL, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        if not data.get("results") or len(data["results"]) == 0:
            print(f"⚠️ Unsplash 搜索 '{query}' 没有找到结果")
            return None
        
        # 获取原始尺寸图片 URL
        photo = data["results"][0]
        image_url = photo["urls"].get("raw") or photo["urls"].get("full")
        
        if not image_url:
            print(f"⚠️ Unsplash 返回的图片没有 URL")
            return None
        
        # 添加尺寸参数（适合海报尺寸）
        # Unsplash URL 格式可能是 https://images.unsplash.com/photo-xxx?ixid=... 或 https://images.unsplash.com/photo-xxx
        if "w=" not in image_url:
            # 判断 URL 中是否已有查询参数
            separator = "&" if "?" in image_url else "?"
            image_url = f"{image_url}{separator}w=1080&h=1920&fit=crop"
        
        photo_desc = photo.get('description') or photo.get('alt_description') or query
        print(f"✅ 从 Unsplash 找到图片: {photo_desc}")
        print(f"   图片 URL: {image_url[:80]}...")
        return image_url
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Unsplash API 调用失败 (网络错误): {e}")
        return None
    except Exception as e:
        print(f"⚠️ Unsplash API 调用失败: {type(e).__name__}: {e}")
        return None
    
    return None


def keywords_to_english(keywords: list) -> str:
    """
    将中文关键词转换为英文搜索词
    
    Args:
        keywords: 中文关键词列表
        
    Returns:
        英文搜索词
    """
    # 关键词映射表
    keyword_map = {
        "科技": "technology",
        "科技感": "technology",
        "赛博朋克": "cyberpunk",
        "未来": "future",
        "高科技": "high tech",
        "喜庆": "festive",
        "红色": "red",
        "节日": "festival",
        "简约": "minimalist",
        "极简": "minimal",
        "干净": "clean",
        "白色": "white",
        "海滩": "beach",
        "沙滩": "beach",
        "海洋": "ocean",
        "天空": "sky",
        "自然": "nature",
        "休闲": "leisure",
        "放松": "relax",
        "风景": "landscape",
        "城市": "city",
        "建筑": "architecture",
        "商务": "business",
        "办公": "office",
        "创意": "creative",
        "艺术": "art",
        "绿色": "green",
        "森林": "forest",
        "户外": "outdoor",
    }
    
    # 尝试映射关键词
    for kw in keywords:
        kw_lower = kw.lower()
        # 直接匹配
        if kw_lower in keyword_map:
            return keyword_map[kw_lower]
        # 部分匹配
        for chinese, english in keyword_map.items():
            if chinese in kw_lower:
                return english
    
    # 如果没有匹配，使用第一个关键词（可能是英文）
    return keywords[0] if keywords else "background"


def search_assets(keywords: list) -> str:
    """
    根据关键词在素材库里找图片
    优先使用 Unsplash API，失败则回退到本地占位符
    
    Args:
        keywords: 风格关键词列表
        
    Returns:
        素材 URL
    """
    print(f"📚 Asset Agent 正在检索素材库，关键词: {keywords}")

    # 如果有 Unsplash API Key，尝试从 Unsplash 搜索
    if UNSPLASH_ACCESS_KEY:
        # 将关键词转换为英文搜索词
        search_query = keywords_to_english(keywords)
        print(f"🔍 使用 Unsplash 搜索: {search_query}")
        
        # 尝试搜索（竖版图片）
        image_url = search_unsplash(search_query, orientation="portrait")
        if image_url:
            print(f"✅ 成功从 Unsplash 获取图片，返回 URL")
            return image_url
        else:
            print("⚠️ Unsplash 搜索未返回图片，使用本地占位符")
    else:
        print("⚠️ 未配置 UNSPLASH_ACCESS_KEY，使用本地占位符")
    
    # 回退到本地占位符库
    print("📦 使用本地占位符库")
    for kw in keywords:
        key = kw.lower()
        if "科技" in key or "tech" in key or "cyber" in key:
            return ASSET_LIBRARY["tech"][0]
        if "喜庆" in key or "红" in key or "festive" in key:
            return ASSET_LIBRARY["festive"][0]
        if "简约" in key or "minimal" in key:
            return ASSET_LIBRARY["minimalist"][0]

    return ASSET_LIBRARY["default"][0]

