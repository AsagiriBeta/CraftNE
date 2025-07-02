"""
地图数据模型
"""

from app import db
from datetime import datetime, timezone
import json
import os

class MapData(db.Model):
    """地图数据模型"""
    
    __tablename__ = 'map_data'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    
    # 地图元数据
    chunk_count = db.Column(db.Integer)
    world_name = db.Column(db.String(255))
    minecraft_version = db.Column(db.String(50))
    region_x = db.Column(db.Integer)
    region_z = db.Column(db.Integer)

    # 解析状态
    is_parsed = db.Column(db.Boolean, default=False)
    parse_status = db.Column(db.String(50), default='pending')  # pending, parsing, completed, failed
    parse_error = db.Column(db.Text)
    parse_progress = db.Column(db.Float, default=0.0)
    task_id = db.Column(db.String(255))  # Celery任务ID

    # 统计信息
    block_types_count = db.Column(db.Text)  # JSON格式存储方块类型统计
    biome_distribution = db.Column(db.Text)  # JSON格式存储生物群系分布
    height_map_data = db.Column(db.Text)  # JSON格式存储高度图数据

    # 时间戳
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    parsed_at = db.Column(db.DateTime)

    # 关系
    annotations = db.relationship('Annotation', backref='map_data', lazy='dynamic', cascade='all, delete-orphan')
    training_jobs = db.relationship('TrainingJob', backref='map_data', lazy='dynamic')

    def __repr__(self):
        return f'<MapData {self.filename}>'

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'chunk_count': self.chunk_count,
            'world_name': self.world_name,
            'minecraft_version': self.minecraft_version,
            'region_x': self.region_x,
            'region_z': self.region_z,
            'is_parsed': self.is_parsed,
            'parse_status': self.parse_status,
            'parse_progress': self.parse_progress,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'parsed_at': self.parsed_at.isoformat() if self.parsed_at else None,
            'block_types_count': json.loads(self.block_types_count) if self.block_types_count else {},
            'biome_distribution': json.loads(self.biome_distribution) if self.biome_distribution else {},
            'annotation_count': self.annotations.count()
        }

    def get_file_size_formatted(self):
        """获取格式化的文件大小"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def file_exists(self):
        """检查文件是否存在"""
        return os.path.exists(self.file_path)

    def update_block_stats(self, block_stats):
        """更新方块统计信息"""
        self.block_types_count = json.dumps(block_stats)
        self.updated_at = datetime.now(timezone.utc)

    def update_biome_distribution(self, biome_data):
        """更新生物群系分布"""
        self.biome_distribution = json.dumps(biome_data)
        self.updated_at = datetime.now(timezone.utc)

    def set_parse_completed(self):
        """设置解析完成状态"""
        self.is_parsed = True
        self.parse_status = 'completed'
        self.parse_progress = 100.0
        self.parsed_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def set_parse_failed(self, error_message):
        """设置解析失败状态"""
        self.is_parsed = False
        self.parse_status = 'failed'
        self.parse_error = error_message
        self.updated_at = datetime.now(timezone.utc)

class ChunkData(db.Model):
    """区块数据模型"""
    
    __tablename__ = 'chunk_data'
    
    id = db.Column(db.Integer, primary_key=True)
    map_data_id = db.Column(db.Integer, db.ForeignKey('map_data.id'), nullable=False)
    
    # 区块坐标
    chunk_x = db.Column(db.Integer, nullable=False)
    chunk_z = db.Column(db.Integer, nullable=False)
    
    # 方块数据 (JSON格式存储)
    blocks_data = db.Column(db.Text)  # JSON string
    
    # 统计信息
    block_count = db.Column(db.Integer)
    unique_blocks = db.Column(db.Text)  # JSON array of unique block types
    
    def get_blocks_data(self):
        """获取方块数据"""
        if self.blocks_data:
            return json.loads(self.blocks_data)
        return []
    
    def set_blocks_data(self, data):
        """设置方块数据"""
        self.blocks_data = json.dumps(data)