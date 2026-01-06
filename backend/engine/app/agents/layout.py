"""
Layout Agent - 空间计算与排版
纯粹的"大脑" (只写 Prompt 和调用 LLM) 输出最终的poster JSON
"""

import json
import re
from typing import Dict, Any, Optional
from ..core.config import settings
from ..core.llm import LLMClientFactory
from ..core.logger import get_logger
from ..prompts import get_layout_prompt
from .base import BaseAgent

logger = get_logger(__name__)


def _fix_truncated_json(content: str, asset_list: Dict[str, Any]) -> str:
    """
    修复被截断的 JSON（主要是 base64 字符串被截断的情况）

    Args:
        content: 原始 JSON 字符串（可能被截断）
        asset_list: 资产列表，用于替换截断的 src

    Returns:
        修复后的 JSON 字符串
    """
    # 查找所有被截断的 src 字段（以 "src": "data:image 开头但未闭合）
    # 模式：匹配 "src": "data:image... 但引号未闭合的情况
    pattern = r'"src":\s*"data:image[^"]*'

    def replace_truncated_src(match):
        # 获取图层 ID（通过查找前面的 "id" 字段）
        match_start = match.start()
        # 向前查找最近的 "id" 字段（在当前图层对象内）
        # 从匹配位置向前查找，找到最近的 "id" 字段
        before_match = content[:match_start]
        # 反向查找，找到最近的图层对象开始位置
        layer_start = before_match.rfind("{")
        if layer_start >= 0:
            layer_content = before_match[layer_start:]
            id_match = re.search(r'"id":\s*"([^"]+)"', layer_content)
            layer_id = id_match.group(1) if id_match else None
        else:
            layer_id = None

        # 根据图层 ID 确定应该使用哪个 src
        if layer_id == "bg" and asset_list.get("background_layer"):
            replacement_src = asset_list["background_layer"].get("src", "")
            logger.info(f"🔧 修复背景图层 src（图层 ID: {layer_id}）")
        elif layer_id in ["person", "foreground"] and asset_list.get("foreground_layer"):
            replacement_src = asset_list["foreground_layer"].get("src", "")
            logger.info(f"🔧 修复前景图层 src（图层 ID: {layer_id}）")
        else:
            # 如果找不到对应的 src，使用空字符串
            replacement_src = ""
            logger.warning(f"⚠️ 无法找到图层 {layer_id} 对应的 src，使用空字符串")

        # 转义 JSON 字符串中的特殊字符
        replacement_src = replacement_src.replace("\\", "\\\\").replace('"', '\\"')
        return f'"src": "{replacement_src}"'

    # 替换所有被截断的 src
    fixed_content = re.sub(pattern, replace_truncated_src, content)

    # 确保 JSON 字符串正确闭合
    # 如果最后有未闭合的引号或括号，尝试修复
    if fixed_content.count('"') % 2 != 0:
        # 引号未闭合，添加闭合引号
        fixed_content = fixed_content.rstrip() + '"'

    # 确保 JSON 对象正确闭合
    open_braces = fixed_content.count("{")
    close_braces = fixed_content.count("}")
    if open_braces > close_braces:
        # 缺少闭合括号
        fixed_content = fixed_content.rstrip() + "}" * (open_braces - close_braces)

    return fixed_content


class LayoutAgent(BaseAgent):
    """Layout Agent 实现类"""

    def _create_client(self):
        return LLMClientFactory.get_client(
            provider=self.config.get("provider", "gemini"),
            api_key=self.config.get("api_key"),
            base_url=self.config.get("base_url"),
        )

    def invoke(self, contents: str, **kwargs) -> Dict[str, Any]:
        """调用 Layout Agent"""
        provider = self.config.get("provider", "gemini").lower()

        if provider == "gemini":
            # Gemini 客户端调用
            from google.genai import types

            if not hasattr(self.client, "models"):
                raise ValueError(f"Gemini Client {type(self.client)} does not have 'models' attribute")

            models = self.client.models
            if not hasattr(models, "generate_content"):
                raise ValueError(f"Gemini Models object {type(models)} does not have 'generate_content' method")

            response = models.generate_content(
                model=self.config["model"],
                contents=contents,
                config=types.GenerateContentConfig(response_mime_type=self.config["response_mime_type"]),
                **kwargs,
            )
            return response
        else:
            # OpenAI 兼容接口调用
            from openai import OpenAI

            if not isinstance(self.client, OpenAI):
                raise ValueError(f"Expected OpenAI client, got {type(self.client)}")

            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=[{"role": "user", "content": contents}],
                temperature=self.config.get("temperature", 0.1),
                response_format=(
                    {"type": "json_object"} if self.config.get("response_mime_type") == "application/json" else None
                ),
                **kwargs,
            )
            return response


def run_layout_agent(
    design_brief: Dict[str, Any],
    asset_list: Dict[str, Any],
    canvas_width: int,
    canvas_height: int,
    review_feedback: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    运行 Layout Agent

    Args:
        design_brief: 设计简报（仅包含设计决策：标题、颜色、风格等）
        asset_list: 资产列表
        canvas_width: 画布宽度（技术参数，从 AgentState 传入）
        canvas_height: 画布高度（技术参数，从 AgentState 传入）
        review_feedback: 审核反馈（可选，用于修正）

    Returns:
        海报 JSON 数据
    """
    logger.info("📐 Layout 正在计算布局坐标...")

    # 如果有审核反馈，记录日志方便调试
    if review_feedback:
        if review_feedback.get("status") == "REJECT":
            logger.info(f"📝 收到审核反馈（需要修正）: {review_feedback.get('feedback', '')}")
            if review_feedback.get("issues"):
                logger.info(f"📋 需要修正的问题: {', '.join(review_feedback.get('issues', []))}")
        else:
            logger.info("✅ 审核已通过，无需修正")

    try:
        # 使用配置化的 prompt（画布尺寸作为独立参数传入）
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
        logger.debug(f"📤 发送 Layout Prompt 到 LLM (长度: {len(prompt_content)} 字符)")
        logger.debug(f"📤 使用的模型: {agent.config.get('model', 'unknown')}")
        logger.debug(f"📤 使用的 Provider: {agent.config.get('provider', 'unknown')}")

        try:
            response = agent.invoke(contents=prompt_content)
            logger.debug("✅ Layout Agent LLM 调用成功，收到响应")
        except Exception as e:
            logger.error(f"❌ Layout Agent LLM 调用失败: {type(e).__name__}: {e}")

            if hasattr(e, "response"):
                logger.error(f"   响应状态码: {getattr(e.response, 'status_code', 'N/A')}")
                logger.error(f"   响应内容: {getattr(e.response, 'text', 'N/A')[:200]}")
            raise  # 重新抛出异常，让上层处理

        # 解析结果
        # 根据不同的客户端类型解析响应
        if hasattr(response, "text"):
            # Gemini 响应
            content = response.text
        elif hasattr(response, "choices") and len(response.choices) > 0:
            # OpenAI 兼容响应
            content = response.choices[0].message.content
        else:
            raise ValueError(f"Unknown response format: {type(response)}")

        # 清理可能存在的 markdown 标记
        if "```json" in content:
            content = content.replace("```json", "").replace("```", "")

        # 在解析 JSON 之前，先移除所有 base64 字符串（防止 JSON 被截断）
        # 使用正则表达式找到所有 "src": "data:image... 的字段，替换为占位符
        base64_pattern = r'"src":\s*"data:image[^"]*'
        content_cleaned = re.sub(base64_pattern, '"src": "{{PLACEHOLDER}}"', content)

        # 尝试解析 JSON
        try:
            poster_json = json.loads(content_cleaned)
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ JSON 解析失败，尝试修复: {e}")
            # 如果还是失败，尝试修复截断的 JSON
            content_fixed = _fix_truncated_json(content_cleaned, asset_list)
            try:
                poster_json = json.loads(content_fixed)
                logger.info("✅ JSON 修复成功")
            except json.JSONDecodeError as e2:
                logger.error(f"❌ JSON 修复失败: {e2}")
                logger.error(f"   原始内容前 500 字符: {content[:500]}")
                raise e  # 抛出原始错误

        # 修正 src 和验证图层位置
        # 优先使用 LLM 返回的画布尺寸，如果 LLM 没有返回或返回的值不一致，则使用传入的参数值
        # 确保 poster_json 中的 canvas 尺寸与传入的参数一致
        poster_canvas = poster_json.get("canvas", {})
        llm_canvas_width = poster_canvas.get("width")
        llm_canvas_height = poster_canvas.get("height")

        # 如果 LLM 返回了画布尺寸，使用 LLM 的值；否则使用传入的参数值
        final_canvas_width = llm_canvas_width if llm_canvas_width else canvas_width
        final_canvas_height = llm_canvas_height if llm_canvas_height else canvas_height

        # 确保 poster_json 中的 canvas 尺寸正确
        if "canvas" not in poster_json:
            poster_json["canvas"] = {}
        poster_json["canvas"]["width"] = final_canvas_width
        poster_json["canvas"]["height"] = final_canvas_height
        # 确保 backgroundColor 存在
        if "backgroundColor" not in poster_json["canvas"]:
            poster_json["canvas"]["backgroundColor"] = design_brief.get("background_color", "#FFFFFF")

        # 自动填充背景图 src（从 asset_list 获取，不依赖 LLM 返回）
        bg_layer = next((l for l in poster_json.get("layers", []) if l.get("id") == "bg"), None)
        if bg_layer:
            if asset_list.get("background_layer"):
                # 无论 LLM 返回什么，都使用 asset_list 中的 src
                old_src = bg_layer.get("src", "")
                new_src = asset_list["background_layer"].get("src", "")
                bg_layer["src"] = new_src
                logger.debug(f"🖼️ 背景图层 src 已自动填充:")
                if old_src and old_src != new_src:
                    logger.debug(f"   LLM 返回: {old_src[:50] if len(old_src) < 100 else 'base64字符串(已忽略)'}...")
                logger.debug(f"   实际使用: {new_src[:80] if new_src else 'None'}...")
            else:
                logger.warning("⚠️ 警告：asset_list 中没有 background_layer，背景图层 src 为空")
        else:
            logger.warning("⚠️ 警告：Layout Agent 没有生成背景图层 (id: bg)")

        # 自动填充前景图 src（从 asset_list 获取，不依赖 LLM 返回），并限制尺寸
        fg_layer = next(
            (l for l in poster_json.get("layers", []) if l.get("id") in ["person", "foreground"]),
            None,
        )
        if fg_layer:
            if asset_list.get("foreground_layer"):
                # 无论 LLM 返回什么，都使用 asset_list 中的 src
                old_src = fg_layer.get("src", "")
                new_src = asset_list["foreground_layer"].get("src", "")
                fg_layer["src"] = new_src
                logger.debug(f"🖼️ 前景图层 src 已自动填充:")
                logger.debug(
                    f"   LLM 返回: {old_src[:50] if old_src and len(old_src) < 100 else 'base64字符串(已忽略)'}..."
                )
                logger.debug(f"   实际使用: {new_src[:80] if new_src else 'None'}...")
            else:
                logger.warning("⚠️ 警告：asset_list 中没有 foreground_layer，前景图层 src 为空")

            # 限制前景图层尺寸，确保不会完全遮挡背景
            # 从 agent 的 config 中获取配置
            max_fg_width = int(final_canvas_width * agent.config["foreground_max_width_ratio"])
            max_fg_height = int(final_canvas_height * agent.config["foreground_max_height_ratio"])

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

                logger.info(
                    f"📏 前景图层尺寸过大 ({current_width}x{current_height})，自动缩小到 ({new_width}x{new_height})"
                )
                fg_layer["width"] = new_width
                fg_layer["height"] = new_height

        # 验证并修正图层位置，确保不超出画布范围
        for layer in poster_json.get("layers", []):
            # 确保图层有必要的属性
            if "x" not in layer:
                layer["x"] = 0
            if "y" not in layer:
                layer["y"] = 0
            if "width" not in layer or layer.get("width", 0) <= 0:
                logger.warning(f"⚠️ 图层 {layer.get('id', 'unknown')} 缺少 width 或 width <= 0，设置默认值")
                layer["width"] = 100 if layer.get("type") == "image" else 200
            if "height" not in layer or layer.get("height", 0) <= 0:
                logger.warning(f"⚠️ 图层 {layer.get('id', 'unknown')} 缺少 height 或 height <= 0，设置默认值")
                layer["height"] = 100 if layer.get("type") == "image" else 50

            # 确保位置 >= 0
            if layer.get("x", 0) < 0:
                layer["x"] = 0
            if layer.get("y", 0) < 0:
                layer["y"] = 0

            # 确保图层右边界不超出画布
            layer_width = layer.get("width", 0)
            layer_height = layer.get("height", 0)
            if layer.get("x", 0) + layer_width > final_canvas_width:
                layer["x"] = max(0, final_canvas_width - layer_width)
            if layer.get("y", 0) + layer_height > final_canvas_height:
                layer["y"] = max(0, final_canvas_height - layer_height)

            # 确保 z_index 存在
            if "z_index" not in layer:
                z_index_config = agent.config["z_index"]
                if layer.get("id") == "bg":
                    layer["z_index"] = z_index_config["background"]
                elif layer.get("id") in ["person", "foreground"]:
                    layer["z_index"] = z_index_config["foreground"]
                else:
                    layer["z_index"] = z_index_config["text"]

        logger.info(f"✅ Layout 完成，生成了 {len(poster_json.get('layers', []))} 个图层")

        # 记录最终的所有图层信息，方便调试
        logger.debug("📋 最终图层列表:")
        for layer in poster_json.get("layers", []):
            layer_type = layer.get("type", "unknown")
            layer_id = layer.get("id", "unknown")
            if layer_type == "image":
                src_preview = layer.get("src", "")[:100] if layer.get("src") else "None"
                logger.debug(f"  - {layer_id} ({layer_type}): src={src_preview}...")
            else:
                logger.debug(f"  - {layer_id} ({layer_type}): {layer.get('content', '')[:50]}...")

        return poster_json

    except json.JSONDecodeError as e:
        logger.error(f"❌ Layout JSON 解析失败: {e}")
        logger.error(f"   原始内容: {content[:500] if 'content' in locals() else 'N/A'}...")
        return settings.ERROR_FALLBACKS["layout"]
    except TimeoutError as e:
        logger.error(f"❌ Layout Agent 调用超时: {e}")
        return settings.ERROR_FALLBACKS["layout"]
    except Exception as e:
        logger.error(f"❌ Layout Error: {type(e).__name__}: {e}")
        # 记录详细错误方便调试
        import traceback

        logger.error(f"   错误堆栈:\n{traceback.format_exc()}")
        if hasattr(e, "response"):
            logger.error(f"   错误响应详情: {e.response}")

        return settings.ERROR_FALLBACKS["layout"]


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

    # 从 AgentState 中获取画布尺寸（技术参数，独立于 design_brief）
    canvas_width = state.get("canvas_width", settings.canvas.WIDTH)
    canvas_height = state.get("canvas_height", settings.canvas.HEIGHT)

    final_poster = run_layout_agent(
        design_brief=design_brief,
        asset_list=asset_list,
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        review_feedback=review_feedback,
    )

    return {"final_poster": final_poster}
