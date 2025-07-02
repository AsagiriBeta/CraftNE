"""
日志配置模块
"""

import logging
import logging.handlers
import os
from datetime import datetime
from flask import current_app, request, g
import json
import traceback

def setup_logging(app):
    """设置应用日志配置"""

    # 创建日志目录
    log_dir = os.path.join(app.instance_path, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s [%(name)s] %(filename)s:%(lineno)d - %(message)s'
    )

    # 应用日志处理器
    app_log_file = os.path.join(log_dir, 'app.log')
    app_handler = logging.handlers.RotatingFileHandler(
        app_log_file, maxBytes=10240000, backupCount=10, encoding='utf-8'
    )
    app_handler.setFormatter(formatter)
    app_handler.setLevel(logging.INFO)

    # 错误日志处理器
    error_log_file = os.path.join(log_dir, 'error.log')
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file, maxBytes=10240000, backupCount=10, encoding='utf-8'
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)

    # 调试日志处理器（仅在调试模式下）
    if app.debug:
        debug_log_file = os.path.join(log_dir, 'debug.log')
        debug_handler = logging.handlers.RotatingFileHandler(
            debug_log_file, maxBytes=10240000, backupCount=5, encoding='utf-8'
        )
        debug_handler.setFormatter(formatter)
        debug_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(debug_handler)

    # 添加处理器到应用日志器
    app.logger.addHandler(app_handler)
    app.logger.addHandler(error_handler)

    # 设置日志级别
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)

    # 禁用Werkzeug的默认日志
    if not app.debug:
        logging.getLogger('werkzeug').setLevel(logging.WARNING)

def log_error(error, context=None, extra_data=None):
    """记录错误日志"""
    try:
        error_info = {
            'timestamp': datetime.utcnow().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'traceback': traceback.format_exc(),
        }

        if hasattr(request, 'url'):
            error_info.update({
                'url': request.url,
                'method': request.method,
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
            })

        if extra_data:
            error_info['extra_data'] = extra_data

        current_app.logger.error(f"错误详情: {json.dumps(error_info, ensure_ascii=False, indent=2)}")

    except Exception as log_error:
        # 如果日志记录本身出错，使用基本的日志记录
        current_app.logger.error(f"日志记录失败: {str(log_error)} | 原始错误: {str(error)}")

def log_info(message, extra_data=None):
    """记录信息日志"""
    try:
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'message': message,
        }

        if extra_data:
            log_data['data'] = extra_data

        current_app.logger.info(json.dumps(log_data, ensure_ascii=False))

    except Exception as e:
        current_app.logger.info(f"日志数据序列化失败: {str(e)} | 消息: {message}")

def log_performance(operation, duration, extra_data=None):
    """记录性能日志"""
    try:
        perf_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'operation': operation,
            'duration_ms': round(duration * 1000, 2),
            'url': request.url if hasattr(request, 'url') else None,
        }

        if extra_data:
            perf_data['data'] = extra_data

        current_app.logger.info(f"性能: {json.dumps(perf_data, ensure_ascii=False)}")

    except Exception as e:
        current_app.logger.info(f"性能日志记录失败: {str(e)} | 操作: {operation}")

def log_user_action(action, user_id=None, extra_data=None):
    """记录用户操作日志"""
    try:
        action_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'action': action,
            'user_id': user_id or getattr(g, 'user_id', None),
            'ip': request.remote_addr if hasattr(request, 'remote_addr') else None,
            'url': request.url if hasattr(request, 'url') else None,
        }

        if extra_data:
            action_data['data'] = extra_data

        current_app.logger.info(f"用户操作: {json.dumps(action_data, ensure_ascii=False)}")

    except Exception as e:
        current_app.logger.info(f"用户操作日志记录失败: {str(e)} | 操作: {action}")
