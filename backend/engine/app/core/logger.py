"""
统一日志系统 - 配置和管理日志
"""
import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    设置并返回一个配置好的 logger
    
    Args:
        name: logger 名称（通常是模块名，如 __name__）
        level: 日志级别（默认 INFO）
        log_file: 日志文件路径（可选，如果不提供则只输出到控制台）
        format_string: 日志格式字符串（可选，使用默认格式）
        
    Returns:
        配置好的 logger 实例
    """
    logger = logging.getLogger(name)
    
    # 避免重复添加 handler
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # 默认格式：时间戳 - 级别 - 模块名 - 消息
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    formatter = logging.Formatter(format_string, datefmt="%Y-%m-%d %H:%M:%S")
    
    # 控制台输出 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件输出 handler（如果指定了日志文件）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取一个 logger 实例（便捷函数）
    
    Args:
        name: logger 名称（通常是 __name__）
        
    Returns:
        logger 实例
    """
    return setup_logger(name)


# 默认 logger（用于快速日志记录）
default_logger = get_logger("vibeposter")

# 别名：方便其他模块导入
logger = default_logger

