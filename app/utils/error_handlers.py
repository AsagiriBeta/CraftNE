"""
错误处理模块
"""

from flask import render_template, request, jsonify, current_app
from app.utils.logging_config import log_error
import traceback

def register_error_handlers(app):
    """注册全局错误处理器"""

    @app.errorhandler(404)
    def not_found_error(error):
        """404错误处理"""
        if request.path.startswith('/api/'):
            return jsonify({'error': '资源未找到', 'code': 404}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """500错误处理"""
        from app import db
        db.session.rollback()
        log_error(error, context=f"请求: {request.url}")
        if request.path.startswith('/api/'):
            return jsonify({'error': '服务器内部错误', 'code': 500}), 500
        return render_template('errors/500.html'), 500

    @app.errorhandler(413)
    def file_too_large(error):
        """文件过大错误处理"""
        if request.path.startswith('/api/'):
            return jsonify({'error': '上传文件过大', 'code': 413}), 413
        return render_template('errors/413.html'), 413

    @app.errorhandler(400)
    def bad_request(error):
        """400错误处理"""
        if request.path.startswith('/api/'):
            return jsonify({'error': '请求格式错误', 'code': 400}), 400
        return render_template('errors/400.html'), 400

    @app.errorhandler(415)
    def unsupported_media_type(error):
        """不支持的文件类型"""
        if request.path.startswith('/api/'):
            return jsonify({'error': '不支持的文件���型', 'code': 415}), 415
        return render_template('errors/415.html'), 415

    @app.errorhandler(Exception)
    def handle_exception(error):
        """处理未捕获的异常"""
        from app import db
        db.session.rollback()
        error_details = {
            'error': str(error),
            'type': type(error).__name__,
            'traceback': traceback.format_exc() if current_app.debug else None
        }
        log_error(error, context=f"未处理异常: {request.url}", extra_data=error_details)

        if request.path.startswith('/api/'):
            return jsonify({
                'error': '系统错误',
                'code': 500,
                'details': error_details if current_app.debug else None
            }), 500
        return render_template('errors/500.html'), 500
