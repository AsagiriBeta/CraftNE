"""
API响应统一处理模块
"""

from flask import jsonify, request
from datetime import datetime
from typing import Any, Dict, Optional, Union
import uuid

class APIResponse:
    """API响应统一格式化类"""

    @staticmethod
    def success(data: Any = None, message: str = "操作成功", code: str = "SUCCESS") -> Dict:
        """成功响应"""
        response = {
            "success": True,
            "code": code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": getattr(request, 'request_id', str(uuid.uuid4())[:8])
        }

        if data is not None:
            response["data"] = data

        return response

    @staticmethod
    def error(message: str, code: str = "ERROR", details: Any = None, status_code: int = 400) -> tuple:
        """错误响应"""
        response = {
            "success": False,
            "code": code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": getattr(request, 'request_id', str(uuid.uuid4())[:8])
        }

        if details is not None:
            response["details"] = details

        return response, status_code

    @staticmethod
    def paginated(data: list, page: int, per_page: int, total: int,
                  message: str = "获取成功") -> Dict:
        """分页响应"""
        total_pages = (total + per_page - 1) // per_page

        return APIResponse.success({
            "items": data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }, message)

    @staticmethod
    def created(data: Any = None, message: str = "创建成功") -> tuple:
        """创建成功响应"""
        return APIResponse.success(data, message, "CREATED"), 201

    @staticmethod
    def not_found(message: str = "资源未找到", code: str = "NOT_FOUND") -> tuple:
        """404响应"""
        return APIResponse.error(message, code, status_code=404)

    @staticmethod
    def validation_error(message: str = "数据验证失败", details: Any = None) -> tuple:
        """验证错误响应"""
        return APIResponse.error(message, "VALIDATION_ERROR", details, 400)

    @staticmethod
    def forbidden(message: str = "权限不足") -> tuple:
        """权限不足响应"""
        return APIResponse.error(message, "FORBIDDEN", status_code=403)

    @staticmethod
    def internal_error(message: str = "服务器内部错误") -> tuple:
        """服务器错误响应"""
        return APIResponse.error(message, "INTERNAL_ERROR", status_code=500)

def make_json_response(data_or_response, status_code=200):
    """创建JSON响应"""
    if isinstance(data_or_response, tuple):
        data, status_code = data_or_response
        return jsonify(data), status_code
    else:
        return jsonify(data_or_response), status_code
