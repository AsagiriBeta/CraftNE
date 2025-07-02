#!/usr/bin/env python3
"""
Celery Worker配置文件
用于处理异步任务，如MCA文件解��和AI模型训练
"""

from app import create_app
from celery import Celery

def make_celery(app):
    """创建Celery实例"""
    celery = Celery(
        app.import_name,
        backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        broker=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    )

    # 更新配置
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        """确保任务在Flask应用上下文中运行"""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

# 创建Flask应用和Celery实例
app = create_app()
celery = make_celery(app)

# 导入任务模块以注册任务
from app import tasks

if __name__ == '__main__':
    celery.start()
