"""
Asset Agent - 素材管理
纯粹的"大脑" (只调用 tools，不写具体实现)
"""
from typing import Dict, Any
from ..core.config import ASSET_CONFIG, ERROR_FALLBACKS
from ..tools import search_assets


def run_asset_agent(
    design_brief: Dict[str, Any],
    user_uploaded_img: str = None
) -> str:
    """
    运行 Asset Agent
    
    Args:
        design_brief: 设计简报
        user_uploaded_img: 用户上传的图片 URL（可选）
        
    Returns:
        选中的素材 URL
    """
    print("🎨 Asset Agent 正在准备素材...")
    
    # 如果用户上传了图片，直接使用
    if user_uploaded_img:
        print("✅ 检测到用户上传/合成图片，直接使用。")
        return user_uploaded_img
    
    # 否则从素材库中搜索（调用 tools）
    try:
        keywords = design_brief.get("style_keywords", [])
        asset_url = search_assets(keywords)
        print(f"📚 检索到素材库图片: {asset_url}")
        return asset_url
    except Exception as e:
        print(f"❌ Asset Agent 出错: {e}")
        # 使用配置化的错误回退
        return ERROR_FALLBACKS["asset"]["fallback_url"]


def asset_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Asset Agent 工作流节点
    
    Args:
        state: 工作流状态
        
    Returns:
        更新后的状态
    """
    design_brief = state.get("design_brief", {})
    user_uploaded_img = state.get("user_uploaded_img")
    
    selected_asset = run_asset_agent(design_brief, user_uploaded_img)
    
    return {"selected_asset": selected_asset}
