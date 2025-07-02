"""
训练任务模型
"""

from app import db
from datetime import datetime, timezone
import json

class TrainingJob(db.Model):
    """训练任务模型"""

    __tablename__ = 'training_jobs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    # 外键关系
    map_data_id = db.Column(db.Integer, db.ForeignKey('map_data.id'), nullable=True)

    # 训练配置
    model_type = db.Column(db.String(50), default='diffusion')  # diffusion, gan, vae
    training_config = db.Column(db.Text)  # JSON格式的训练参数

    # 训练数据
    training_data_path = db.Column(db.String(500))
    validation_data_path = db.Column(db.String(500))

    # 训练状态
    status = db.Column(db.String(50), default='pending')  # pending, running, completed, failed, stopped
    progress = db.Column(db.Float, default=0.0)  # 0.0 - 1.0
    current_epoch = db.Column(db.Integer, default=0)
    total_epochs = db.Column(db.Integer, default=100)

    # 训练指标
    train_loss = db.Column(db.Float)
    validation_loss = db.Column(db.Float)
    best_loss = db.Column(db.Float)

    # 模型输出
    model_path = db.Column(db.String(500))
    checkpoint_path = db.Column(db.String(500))

    # 错误信息
    error_message = db.Column(db.Text)

    # 时间戳
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'model_type': self.model_type,
            'status': self.status,
            'progress': self.progress,
            'current_epoch': self.current_epoch,
            'total_epochs': self.total_epochs,
            'train_loss': self.train_loss,
            'validation_loss': self.validation_loss,
            'best_loss': self.best_loss,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'updated_at': self.updated_at.isoformat()
        }

    def get_training_config(self):
        """获取训练配置"""
        return json.loads(self.training_config) if self.training_config else {}

    def set_training_config(self, config):
        """设置训练配置"""
        self.training_config = json.dumps(config)

    def update_progress(self, epoch, train_loss=None, val_loss=None):
        """更新训练进度"""
        self.current_epoch = epoch
        self.progress = epoch / self.total_epochs
        if train_loss is not None:
            self.train_loss = train_loss
        if val_loss is not None:
            self.validation_loss = val_loss
            if self.best_loss is None or val_loss < self.best_loss:
                self.best_loss = val_loss
        self.updated_at = datetime.now(timezone.utc)


class GeneratedMap(db.Model):
    """生成的地图模型"""

    __tablename__ = 'generated_maps'

    id = db.Column(db.Integer, primary_key=True)
    training_job_id = db.Column(db.Integer, db.ForeignKey('training_jobs.id'), nullable=False)

    # 生成参数
    prompt = db.Column(db.Text, nullable=False)
    negative_prompt = db.Column(db.Text)
    seed = db.Column(db.Integer)

    # 生成配置
    generation_config = db.Column(db.Text)  # JSON格式

    # 输出文件
    output_path = db.Column(db.String(500))
    preview_image_path = db.Column(db.String(500))

    # 生成状态
    status = db.Column(db.String(50), default='pending')  # pending, generating, completed, failed
    progress = db.Column(db.Float, default=0.0)

    # 时间戳
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime)

    # 关联
    training_job = db.relationship('TrainingJob', backref='generated_maps')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'training_job_id': self.training_job_id,
            'prompt': self.prompt,
            'negative_prompt': self.negative_prompt,
            'seed': self.seed,
            'status': self.status,
            'progress': self.progress,
            'output_path': self.output_path,
            'preview_image_path': self.preview_image_path,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
