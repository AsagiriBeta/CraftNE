"""
实用装饰器模块
"""

import time
import functools
from flask import jsonify, request, current_app
from app.utils.logging_config import log_performance, log_user_action, log_error

def monitor_performance(operation_name=None):
    """性能监控装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            operation = operation_name or f"{func.__module__}.{func.__name__}"

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # 记录性能日志
                extra_data = {
                    'function': func.__name__,
                    'args_count': len(args),
                    'kwargs_count': len(kwargs)
                }
                log_performance(operation, duration, extra_data)

                return result

            except Exception as e:
                duration = time.time() - start_time
                log_error(e, context=f"性能监控中的错误 - 操作: {operation}, 耗时: {duration:.3f}s")
                raise

        return wrapper
    return decorator

def validate_json_request(required_fields=None):
    """JSON请求验证装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': '请求必须是JSON格式',
                    'code': 'INVALID_CONTENT_TYPE'
                }), 400

            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'JSON数据为空',
                    'code': 'EMPTY_JSON'
                }), 400

            # 检查必需字段
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return jsonify({
                        'success': False,
                        'error': f'缺少必需字段: {", ".join(missing_fields)}',
                        'code': 'MISSING_FIELDS',
                        'missing_fields': missing_fields
                    }), 400

            return func(*args, **kwargs)
        return wrapper
    return decorator

def log_user_activity(action_name=None):
    """用户活动记录装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            action = action_name or f"{func.__name__}"

            # 收集请求信息
            extra_data = {
                'function': func.__name__,
                'method': request.method,
                'endpoint': request.endpoint,
                'user_agent': request.headers.get('User-Agent', '')[:100]  # 截断长用户代理
            }

            # 对于POST请求，记录一些基本信息（避免敏感数据）
            if request.method == 'POST' and request.is_json:
                json_data = request.get_json()
                if json_data:
                    # 只记录非敏感的键
                    safe_keys = ['filename', 'map_id', 'annotation_type', 'action_type']
                    extra_data['request_data'] = {
                        k: v for k, v in json_data.items()
                        if k in safe_keys and len(str(v)) < 100
                    }

            log_user_action(action, extra_data=extra_data)

            return func(*args, **kwargs)
        return wrapper
    return decorator

def handle_exceptions(default_message="操作失败"):
    """异常处理装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValueError as e:
                return jsonify({
                    'success': False,
                    'error': str(e) or default_message,
                    'code': 'VALIDATION_ERROR'
                }), 400
            except FileNotFoundError as e:
                return jsonify({
                    'success': False,
                    'error': '文件未找到',
                    'code': 'FILE_NOT_FOUND'
                }), 404
            except PermissionError as e:
                return jsonify({
                    'success': False,
                    'error': '权限不足',
                    'code': 'PERMISSION_DENIED'
                }), 403
            except Exception as e:
                log_error(e, context=f"未处理异常在函数 {func.__name__}")
                return jsonify({
                    'success': False,
                    'error': default_message,
                    'code': 'INTERNAL_ERROR'
                }), 500
        return wrapper
    return decorator

def api_response():
    """API响应标准��装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)

                # 如果返回的是tuple（response, status_code），处理它
                if isinstance(result, tuple):
                    data, status_code = result
                    if isinstance(data, dict) and 'success' not in data:
                        data['success'] = 200 <= status_code < 300
                    return jsonify(data), status_code

                # 如果返回的是dict，包装成标准响应
                elif isinstance(result, dict):
                    if 'success' not in result:
                        result['success'] = True
                    return jsonify(result)

                # 其他情况直接返回
                return result

            except Exception as e:
                log_error(e, context=f"API响应处理错误在函数 {func.__name__}")
                return jsonify({
                    'success': False,
                    'error': '处理请求时发生错误',
                    'code': 'PROCESSING_ERROR'
                }), 500

        return wrapper
    return decorator

def require_file_upload(allowed_extensions=None):
    """文件上传验证装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if 'file' not in request.files:
                return jsonify({
                    'success': False,
                    'error': '没有上传文件',
                    'code': 'NO_FILE'
                }), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': '未选择文件',
                    'code': 'EMPTY_FILENAME'
                }), 400

            # 检查文件扩展名
            if allowed_extensions:
                file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                if file_ext not in allowed_extensions:
                    return jsonify({
                        'success': False,
                        'error': f'不支持的文件类型。支持的类型: {", ".join(allowed_extensions)}',
                        'code': 'INVALID_FILE_TYPE',
                        'allowed_extensions': allowed_extensions
                    }), 415

            return func(*args, **kwargs)
        return wrapper
    return decorator
