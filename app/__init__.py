"""
CraftNE应用工厂
"""

from flask import Flask, request, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config.config import Config
from app.utils.logging_config import setup_logging
from app.utils.error_handlers import register_error_handlers
from app.utils.cache import cache_manager
import os
import uuid
import time

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    """创建Flask应用实例"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 设置日志系统
    setup_logging(app)

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    cache_manager.init_app(app)

    # 注册错误处理器
    register_error_handlers(app)

    # 请求处理中间件
    @app.before_request
    def before_request():
        """请求前处理"""
        # 生成请求ID用于追踪
        request.request_id = str(uuid.uuid4())[:8]
        g.request_start_time = time.time()

        # 记录请求信息
        if not request.path.startswith('/static/'):
            app.logger.info(f"请求开始: {request.method} {request.path} [ID: {request.request_id}]")

    @app.after_request
    def after_request(response):
        """请求后处理"""
        if hasattr(g, 'request_start_time'):
            duration = time.time() - g.request_start_time
            app.logger.info(
                f"请求完成: {request.method} {request.path} "
                f"[ID: {getattr(request, 'request_id', 'unknown')}] "
                f"状态: {response.status_code} 耗时: {duration:.3f}s"
            )
        return response

    # 注册蓝图
    from app.views.main import bp as main_bp
    from app.views.upload import bp as upload_bp
    from app.views.annotation import bp as annotation_bp
    from app.views.generation import bp as generation_bp
    from app.views.api import bp as api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(upload_bp, url_prefix='/upload')
    app.register_blueprint(annotation_bp, url_prefix='/annotation')
    app.register_blueprint(generation_bp, url_prefix='/generation')
    app.register_blueprint(api_bp, url_prefix='/api')

    # 创建必要目录
    directories = [
        app.config['UPLOAD_FOLDER'],
        app.config.get('MODEL_CACHE_DIR', 'models_cache'),
        app.config.get('TRAINING_DATA_DIR', 'training_data'),
        os.path.join(app.instance_path, 'logs'),
        os.path.join(app.instance_path, 'cache')
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    app.logger.info("CraftNE应用初始化完成")
    return app

# 导入模型（放在最后避免循环导入）
from app import models