"""
文件上传视图
"""

import os
import uuid
from flask import Blueprint, request, jsonify, current_app, render_template
from werkzeug.utils import secure_filename
from app import db
from app.models.map_data import MapData
from app.services.mca_parser import MCAParser
from app.utils.validators import allowed_file

bp = Blueprint('upload', __name__)

@bp.route('/')
def upload_page():
    """上传页面"""
    return render_template('upload.html')

@bp.route('/api/upload', methods=['POST'])
def upload_file():
    """API: 上传MCA文件"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # 生成安全的文件名
        original_filename = file.filename
        filename = str(uuid.uuid4()) + '_' + secure_filename(original_filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # ��存文件
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        
        # 创建数据库记录
        map_data = MapData(
            filename=filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            parse_status='pending'
        )
        
        db.session.add(map_data)
        db.session.commit()
        
        # 启动异步解析任务
        try:
            from app.tasks import celery, parse_mca_file_task
            task = parse_mca_file_task.delay(map_data.id)

            # 更新任务ID
            map_data.task_id = task.id
            map_data.parse_status = 'parsing'
            db.session.commit()

            return jsonify({
                'message': 'File uploaded successfully, parsing started',
                'map_id': map_data.id,
                'task_id': task.id,
                'filename': original_filename,
                'status': 'parsing'
            })

        except Exception as e:
            # 如果异 asynchronous 任务启动失败，回退到同步解析
            current_app.logger.warning(f"异步任务启动失败，回退到同步解析: {str(e)}")

            try:
                map_data.parse_status = 'parsing'
                db.session.commit()

                parser = MCAParser()
                result = parser.parse_file(file_path, map_data.id)

                if result.get('success', False):
                    map_data.parse_status = 'completed'
                    map_data.is_parsed = True
                    db.session.commit()

                    return jsonify({
                        'message': 'File uploaded and parsed successfully',
                        'map_id': map_data.id,
                        'filename': original_filename,
                        'status': 'completed'
                    })
                else:
                    map_data.parse_status = 'failed'
                    map_data.parse_error = result.get('error', 'Unknown parsing error')
                    db.session.commit()

                    return jsonify({
                        'message': 'File uploaded but parsing failed',
                        'map_id': map_data.id,
                        'filename': original_filename,
                        'error': result.get('error', 'Unknown parsing error')
                    }), 206

            except Exception as sync_e:
                map_data.parse_status = 'failed'
                map_data.parse_error = str(sync_e)
                db.session.commit()

                return jsonify({
                    'message': 'File uploaded but parsing failed',
                    'map_id': map_data.id,
                    'filename': original_filename,
                    'error': str(sync_e)
                }), 206

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/maps')
def list_maps():
    """API: 获取地图列表"""
    maps = MapData.query.order_by(MapData.created_at.desc()).all()
    return jsonify([map_data.to_dict() for map_data in maps])

@bp.route('/api/maps/<int:map_id>')
def get_map(map_id):
    """API: 获取单个地图信息"""
    map_data = MapData.query.get_or_404(map_id)
    
    result = map_data.to_dict()
    
    # 如果已解析，添加统计信息
    if map_data.is_parsed:
        try:
            parser = MCAParser()
            stats = parser.get_map_stats(map_id)
            result['stats'] = stats
        except Exception as e:
            result['stats_error'] = str(e)
    
    return jsonify(result)

@bp.route('/api/maps/<int:map_id>/status')
def get_parse_status(map_id):
    """API: 获取解析状态"""
    map_data = MapData.query.get_or_404(map_id)

    result = {
        'map_id': map_id,
        'parse_status': map_data.parse_status,
        'parse_progress': map_data.parse_progress or 0.0,
        'is_parsed': map_data.is_parsed,
        'parse_error': map_data.parse_error
    }

    # 如果有任务ID，获取Celery任务状态
    if hasattr(map_data, 'task_id') and map_data.task_id:
        try:
            from app.tasks import celery
            task = celery.AsyncResult(map_data.task_id)

            result['task_status'] = task.status
            if task.status == 'PROGRESS':
                result['task_info'] = task.info
            elif task.status == 'FAILURE':
                result['task_error'] = str(task.info)
        except Exception as e:
            result['task_error'] = f"无法获取任务状态: {str(e)}"

    return jsonify(result)

@bp.route('/api/maps/<int:map_id>', methods=['DELETE'])
def delete_map(map_id):
    """API: 删除地图"""
    try:
        map_data = MapData.query.get_or_404(map_id)

        # 如果有正在进行的任务，尝试取消
        if hasattr(map_data, 'task_id') and map_data.task_id:
            try:
                from app.tasks import celery
                celery.control.revoke(map_data.task_id, terminate=True)
                current_app.logger.info(f"已取消任务: {map_data.task_id}")
            except Exception as e:
                current_app.logger.warning(f"无法取消任务 {map_data.task_id}: {str(e)}")

        # 删除文件
        if os.path.exists(map_data.file_path):
            try:
                os.remove(map_data.file_path)
                current_app.logger.info(f"已删除文件: {map_data.file_path}")
            except Exception as e:
                current_app.logger.warning(f"无法删除文件 {map_data.file_path}: {str(e)}")

        # 删除缓存数据
        try:
            from app.utils.cache import delete_map_cache
            delete_map_cache(map_id)
            current_app.logger.info(f"已删除缓存: map_{map_id}")
        except Exception as e:
            current_app.logger.warning(f"无法删除缓存: {str(e)}")

        # 删除数据库记录
        db.session.delete(map_data)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'地图 "{map_data.original_filename}" 已成功删除'
        })

    except Exception as e:
        current_app.logger.error(f"删除地图失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'删除地图失败: {str(e)}'
        }), 500

@bp.route('/api/maps/<int:map_id>/retry', methods=['POST'])
def retry_parse(map_id):
    """API: 重新解析地图"""
    try:
        map_data = MapData.query.get_or_404(map_id)

        # 取消现有任务
        if hasattr(map_data, 'task_id') and map_data.task_id:
            try:
                from app.tasks import celery
                celery.control.revoke(map_data.task_id, terminate=True)
            except Exception:
                pass

        # 重置状态
        map_data.parse_status = 'pending'
        map_data.parse_error = None
        map_data.parse_progress = 0.0
        map_data.is_parsed = False
        map_data.task_id = None
        db.session.commit()

        # 启动新的解析任务
        try:
            from app.tasks import parse_mca_file_task
            task = parse_mca_file_task.delay(map_data.id)

            map_data.task_id = task.id
            map_data.parse_status = 'parsing'
            db.session.commit()

            return jsonify({
                'success': True,
                'message': '重新解析已启动',
                'task_id': task.id
            })

        except Exception as e:
            # 回退到同步解析
            current_app.logger.warning(f"异步任务启动失败，回退到同步解析: {str(e)}")

            map_data.parse_status = 'parsing'
            db.session.commit()

            parser = MCAParser()
            result = parser.parse_file(map_data.file_path, map_data.id)

            if result.get('success', False):
                map_data.parse_status = 'completed'
                map_data.is_parsed = True
            else:
                map_data.parse_status = 'failed'
                map_data.parse_error = result.get('error', 'Unknown parsing error')

            db.session.commit()

            return jsonify({
                'success': result.get('success', False),
                'message': '重新解析完成' if result.get('success') else '重新解析失败',
                'error': result.get('error') if not result.get('success') else None
            })

    except Exception as e:
        current_app.logger.error(f"重新解析失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'重新解析失败: {str(e)}'
        }), 500
