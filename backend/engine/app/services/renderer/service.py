"""
渲染服务 - 统一入口

职责：
1. 协调 DSL 解析和 Schema 转换
2. 提供完整的渲染流程
3. 便捷方法

Author: VibePoster Team
Date: 2025-01
"""

from typing import Dict, Any, List, Optional

from ...models.poster import PosterData, Canvas
from ...core.layout import VerticalContainer
from ...core.logger import get_logger
from .dsl_parser import DSLParser
from .schema_converter import SchemaConverter

logger = get_logger(__name__)


class RendererService:
    """
    渲染服务 - 统一入口
    
    将 DSL 解析和 Schema 转换整合为一个简单的接口
    """
    
    def __init__(self):
        self.dsl_parser = DSLParser()
        self.schema_converter = SchemaConverter()
    
    def parse_dsl_and_build_layout(
        self,
        dsl_instructions: List[Dict[str, Any]],
        canvas_width: int = 1080,
        canvas_height: int = 1920,
        design_brief: Optional[Dict[str, Any]] = None
    ) -> VerticalContainer:
        """解析 DSL 指令并构建 OOP 布局"""
        return self.dsl_parser.parse(
            dsl_instructions=dsl_instructions,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            design_brief=design_brief
        )
    
    def convert_to_pydantic_schema(
        self,
        container: Optional[VerticalContainer] = None,
        design_brief: Optional[Dict[str, Any]] = None
    ) -> PosterData:
        """将 OOP 布局引擎的输出转换为 Pydantic Schema"""
        if container is None:
            container = self.dsl_parser.container
        
        if container is None:
            raise ValueError("容器未初始化，请先调用 parse_dsl_and_build_layout")
        
        return self.schema_converter.convert(container, design_brief)
    
    def merge_with_design_brief(
        self,
        poster_data: PosterData,
        design_brief: Dict[str, Any],
        asset_list: Optional[Dict[str, Any]] = None
    ) -> PosterData:
        """合并设计数据"""
        return self.schema_converter.merge_with_design_brief(
            poster_data, design_brief, asset_list
        )
    
    def render_poster_from_workflow_state(
        self,
        workflow_state: Dict[str, Any]
    ) -> PosterData:
        """
        从工作流状态直接渲染海报（完整流程）
        
        Args:
            workflow_state: 工作流状态字典
        
        Returns:
            最终的 PosterData
        """
        logger.info("=" * 80)
        logger.info("🎨 开始完整渲染流程")
        logger.info("=" * 80)
        
        # 1. 提取数据
        design_brief = workflow_state.get("design_brief", {})
        asset_list = workflow_state.get("asset_list")
        final_poster = workflow_state.get("final_poster", {})
        canvas_width = workflow_state.get("canvas_width", 1080)
        canvas_height = workflow_state.get("canvas_height", 1920)
        
        # 2. 获取 DSL 指令
        dsl_instructions = final_poster.get("dsl_instructions", [])
        
        # 如果没有 DSL 指令，尝试直接使用 layers
        if not dsl_instructions and "layers" in final_poster:
            logger.info("⚠️  未找到 DSL 指令，直接使用 layers 数据")
            canvas = Canvas(
                width=canvas_width,
                height=canvas_height,
                backgroundColor=design_brief.get("background_color", "#FFFFFF")
            )
            return PosterData(
                canvas=canvas,
                layers=final_poster["layers"]
            )
        
        # 3. 解析 DSL 并构建布局
        container = self.parse_dsl_and_build_layout(
            dsl_instructions=dsl_instructions,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            design_brief=design_brief
        )
        
        # 4. 转换为 Pydantic Schema
        poster_data = self.convert_to_pydantic_schema(
            container=container,
            design_brief=design_brief
        )
        
        # 5. 合并设计数据
        poster_data = self.merge_with_design_brief(
            poster_data=poster_data,
            design_brief=design_brief,
            asset_list=asset_list
        )
        
        logger.info("=" * 80)
        logger.info(f"✅ 渲染完成！海报尺寸: {poster_data.canvas.width} x {poster_data.canvas.height}")
        logger.info(f"   共 {len(poster_data.layers)} 个图层")
        logger.info("=" * 80)
        
        return poster_data


def create_simple_poster_from_text(
    title: str,
    subtitle: Optional[str] = None,
    image_url: Optional[str] = None,
    canvas_width: int = 1080,
    canvas_height: int = 1920
) -> PosterData:
    """
    快速创建简单海报（无需 DSL）
    
    Args:
        title: 标题文本
        subtitle: 副标题（可选）
        image_url: 图片 URL（可选）
        canvas_width: 画布宽度
        canvas_height: 画布高度
    
    Returns:
        PosterData 对象
    """
    renderer = RendererService()
    
    # 构建 DSL 指令
    instructions = [
        {"command": "add_title", "content": title, "font_size": 48}
    ]
    
    if subtitle:
        instructions.append({
            "command": "add_subtitle",
            "content": subtitle,
            "font_size": 32
        })
    
    if image_url:
        instructions.append({
            "command": "add_image",
            "src": image_url,
            "width": 800,
            "height": 600
        })
    
    # 渲染
    container = renderer.parse_dsl_and_build_layout(
        dsl_instructions=instructions,
        canvas_width=canvas_width,
        canvas_height=canvas_height
    )
    
    return renderer.convert_to_pydantic_schema(container)

