"""
海报生成服务 - 业务逻辑层

提供一次性生成海报的能力（通过 LangGraph 工作流）。
当前由 MCP Server 调用。前端使用分步向导 API（steps.py）。
"""
from typing import Dict, Any, Optional, List
from ..core.logger import get_logger

logger = get_logger(__name__)


class PosterService:
    """海报生成服务类"""
    
    def __init__(self, search_assets_func=None):
        from ..workflow import app_workflow
        from ..tools import search_assets as _search_assets
        self.workflow = app_workflow
        self.search_assets = search_assets_func or _search_assets
    
    def process_user_images(
        self, 
        image_subject: Optional[bytes] = None,
        image_bg: Optional[bytes] = None
    ) -> List[Dict[str, Any]]:
        """
        处理用户上传的图片
        
        Args:
            image_subject: 主体素材二进制数据（透明 PNG）
            image_bg: 背景图片二进制数据
            
        Returns:
            用户图片列表
        """
        user_images = []
        
        if image_bg:
            logger.info("📸 检测到用户上传了背景图...")
            user_images.append({
                "type": "background",
                "data": image_bg,
            })
        
        if image_subject:
            logger.info("📸 检测到用户上传了主体素材...")
            user_images.append({
                "type": "subject",
                "data": image_subject,
            })
        
        return user_images if user_images else None
    
    def build_initial_state(
        self,
        prompt: str,
        canvas_width: int,
        canvas_height: int,
        user_images: Optional[List[Dict[str, Any]]] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
        brand_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        构建工作流初始状态
        
        Args:
            prompt: 用户输入的提示词
            canvas_width: 画布宽度
            canvas_height: 画布高度
            user_images: 用户上传的图片列表
            chat_history: 对话历史（可选）
            brand_name: 品牌名称，用于 RAG 检索（可选）
            
        Returns:
            工作流初始状态字典
        """
        return {
            "user_prompt": prompt,
            "chat_history": chat_history,  # 暂时不支持多轮对话，但保留接口
            "user_images": user_images,
            "canvas_width": canvas_width,  # 画布尺寸作为独立字段（技术参数）
            "canvas_height": canvas_height,
            "brand_name": brand_name,  # 品牌名称，用于 RAG 检索（可选）
            "design_brief": {},  # 设计简报（由 Planner Agent 生成，不包含技术参数）
            "asset_list": None,
            "final_poster": {},
            "review_feedback": None,
            "_retry_count": 0,  # 重试计数器
            "search_assets": self.search_assets,
        }
    
    def generate_poster(
        self,
        prompt: str,
        canvas_width: int,
        canvas_height: int,
        image_subject: Optional[bytes] = None,
        image_bg: Optional[bytes] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
        brand_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成海报（主要业务逻辑）
        
        集成功能：
        - Knowledge Graph: 根据 prompt 中的行业/氛围关键词推理设计规则
        - RAG: 如果指定 brand_name，检索企业品牌知识库
        
        Args:
            prompt: 用户输入的提示词
            canvas_width: 画布宽度
            canvas_height: 画布高度
            image_subject: 主体素材二进制数据（可选，透明 PNG）
            image_bg: 背景图片二进制数据（可选）
            chat_history: 对话历史（可选）
            brand_name: 品牌名称，用于 RAG 检索（可选）
            
        Returns:
            生成的海报数据
        """
        logger.info(f"🚀 收到设计请求: {prompt}")
        logger.info(f"🎨 画布尺寸: {canvas_width}x{canvas_height}")
        if brand_name:
            logger.info(f"📚 品牌名称: {brand_name} (将启用 RAG 检索)")
        
        user_images = self.process_user_images(image_subject, image_bg)
        
        # 构建初始状态
        initial_state = self.build_initial_state(
            prompt=prompt,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            user_images=user_images,
            chat_history=chat_history,
            brand_name=brand_name  # 传递品牌名称用于 RAG 检索
        )
        
        # 启动工作流
        logger.info("🤖 启动 Agent 工作流 (Planner[KG+RAG] -> Visual -> Layout -> Critic)...")
        final_state = self.workflow.invoke(initial_state)
        
        logger.info("🏁 生成结束，返回 JSON 数据。")
        final_poster = final_state["final_poster"]
        
        # 记录最终海报的图层信息，方便调试
        if final_poster and "layers" in final_poster:
            logger.debug("📊 最终返回的图层信息:")
            for layer in final_poster.get("layers", []):
                if layer.get("type") == "image":
                    src = layer.get("src", "")
                    logger.debug(f"  - {layer.get('id', 'unknown')}: src={src[:100] if src else 'None'}...")
        
        return final_poster
