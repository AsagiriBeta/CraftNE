"""
标注数据模型
"""

from app import db
from datetime import datetime, timezone
import json

class Annotation(db.Model):
    """标注数据模型"""
    
    __tablename__ = 'annotations'
    
    id = db.Column(db.Integer, primary_key=True)
    map_data_id = db.Column(db.Integer, db.ForeignKey('map_data.id'), nullable=False)
    
    # 标注信息
    label = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # 标注区域 (3D边界框)
    min_x = db.Column(db.Integer, nullable=False)
    min_y = db.Column(db.Integer, nullable=False)
    min_z = db.Column(db.Integer, nullable=False)
    max_x = db.Column(db.Integer, nullable=False)
    max_y = db.Column(db.Integer, nullable=False)
    max_z = db.Column(db.Integer, nullable=False)
    
    # 标注类型
    annotation_type = db.Column(db.String(50), default='region')  # region, structure, biome
    
    # 额外属性
    properties = db.Column(db.Text)  # JSON格式
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'map_data_id': self.map_data_id,
            'label': self.label,
            'description': self.description,
            'bbox': {
                'min': [self.min_x, self.min_y, self.min_z],
                'max': [self.max_x, self.max_y, self.max_z]
            },
            'annotation_type': self.annotation_type,
            'properties': json.loads(self.properties) if self.properties else {},
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def get_volume(self):
        """计算标注区域体积"""
        return (self.max_x - self.min_x + 1) * (self.max_y - self.min_y + 1) * (self.max_z - self.min_z + 1)

    @staticmethod
    def create_from_dict(data):
        """从字典创建标注对象"""
        properties = data.get('properties', {})
        return Annotation(
            map_data_id=data['map_data_id'],
            label=data['label'],
            description=data.get('description', ''),
            min_x=data['bbox']['min'][0],
            min_y=data['bbox']['min'][1],
            min_z=data['bbox']['min'][2],
            max_x=data['bbox']['max'][0],
            max_y=data['bbox']['max'][1],
            max_z=data['bbox']['max'][2],
            annotation_type=data.get('annotation_type', 'region'),
            properties=json.dumps(properties) if properties else None
        )

class AnnotationLabel(db.Model):
    """标注标签预设"""
    
    __tablename__ = 'annotation_labels'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    color = db.Column(db.String(7), nullable=False)  # hex color
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
