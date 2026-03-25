"""
视觉处理工具 — 图像分析、合成、编码
负责底层的图像处理，不涉及决策，只干活
"""
from typing import Dict, Any, Optional
import base64
import io
from PIL import Image
import numpy as np
from ..core.logger import get_logger

logger = get_logger(__name__)


def analyze_image(image_data: bytes) -> Dict[str, Any]:
    """
    图像分析：获取宽高、主色调、主体 Bounding Box
    
    Args:
        image_data: 图片二进制数据
        
    Returns:
        图像分析结果
    """
    try:
        # 打开图片
        img = Image.open(io.BytesIO(image_data))
        width, height = img.size
        
        # 转换为 RGB（如果是 RGBA）
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 计算主色调（使用 K-means 简化版：取平均值）
        img_array = np.array(img)
        # 计算所有像素的平均颜色
        avg_color = img_array.mean(axis=(0, 1))
        main_color = f"#{int(avg_color[0]):02X}{int(avg_color[1]):02X}{int(avg_color[2]):02X}"
        
        # 简单的主体检测（占位实现）
        # TODO: 使用更高级的检测算法（如 YOLO、MediaPipe 等）
        # 这里假设主体在中心区域
        subject_bbox = None
        if width > 0 and height > 0:
            # 假设主体占据中心 60% 的区域
            margin_x = int(width * 0.2)
            margin_y = int(height * 0.2)
            subject_bbox = [
                margin_x,
                margin_y,
                width - margin_x,
                height - margin_y
            ]
        
        return {
            "width": width,
            "height": height,
            "main_color": main_color,
            "subject_bbox": subject_bbox,
        }
    except Exception as e:
        logger.error(f"❌ 图像分析失败: {e}")
        # 返回默认值
        return {
            "width": 1080,
            "height": 1920,
            "main_color": "#000000",
            "subject_bbox": None,
        }


def image_to_base64(image_data: bytes, mime_type: str = "image/png") -> str:
    """
    将图片转换为 Base64 字符串
    
    Args:
        image_data: 图片二进制数据
        mime_type: MIME 类型
        
    Returns:
        Base64 字符串
    """
    b64_img = base64.b64encode(image_data).decode("utf-8")
    return f"data:{mime_type};base64,{b64_img}"
