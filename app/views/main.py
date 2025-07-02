"""
主页面视图
"""

from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from app.models.map_data import MapData
from app.models.annotation import Annotation
from app import db
import json
import os

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """主页"""
    return render_template('index.html')

@bp.route('/dashboard')
def dashboard():
    """仪表板"""
    # 获取统计数据
    total_maps = MapData.query.count()
    parsed_maps = MapData.query.filter_by(is_parsed=True).count()
    total_annotations = Annotation.query.count()
    
    recent_maps = MapData.query.order_by(MapData.created_at.desc()).limit(5).all()
    
    stats = {
        'total_maps': total_maps,
        'parsed_maps': parsed_maps,
        'pending_maps': total_maps - parsed_maps,
        'total_annotations': total_annotations,
        'recent_maps': [map_data.to_dict() for map_data in recent_maps]
    }
    
    return render_template('dashboard.html', stats=stats)

@bp.route('/api/stats')
def api_stats():
    """API: 获取统计数据"""
    total_maps = MapData.query.count()
    parsed_maps = MapData.query.filter_by(is_parsed=True).count()
    total_annotations = Annotation.query.count()
    
    return jsonify({
        'total_maps': total_maps,
        'parsed_maps': parsed_maps,
        'pending_maps': total_maps - parsed_maps,
        'total_annotations': total_annotations
    })

@bp.route('/maps')
def map_list():
    """地图列表页面"""
    page = request.args.get('page', 1, type=int)
    per_page = 10  # 每页显示10个地���

    maps = MapData.query.filter_by(is_parsed=True).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('map_list.html', maps=maps)

@bp.route('/maps/<int:map_id>')
def map_viewer(map_id):
    """地图查看器页面"""
    map_data = MapData.query.get_or_404(map_id)

    if not map_data.is_parsed:
        return render_template('errors/404.html'), 404

    # 获取地图的注释
    annotations = Annotation.query.filter_by(map_data_id=map_id).all()

    # 尝试加载Three.js数据
    threejs_data = None
    threejs_file_path = os.path.join('models_cache', f'threejs_data_{map_id}.json')
    if os.path.exists(threejs_file_path):
        try:
            with open(threejs_file_path, 'r', encoding='utf-8') as f:
                threejs_data = json.load(f)
        except Exception as e:
            print(f"加载Three.js数据失败: {e}")

    return render_template('map_viewer.html',
                         map_data=map_data,
                         map_id=map_id,
                         annotations=annotations,
                         threejs_data=threejs_data)

@bp.route('/api/maps')
def api_map_list():
    """API: 获取地图列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    maps = MapData.query.filter_by(is_parsed=True).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'maps': [map_data.to_dict() for map_data in maps.items],
        'total': maps.total,
        'pages': maps.pages,
        'current_page': page,
        'has_next': maps.has_next,
        'has_prev': maps.has_prev
    })

@bp.route('/api/maps/<int:map_id>')
def api_map_detail(map_id):
    """API: 获取地图详细信息"""
    map_data = MapData.query.get_or_404(map_id)

    if not map_data.is_parsed:
        return jsonify({'error': '地图尚未解析'}), 404

    # 加载Three.js数据
    threejs_data = None
    threejs_file_path = os.path.join('models_cache', f'threejs_data_{map_id}.json')
    if os.path.exists(threejs_file_path):
        try:
            with open(threejs_file_path, 'r', encoding='utf-8') as f:
                threejs_data = json.load(f)
        except Exception as e:
            return jsonify({'error': f'加载地图数据失败: {str(e)}'}), 500

    return jsonify({
        'map_data': map_data.to_dict(),
        'threejs_data': threejs_data
    })

@bp.route('/api/maps/<int:map_id>', methods=['DELETE'])
def api_delete_map(map_id):
    """API: 删除地图"""
    try:
        map_data = MapData.query.get_or_404(map_id)

        # ��除相关文件
        files_to_delete = []

        # 删除原始MCA文件
        if map_data.file_path and os.path.exists(map_data.file_path):
            files_to_delete.append(map_data.file_path)

        # 删除缓存的JSON文件
        cache_files = [
            os.path.join('models_cache', f'map_data_{map_id}.json'),
            os.path.join('models_cache', f'threejs_data_{map_id}.json')
        ]

        for cache_file in cache_files:
            if os.path.exists(cache_file):
                files_to_delete.append(cache_file)

        # 删除数据库记录（会级联删除相关的标注和训练任务）
        db.session.delete(map_data)
        db.session.commit()

        # 删除文件
        for file_path in files_to_delete:
            try:
                os.remove(file_path)
            except OSError as e:
                print(f"删除文件失败 {file_path}: {e}")

        return jsonify({
            'success': True,
            'message': '地图删除成功'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'删除失败: {str(e)}'
        }), 500

@bp.route('/maps/<int:map_id>/delete', methods=['POST'])
def delete_map(map_id):
    """删除地图（页面操作）"""
    try:
        map_data = MapData.query.get_or_404(map_id)

        # 删除相关文件
        files_to_delete = []

        # 删除原始MCA文件
        if map_data.file_path and os.path.exists(map_data.file_path):
            files_to_delete.append(map_data.file_path)

        # 删除缓存的JSON文件
        cache_files = [
            os.path.join('models_cache', f'map_data_{map_id}.json'),
            os.path.join('models_cache', f'threejs_data_{map_id}.json')
        ]

        for cache_file in cache_files:
            if os.path.exists(cache_file):
                files_to_delete.append(cache_file)

        # 保存文件名用于成功消息
        filename = map_data.original_filename

        # 删除数据库记录
        db.session.delete(map_data)
        db.session.commit()

        # 删除文件
        for file_path in files_to_delete:
            try:
                os.remove(file_path)
            except OSError as e:
                print(f"删除文件失败 {file_path}: {e}")

        flash(f'地图 "{filename}" 删除成功', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'删除失败: {str(e)}', 'error')

    return redirect(url_for('main.map_list'))
