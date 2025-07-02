"""
Celery配置模块
"""

from celery import Celery
from config.config import Config
import os

def make_celery(app):
    """创建Celery实例"""
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )

    # 更新Celery配置
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='Asia/Shanghai',
        enable_utc=True,
        task_track_started=True,
        task_time_limit=30 * 60,  # 30分钟超时
        task_soft_time_limit=25 * 60,  # 25分钟软超时
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=100,
        result_expires=3600,  # 结果保存1小时

        # 任务路由
        task_routes={
            'app.tasks.mca_parsing.*': {'queue': 'parsing'},
            'app.tasks.model_training.*': {'queue': 'training'},
            'app.tasks.map_generation.*': {'queue': 'generation'},
            'app.tasks.system.*': {'queue': 'system'}
        },

        # 队列定义
        task_default_queue='default',
        task_default_exchange='default',
        task_default_exchange_type='direct',
        task_default_routing_key='default',
    )

    class ContextTask(celery.Task):
        """包含Flask应用上下文的任务基类"""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
