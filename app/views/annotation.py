"""
标注相关视图
"""
from flask import Blueprint, jsonify, request
from app.models.annotation import Annotation
from app import db

bp = Blueprint('annotation', __name__)

@bp.route('/api/annotations/<int:map_id>', methods=['GET'])
def get_annotations(map_id):
    """获取指定地图的所有标注"""
    annotations = Annotation.query.filter_by(map_data_id=map_id).all()
    return jsonify([a.to_dict() for a in annotations])

@bp.route('/api/annotations', methods=['POST'])
def create_annotation():
    """创建新标注"""
    data = request.get_json()
    annotation = Annotation.create_from_dict(data)
    db.session.add(annotation)
    db.session.commit()
    return jsonify(annotation.to_dict()), 201

