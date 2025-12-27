"""
Layout Agent - 空间计算与排版
纯粹的"大脑" (只写 Prompt 和调用 LLM)
"""
import json
from typing import Dict, Any, Optional
from ..core.config import CANVAS_DEFAULTS, ERROR_FALLBACKS, GEMINI_CONFIG
from ..core.llm import LLMClientFactory
from ..prompts import get_layout_prompt
from .base import BaseAgent


class LayoutAgent(BaseAgent):
    """Layout Agent 实现类"""
    
    def _create_client(self):
        return LLMClientFactory.get_gemini_client()
    
    def invoke(self, contents: str, **kwargs) -> Dict[str, Any]:
        """调用 Layout Agent"""
        from google.genai import types
        
        response = self.client.models.generate_content(
            model=GEMINI_CONFIG["model"],
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type=GEMINI_CONFIG.get("response_mime_type", "application/json")
            ),
            **kwargs,
        )
        return response


def run_layout_agent(
    design_brief: Dict[str, Any],
    asset_list: Dict[str, Any],
    canvas_width: int = None,
    canvas_height: int = None,
    review_feedback: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    运行 Layout Agent
    
    Args:
        design_brief: 设计简报
        asset_list: 资产列表
        canvas_width: 画布宽度（可选）
        canvas_height: 画布高度（可选）
        review_feedback: 审核反馈（可选，用于修正）
        
    Returns:
        海报 JSON 数据
    """
    print("📐 Layout (Gemini Native) 正在计算布局坐标...")
    
    # 如果有审核反馈，打印出来方便调试
    if review_feedback:
        if review_feedback.get("status") == "REJECT":
            print(f"📝 收到审核反馈（需要修正）: {review_feedback.get('feedback', '')}")
            if review_feedback.get("issues"):
                print(f"📋 需要修正的问题: {', '.join(review_feedback.get('issues', []))}")
        else:
            print("✅ 审核已通过，无需修正")

    try:
        # 使用配置化的 prompt
        prompt_content = get_layout_prompt(
            design_brief=design_brief,
            asset_list=asset_list,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            review_feedback=review_feedback,
        )

        # 使用工厂类获取 Agent
        from .base import AgentFactory
        agent = AgentFactory.get_layout_agent()
        
        # 调用 Agent（使用统一的 invoke 接口）
        response = agent.invoke(contents=prompt_content)

        # 解析结果
        content = response.text

        # 清理可能存在的 markdown 标记
        if "```json" in content:
            content = content.replace("```json", "").replace("```", "")

        poster_json = json.loads(content)

        # 修正 src 和验证图层位置
        canvas_width = poster_json.get("canvas", {}).get("width", CANVAS_DEFAULTS["width"])
        canvas_height = poster_json.get("canvas", {}).get("height", CANVAS_DEFAULTS["height"])
        
        # 确保背景图 src 正确
        bg_layer = next((l for l in poster_json.get("layers", []) if l.get("id") == "bg"), None)
        if bg_layer and asset_list.get("background_layer"):
            bg_layer["src"] = asset_list["background_layer"]["src"]
        
        # 确保前景图 src 正确，并限制尺寸
        fg_layer = next((l for l in poster_json.get("layers", []) if l.get("id") in ["person", "foreground"]), None)
        if fg_layer and asset_list.get("foreground_layer"):
            fg_layer["src"] = asset_list["foreground_layer"]["src"]
            
            # 限制前景图层尺寸，确保不会完全遮挡背景
            max_fg_width = int(canvas_width * 0.5)  # 最大宽度为画布的50%
            max_fg_height = int(canvas_height * 0.6)  # 最大高度为画布的60%
            
            current_width = fg_layer.get("width", 0)
            current_height = fg_layer.get("height", 0)
            
            # 如果尺寸超过限制，按比例缩小
            if current_width > max_fg_width or current_height > max_fg_height:
                # 计算缩放比例，保持宽高比
                scale_w = max_fg_width / current_width if current_width > 0 else 1
                scale_h = max_fg_height / current_height if current_height > 0 else 1
                scale = min(scale_w, scale_h)  # 取较小的比例，确保两个方向都不超过
                
                new_width = int(current_width * scale)
                new_height = int(current_height * scale)
                
                print(f"📏 前景图层尺寸过大 ({current_width}x{current_height})，自动缩小到 ({new_width}x{new_height})")
                fg_layer["width"] = new_width
                fg_layer["height"] = new_height
        
        # 验证并修正图层位置，确保不超出画布范围
        for layer in poster_json.get("layers", []):
            if layer.get("x", 0) < 0:
                layer["x"] = 0
            if layer.get("y", 0) < 0:
                layer["y"] = 0
            
            # 确保图层右边界不超出画布
            layer_width = layer.get("width", 0)
            layer_height = layer.get("height", 0)
            if layer.get("x", 0) + layer_width > canvas_width:
                layer["x"] = max(0, canvas_width - layer_width)
            if layer.get("y", 0) + layer_height > canvas_height:
                layer["y"] = max(0, canvas_height - layer_height)
            
            # 确保 z_index 存在
            if "z_index" not in layer:
                if layer.get("id") == "bg":
                    layer["z_index"] = 0
                elif layer.get("id") in ["person", "foreground"]:
                    layer["z_index"] = 1
                else:
                    layer["z_index"] = 2

        print(f"✅ Layout 完成，生成了 {len(poster_json.get('layers', []))} 个图层")
        return poster_json

    except Exception as e:
        print(f"❌ Gemini Layout Error: {e}")
        # 打印详细错误方便调试
        if hasattr(e, "response"):
            print(e.response)

        return ERROR_FALLBACKS["layout"]


def layout_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Layout Agent 工作流节点
    
    Args:
        state: 工作流状态
        
    Returns:
        更新后的状态
    """
    design_brief = state.get("design_brief", {})
    asset_list = state.get("asset_list", {})
    review_feedback = state.get("review_feedback")
    
    final_poster = run_layout_agent(
        design_brief=design_brief,
        asset_list=asset_list,
        canvas_width=CANVAS_DEFAULTS["width"],
        canvas_height=CANVAS_DEFAULTS["height"],
        review_feedback=review_feedback,
    )
    
    return {"final_poster": final_poster}
