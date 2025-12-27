"""
视觉处理工具 - 抠图、图像分析 (RMBG/Pillow)
负责底层的图像处理，不涉及决策，只干活
"""
from typing import Dict, Any, Optional
import base64
import io
import tempfile
import os
from PIL import Image
import numpy as np

# 尝试导入 rembg，如果失败则使用占位实现
try:
    from rembg import remove
    REMBG_AVAILABLE = True
    print("✅ rembg 已启用，抠图功能可用")
except ImportError:
    REMBG_AVAILABLE = False
    print("⚠️ rembg 未安装，抠图功能将使用占位实现")


def remove_background(image_data: bytes) -> bytes:
    """
    移除背景（抠图）
    
    Args:
        image_data: 图片二进制数据
        
    Returns:
        处理后的透明 PNG 二进制数据
    """
    if REMBG_AVAILABLE:
        try:
            # 使用 rembg 抠图
            output = remove(image_data)
            return output
        except Exception as e:
            print(f"❌ 抠图失败: {e}")
            # 如果失败，返回原图
            return image_data
    else:
        # 占位实现：返回原图（仅在 rembg 未安装时使用）
        print("⚠️ rembg 未安装，返回原图")
        return image_data


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
        print(f"❌ 图像分析失败: {e}")
        # 返回默认值
        return {
            "width": 1080,
            "height": 1920,
            "main_color": "#000000",
            "subject_bbox": None,
        }


def process_cutout(image_data: bytes) -> Dict[str, Any]:
    """
    处理抠图：输入图片 -> 输出透明 PNG 和分析结果
    
    Args:
        image_data: 图片二进制数据
        
    Returns:
        包含处理后的图片和分析结果的字典
    """
    # 抠图
    processed_image = remove_background(image_data)
    
    # 分析原图（用于获取尺寸等信息）
    analysis = analyze_image(image_data)
    
    # 转换为 Base64
    processed_base64 = image_to_base64(processed_image, "image/png")
    
    # 保存到临时文件（可选）
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            tmp_file.write(processed_image)
            temp_path = tmp_file.name
    except Exception as e:
        print(f"⚠️ 保存临时文件失败: {e}")
    
    return {
        "processed_image_path": temp_path,
        "processed_image_base64": processed_base64,
        "width": analysis["width"],
        "height": analysis["height"],
        "main_color": analysis["main_color"],
        "subject_bbox": analysis["subject_bbox"],
    }


def composite_images(foreground: bytes, background: bytes, position: tuple = None) -> bytes:
    """
    图像合成：将前景图合成到背景图上
    
    Args:
        foreground: 前景图（已抠图，透明 PNG）
        background: 背景图
        position: 合成位置 (x, y)，如果为 None 则居中
        
    Returns:
        合成后的图片二进制数据
    """
    try:
        # 打开图片
        fg_img = Image.open(io.BytesIO(foreground))
        bg_img = Image.open(io.BytesIO(background))
        
        # 确保背景图是 RGB
        if bg_img.mode != 'RGB':
            bg_img = bg_img.convert('RGB')
        
        # 计算位置
        if position is None:
            # 居中
            x = (bg_img.width - fg_img.width) // 2
            y = (bg_img.height - fg_img.height) // 2
        else:
            x, y = position
        
        # 合成
        bg_img.paste(fg_img, (x, y), fg_img if fg_img.mode == 'RGBA' else None)
        
        # 转换为字节
        output = io.BytesIO()
        bg_img.save(output, format='PNG')
        return output.getvalue()
    except Exception as e:
        print(f"❌ 图像合成失败: {e}")
        return background


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
