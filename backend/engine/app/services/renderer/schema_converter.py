"""
Schema 转换器 - OOP 布局到 Pydantic Schema 的转换

职责：
1. 将布局元素转换为 Pydantic 图层
2. 创建 PosterData 对象
3. 合并设计数据

Author: VibePoster Team
Date: 2025-01
"""

from typing import Dict, Any, List, Optional, Union

from ...models.poster import (
    PosterData,
    Canvas,
    TextLayer,
    ImageLayer,
    ShapeLayer
)
from ...core.layout import VerticalContainer
from ...core.logger import get_logger

logger = get_logger(__name__)


class SchemaConverter:
    """
    Schema 转换器
    
    负责将 OOP 布局引擎的输出转换为 Pydantic Schema
    """
    
    def convert(
        self,
        container: VerticalContainer,
        design_brief: Optional[Dict[str, Any]] = None
    ) -> PosterData:
        """
        将 OOP 布局引擎的输出转换为 Pydantic Schema
        
        Args:
            container: 布局容器
            design_brief: 设计简报
        
        Returns:
            PosterData 对象
        """
        logger.info("🔄 开始转换为 Pydantic Schema...")
        
        # 获取所有元素
        raw_elements = container.get_all_elements()
        
        # 转换为 Pydantic 图层
        layers: List[Union[TextLayer, ImageLayer, ShapeLayer]] = []
        
        for i, elem in enumerate(raw_elements):
            try:
                layer = self._convert_element_to_layer(elem, i)
                if layer:
                    layers.append(layer)
            except Exception as e:
                logger.error(f"转换图层 {i} 失败: {e}")
                continue
        
        # 创建画布配置
        bg_color = design_brief.get("background_color", "#FFFFFF") if design_brief else "#FFFFFF"
        canvas = Canvas(
            width=int(container.width),
            height=int(container.height),
            backgroundColor=bg_color
        )
        
        # 创建 PosterData
        poster_data = PosterData(
            canvas=canvas,
            layers=layers
        )
        
        logger.info(f"✅ 转换完成，共 {len(layers)} 个图层")
        return poster_data
    
    def _convert_element_to_layer(
        self,
        elem: Dict[str, Any],
        index: int
    ) -> Optional[Union[TextLayer, ImageLayer, ShapeLayer]]:
        """将单个元素转换为 Pydantic 图层"""
        elem_type = elem.get("type")
        
        # 生成图层 ID
        layer_id = f"{elem_type}_{index}"
        
        # 基础属性
        base_attrs = {
            "id": layer_id,
            "name": f"{elem_type.capitalize()} {index}",
            "type": elem_type,
            "x": int(elem.get("x", 0)),
            "y": int(elem.get("y", 0)),
            "width": int(elem.get("width", 0)),
            "height": int(elem.get("height", 0)),
            "rotation": int(elem.get("rotation", 0)),
            "opacity": float(elem.get("opacity", 1.0)),
            "z_index": int(elem.get("z_index", index))
        }
        
        # 根据类型创建对应的图层
        if elem_type == "text":
            return TextLayer(
                **base_attrs,
                content=elem.get("content", ""),
                fontSize=int(elem.get("fontSize", 24)),
                color=elem.get("color", "#000000"),
                fontFamily=elem.get("fontFamily", "Arial"),
                textAlign=elem.get("textAlign", "left"),
                fontWeight=elem.get("fontWeight", "normal")
            )
        
        elif elem_type == "image":
            return ImageLayer(
                **base_attrs,
                src=elem.get("src", "")
            )
        
        elif elem_type == "rect":
            return ShapeLayer(
                **base_attrs,
                backgroundColor=elem.get("backgroundColor", "transparent")
            )
        
        else:
            logger.warning(f"未知的元素类型: {elem_type}")
            return None
    
    def merge_with_design_brief(
        self,
        poster_data: PosterData,
        design_brief: Dict[str, Any],
        asset_list: Optional[Dict[str, Any]] = None
    ) -> PosterData:
        """
        合并 Planner 的设计简报和 Layout 的坐标数据
        
        Args:
            poster_data: 已计算好坐标的海报数据
            design_brief: Planner 的设计简报
            asset_list: Visual Agent 的素材列表
        
        Returns:
            最终完整的海报数据
        """
        logger.info("🔗 开始合并设计数据...")
        
        # 更新画布背景色
        if "background_color" in design_brief:
            poster_data.canvas.backgroundColor = design_brief["background_color"]
        
        # 遍历图层，填充缺失的数据
        for layer in poster_data.layers:
            if layer.type == "text":
                if "main_color" in design_brief and "标题" in layer.name:
                    layer.color = design_brief["main_color"]
                
                if not layer.content and "title" in design_brief:
                    layer.content = design_brief["title"]
            
            elif layer.type == "image":
                if asset_list and not layer.src:
                    if "background_layer" in asset_list:
                        layer.src = asset_list["background_layer"].get("src", "")
                    elif "foreground_layer" in asset_list:
                        layer.src = asset_list["foreground_layer"].get("src", "")
        
        logger.info("✅ 数据合并完成")
        return poster_data

