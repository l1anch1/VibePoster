"""
DSL 解析器 - 解析 Layout Agent 的 DSL 指令

职责：
1. 解析 DSL 指令列表
2. 实例化 layout 组件
3. 构建布局容器

Author: VibePoster Team
Date: 2025-01
"""

from typing import Dict, Any, List, Optional

from ...core.layout import (
    VerticalContainer,
    TextBlock,
    ImageBlock,
    Style,
    Element
)
from ...core.logger import get_logger

logger = get_logger(__name__)


class DSLParser:
    """
    DSL 解析器
    
    负责将 Layout Agent 输出的 DSL 指令转换为 OOP 布局组件
    """
    
    def __init__(self):
        self.container: Optional[VerticalContainer] = None
    
    def parse(
        self,
        dsl_instructions: List[Dict[str, Any]],
        canvas_width: int = 1080,
        canvas_height: int = 1920,
        design_brief: Optional[Dict[str, Any]] = None
    ) -> VerticalContainer:
        """
        解析 DSL 指令并构建 OOP 布局
        
        Args:
            dsl_instructions: Layout Agent 输出的 DSL 指令列表
            canvas_width: 画布宽度
            canvas_height: 画布高度
            design_brief: Planner 的设计简报
        
        Returns:
            布局容器
        """
        logger.info(f"🎨 开始解析 {len(dsl_instructions)} 条 DSL 指令...")
        
        # 创建主容器
        self.container = VerticalContainer(
            x=0,
            y=0,
            width=canvas_width,
            padding=40,
            gap=20
        )
        
        # 解析每条指令
        for i, instruction in enumerate(dsl_instructions):
            try:
                command = instruction.get("command")
                element = self._parse_instruction(instruction, design_brief)
                
                if element:
                    self.container.add(element)
                    logger.debug(f"  ✅ [{i+1}] {command} - 添加成功")
                else:
                    logger.warning(f"  ⚠️  [{i+1}] {command} - 无法解析，跳过")
            
            except Exception as e:
                logger.error(f"  ❌ [{i+1}] 解析指令失败: {e}")
                continue
        
        # 执行布局计算
        self.container.arrange()
        logger.info(f"✅ 布局计算完成，容器尺寸: {self.container.width} x {self.container.height:.1f}")
        
        return self.container
    
    def _parse_instruction(
        self,
        instruction: Dict[str, Any],
        design_brief: Optional[Dict[str, Any]] = None
    ) -> Optional[Element]:
        """解析单条 DSL 指令"""
        command = instruction.get("command")
        
        # 获取设计规范
        main_color = design_brief.get("main_color", "#000000") if design_brief else "#000000"
        
        # 解析不同的指令类型
        if command in ["add_title", "add_heading", "add_main_title"]:
            return self._create_text_block(
                content=instruction.get("content", "标题"),
                font_size=instruction.get("font_size", 48),
                color=instruction.get("color", main_color),
                font_weight="bold",
                text_align=instruction.get("text_align", "center")
            )
        
        elif command in ["add_subtitle", "add_subheading"]:
            return self._create_text_block(
                content=instruction.get("content", "副标题"),
                font_size=instruction.get("font_size", 32),
                color=instruction.get("color", "#666666"),
                font_weight="normal",
                text_align=instruction.get("text_align", "center")
            )
        
        elif command in ["add_text", "add_body_text", "add_description"]:
            return self._create_text_block(
                content=instruction.get("content", "正文"),
                font_size=instruction.get("font_size", 24),
                color=instruction.get("color", "#333333"),
                font_weight="normal",
                text_align=instruction.get("text_align", "left"),
                line_height=instruction.get("line_height", 1.6)
            )
        
        elif command in ["add_image", "add_hero_image", "add_background_image"]:
            return self._create_image_block(
                src=instruction.get("src", ""),
                width=instruction.get("width", 800),
                height=instruction.get("height", 600)
            )
        
        elif command in ["add_cta", "add_button_text"]:
            return self._create_text_block(
                content=instruction.get("content", "立即行动 →"),
                font_size=instruction.get("font_size", 28),
                color=instruction.get("color", "#0066FF"),
                font_weight="bold",
                text_align="center"
            )
        
        else:
            logger.warning(f"未知指令: {command}")
            return None
    
    def _create_text_block(
        self,
        content: str,
        font_size: int = 24,
        color: str = "#000000",
        font_weight: str = "normal",
        text_align: str = "left",
        line_height: float = 1.5
    ) -> TextBlock:
        """创建文本块"""
        max_width = self.container.width - 2 * self.container.padding if self.container else 800
        
        return TextBlock(
            content=content,
            font_size=font_size,
            max_width=max_width,
            line_height=line_height,
            style=Style(
                font_size=font_size,
                color=color,
                font_weight=font_weight,
                text_align=text_align
            )
        )
    
    def _create_image_block(
        self,
        src: str,
        width: int,
        height: int
    ) -> ImageBlock:
        """创建图片块"""
        max_width = self.container.width - 2 * self.container.padding if self.container else 800
        
        if width > max_width:
            scale = max_width / width
            width = int(max_width)
            height = int(height * scale)
        
        return ImageBlock(
            src=src,
            width=width,
            height=height,
            maintain_aspect_ratio=True
        )

