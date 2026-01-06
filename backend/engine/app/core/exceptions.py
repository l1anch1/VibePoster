"""
自定义异常类定义
用于业务逻辑层的错误处理
"""
from typing import Optional, Dict, Any


class VibePosterException(Exception):
    """基础异常类"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        detail: Optional[Dict[str, Any]] = None
    ):
        """
        初始化异常
        
        Args:
            message: 错误消息
            status_code: HTTP 状态码
            detail: 错误详情（可选）
        """
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(self.message)


class ValidationException(VibePosterException):
    """参数验证异常（400）"""
    
    def __init__(self, message: str = "请求参数错误", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, detail=detail)


class NotFoundException(VibePosterException):
    """资源未找到异常（404）"""
    
    def __init__(self, message: str = "资源未找到", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=404, detail=detail)


class ServiceException(VibePosterException):
    """服务层异常（500）"""
    
    def __init__(self, message: str = "服务器内部错误", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, detail=detail)


class WorkflowException(VibePosterException):
    """工作流异常（500）"""
    
    def __init__(self, message: str = "工作流执行失败", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, detail=detail)

