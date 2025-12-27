"""
Prompter Agent - 视觉调度中心
处理图片（抠图、分析、搜图），是"视觉调度中心"
"""
from typing import Dict, Any, Optional, List
from ..core.config import ERROR_FALLBACKS, DEEPSEEK_CONFIG
from ..core.llm import LLMClientFactory
from ..tools.vision import process_cutout, image_to_base64
from ..tools import search_assets
from .base import BaseAgent


class PrompterAgent(BaseAgent):
    """Prompter Agent 实现类（用于路由决策）"""
    
    def _create_client(self):
        return LLMClientFactory.get_deepseek_client()
    
    def invoke(self, messages: list, **kwargs) -> Dict[str, Any]:
        """调用 Prompter Agent"""
        response = self.client.chat.completions.create(
            model=DEEPSEEK_CONFIG["model"],
            messages=messages,
            temperature=DEEPSEEK_CONFIG.get("temperature", 0.7),
            response_format=DEEPSEEK_CONFIG.get("response_format"),
            **kwargs,
        )
        return response


def run_prompter_agent(
    user_images: Optional[List[Dict[str, Any]]],
    design_brief: Dict[str, Any]
) -> Dict[str, Any]:
    """
    运行 Prompter Agent
    
    路由逻辑：
    - 情况 A（双图）：用户传了 Image A (背景) + Image B (人) -> 抠图 B，保留 A
    - 情况 B（单图）：用户传了 Image B (人) -> 抠图 B，去素材库搜/生成背景 A
    - 情况 C（无图）：去素材库搜/生成背景 A
    
    Args:
        user_images: 用户上传的图片列表 [{"type": "person"|"background", "data": bytes}]
        design_brief: 设计简报
        
    Returns:
        资产列表字典
    """
    print("🎨 Prompter Agent 正在处理图片...")
    
    image_count = len(user_images) if user_images else 0
    
    try:
        # 情况 C：无图，直接搜索素材库
        if image_count == 0:
            print("📚 情况 C：无图，搜索素材库...")
            keywords = design_brief.get("style_keywords", [])
            bg_url = search_assets(keywords)
            
            return {
                "background_layer": {
                    "type": "image",
                    "src": bg_url,
                    "source_type": "stock",
                }
            }
        
        # 情况 A 或 B：有图，需要路由决策
        # 使用 LLM 做路由决策（如果图片数量不明确）
        if image_count == 1:
            # 单图情况：判断是人物还是背景
            # 简化处理：假设是人物，进行抠图
            print("📸 情况 B：单图，假设是人物，进行抠图...")
            image_data = user_images[0].get("data")
            
            if image_data:
                # 抠图
                cutout_result = process_cutout(image_data)
                
                # 搜索背景
                keywords = design_brief.get("style_keywords", [])
                bg_url = search_assets(keywords)
                
                return {
                    "background_layer": {
                        "type": "image",
                        "src": bg_url,
                        "source_type": "stock",
                    },
                    "foreground_layer": {
                        "type": "image",
                        "src": cutout_result["processed_image_base64"],
                        "source_type": "user_upload",
                        "width": cutout_result["width"],
                        "height": cutout_result["height"],
                        "suggested_position": "center_bottom",
                        "subject_bbox": cutout_result.get("subject_bbox"),
                    }
                }
        
        elif image_count >= 2:
            # 情况 A：双图，第一张是背景，第二张是人物
            print("📸 情况 A：双图融合，第一张背景，第二张人物...")
            bg_data = user_images[0].get("data")
            person_data = user_images[1].get("data")
            
            # 背景图转 Base64
            bg_base64 = image_to_base64(bg_data) if bg_data else None
            
            # 人物图抠图
            cutout_result = process_cutout(person_data) if person_data else None
            
            if not bg_base64 or not cutout_result:
                raise ValueError("图片处理失败")
            
            return {
                "background_layer": {
                    "type": "image",
                    "src": bg_base64,
                    "source_type": "user_upload",
                },
                "foreground_layer": {
                    "type": "image",
                    "src": cutout_result["processed_image_base64"],
                    "source_type": "user_upload",
                    "width": cutout_result["width"],
                    "height": cutout_result["height"],
                    "suggested_position": "center_bottom",
                    "subject_bbox": cutout_result.get("subject_bbox"),
                }
            }
        
        # 默认情况
        raise ValueError(f"无法处理的图片数量: {image_count}")
        
    except Exception as e:
        print(f"❌ Prompter Agent 出错: {e}")
        return ERROR_FALLBACKS["prompter"]


def prompter_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prompter Agent 工作流节点
    
    Args:
        state: 工作流状态
        
    Returns:
        更新后的状态
    """
    user_images = state.get("user_images")
    design_brief = state.get("design_brief", {})
    
    asset_list = run_prompter_agent(user_images, design_brief)
    
    return {"asset_list": asset_list}
