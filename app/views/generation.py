"""
地图生成相关视图
"""
from flask import Blueprint, render_template, jsonify, request
from app.models.map_data import MapData
from app import db

bp = Blueprint('generation', __name__)

@bp.route('/')
def generation_page():
    """地图生成页面"""
    return render_template('generation.html')

@bp.route('/api/generate', methods=['POST'])
def generate_map():
    """生成新地图"""
    data = request.get_json()

    # TODO: 实现地图生成逻辑
    # 这里是占位符，后续需要实现AI生成功能

    return jsonify({
        'message': '地图生成功能正在开发中',
        'status': 'pending'
    }), 202

@bp.route('/api/jobs')
def get_generation_jobs():
    """获取生成任务列表"""
    # TODO: 实现生成任务查询
    return jsonify([])
