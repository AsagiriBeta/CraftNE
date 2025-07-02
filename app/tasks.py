"""
异步任务模块
"""

from celery import current_app
import time
import traceback
from datetime import datetime, timezone

# 获取当前的Celery实例
celery = current_app

@celery.task(bind=True)
def parse_mca_file_task(self, map_data_id):
    """异步解析MCA文件任务"""
    try:
        from app import db, create_app
        from app.models.map_data import MapData
        from app.services.mca_parser import MCAParser
        from app.utils.logging_config import log_info, log_error

        # 更新任务状态
        self.update_state(state='PROGRESS', meta={'step': '开始解析', 'progress': 0})

        # 获取地图数据
        map_data = MapData.query.get(map_data_id)
        if not map_data:
            raise ValueError(f"地图数据 {map_data_id} 不存在")

        # 更新地图状态
        map_data.parse_status = 'parsing'
        map_data.parse_progress = 0.0
        db.session.commit()

        # 创建��析器
        parser = MCAParser()

        # 更新进度
        self.update_state(state='PROGRESS', meta={'step': '开始解析MCA文件', 'progress': 20})

        # 解析文件
        result = parser.parse_file(map_data.file_path, map_data_id)

        if result.get('success', False):
            # 解析成功
            map_data.parse_status = 'completed'
            map_data.is_parsed = True
            map_data.parse_progress = 100.0
            map_data.parsed_at = datetime.now(timezone.utc)

            # 保存解析结果
            if 'blocks_data' in result:
                map_data.blocks_data = result['blocks_data']
            if 'statistics' in result:
                map_data.statistics = result['statistics']

            db.session.commit()

            log_info(f"MCA文件解析完成: {map_data.filename}")

            return {
                'success': True,
                'message': '解析完成',
                'map_data_id': map_data_id,
                'statistics': result.get('statistics', {})
            }
        else:
            # 解析失败
            map_data.parse_status = 'failed'
            map_data.parse_progress = 0.0
            error_msg = result.get('error', '未知错误')
            map_data.error_message = error_msg
            db.session.commit()

            log_error(f"MCA文件解析失败: {map_data.filename}, 错误: {error_msg}")

            raise Exception(f"解析失败: {error_msg}")

    except Exception as e:
        # 更新状态为失败
        try:
            map_data = MapData.query.get(map_data_id)
            if map_data:
                map_data.parse_status = 'failed'
                map_data.parse_progress = 0.0
                map_data.error_message = str(e)
                db.session.commit()
        except:
            pass

        error_msg = f"解析任务异常: {str(e)}"
        log_error(f"{error_msg}\n{traceback.format_exc()}")

        # 更新任务状态
        self.update_state(
            state='FAILURE',
            meta={
                'error': error_msg,
                'traceback': traceback.format_exc()
            }
        )

        raise Exception(error_msg)


@celery.task(bind=True)
def train_model_task(self, training_job_id):
    """异步训练模型任务"""
    try:
        from app import db
        from app.models.training_job import TrainingJob
        from app.services.model_trainer import ModelTrainer
        from app.utils.logging_config import log_info, log_error

        # 更新任务状态
        self.update_state(state='PROGRESS', meta={'step': '开始训练', 'progress': 0})

        # 获取训练任务
        training_job = TrainingJob.query.get(training_job_id)
        if not training_job:
            raise ValueError(f"训练任务 {training_job_id} 不存在")

        # 更新训练状态
        training_job.status = 'training'
        training_job.progress = 0.0
        training_job.started_at = datetime.now(timezone.utc)
        db.session.commit()

        # 创建训练器
        trainer = ModelTrainer()

        # 定义进度回调函数
        def progress_callback(step, total_steps, loss=None):
            progress = int((step / total_steps) * 100)
            meta = {
                'step': f'训练步骤 {step}/{total_steps}',
                'progress': progress
            }
            if loss is not None:
                meta['loss'] = loss

            self.update_state(state='PROGRESS', meta=meta)

            # 更新数据库中的进度
            training_job.progress = progress
            if loss is not None:
                training_job.current_loss = loss
            db.session.commit()

        # 开始训练
        result = trainer.train(
            training_job_id=training_job_id,
            progress_callback=progress_callback
        )

        if result.get('success', False):
            # 训练成功
            training_job.status = 'completed'
            training_job.progress = 100.0
            training_job.completed_at = datetime.now(timezone.utc)
            training_job.model_path = result.get('model_path', '')
            training_job.final_loss = result.get('final_loss', 0.0)

            db.session.commit()

            log_info(f"模型训练完成: 任务ID {training_job_id}")

            return {
                'success': True,
                'message': '训练完成',
                'training_job_id': training_job_id,
                'model_path': result.get('model_path', ''),
                'final_loss': result.get('final_loss', 0.0)
            }
        else:
            # 训练失败
            training_job.status = 'failed'
            error_msg = result.get('error', '未知错误')
            training_job.error_message = error_msg
            training_job.completed_at = datetime.now(timezone.utc)
            db.session.commit()

            log_error(f"模型训练失败: 任务ID {training_job_id}, 错误: {error_msg}")

            raise Exception(f"训练失败: {error_msg}")

    except Exception as e:
        # 更新状态为失败
        try:
            training_job = TrainingJob.query.get(training_job_id)
            if training_job:
                training_job.status = 'failed'
                training_job.error_message = str(e)
                training_job.completed_at = datetime.now(timezone.utc)
                db.session.commit()
        except:
            pass

        error_msg = f"训练任务异常: {str(e)}"
        log_error(f"{error_msg}\n{traceback.format_exc()}")

        # 更新任务状态
        self.update_state(
            state='FAILURE',
            meta={
                'error': error_msg,
                'traceback': traceback.format_exc()
            }
        )

        raise Exception(error_msg)


@celery.task(bind=True)
def generate_map_task(self, prompt, parameters=None):
    """异步生成地图任务"""
    try:
        from app.services.map_generator import MapGenerator
        from app.utils.logging_config import log_info, log_error

        # 更新任务状态
        self.update_state(state='PROGRESS', meta={'step': '开始生成', 'progress': 0})

        # 创建地图生成器
        generator = MapGenerator()

        # 定义进度回调函数
        def progress_callback(step, total_steps, current_step_name=None):
            progress = int((step / total_steps) * 100)
            meta = {
                'step': current_step_name or f'生成步骤 {step}/{total_steps}',
                'progress': progress
            }
            self.update_state(state='PROGRESS', meta=meta)

        # 开始生成
        result = generator.generate(
            prompt=prompt,
            parameters=parameters or {},
            progress_callback=progress_callback
        )

        if result.get('success', False):
            log_info(f"地图生成完成: {prompt}")

            return {
                'success': True,
                'message': '生成完成',
                'file_path': result.get('file_path', ''),
                'preview_data': result.get('preview_data', {})
            }
        else:
            error_msg = result.get('error', '未知错误')
            log_error(f"地图生成失败: {prompt}, 错误: {error_msg}")
            raise Exception(f"生成失败: {error_msg}")

    except Exception as e:
        error_msg = f"生成任务异常: {str(e)}"
        log_error(f"{error_msg}\n{traceback.format_exc()}")

        # 更新任务状态
        self.update_state(
            state='FAILURE',
            meta={
                'error': error_msg,
                'traceback': traceback.format_exc()
            }
        )

        raise Exception(error_msg)
