"""
API蓝图 - 提供RESTful API接口
"""

from flask import Blueprint, request, jsonify, current_app
from app.models.map_data import MapData
from app.models.annotation import Annotation
from app.models.training_job import TrainingJob
from app.services.mca_parser import MCAParser
from app.utils.validators import allowed_file
from app.utils.logging_config import log_error, log_user_action
from app.utils.decorators import (
    monitor_performance, validate_json_request,
    log_user_activity, handle_exceptions, api_response
)
from app.utils.response import APIResponse, make_json_response
from app.utils.cache import cache_result
from app import db
import os
import json

bp = Blueprint('api', __name__)

@bp.route('/maps', methods=['GET'])
@api_response()
@monitor_performance('api_get_maps')
@log_user_activity('获取地图列表')
@cache_result(expire=300)  # 缓存5分钟
def get_maps():
    """获取所有地图列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)

        query = MapData.query

        # 支持按状态过滤
        status = request.args.get('status')
        if status:
            query = query.filter(MapData.status == status)

        # 支���按文件名搜索
        search = request.args.get('search')
        if search:
            query = query.filter(MapData.filename.contains(search))

        # 分页查询
        maps_pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        maps_data = [map_data.to_dict() for map_data in maps_pagination.items]

        return APIResponse.paginated(
            maps_data, page, per_page, maps_pagination.total
        )
    except Exception as e:
        log_error(e, context='获取地图列表')
        return APIResponse.internal_error('获取地图列表失败')

@bp.route('/maps/<int:map_id>', methods=['GET'])
@api_response()
@monitor_performance('api_get_map_detail')
@log_user_activity('获取地图详情')
@cache_result(expire=300)
def get_map_detail(map_id):
    """获取地图详细信息"""
    try:
        map_data = MapData.query.get_or_404(map_id)
        return APIResponse.success(data=map_data.to_dict())
    except Exception as e:
        log_error(f"获取地图详情失败: {str(e)}", extra={'map_id': map_id})
        return APIResponse.error("获取地图详情失败")

@bp.route('/maps/<int:map_id>/blocks', methods=['GET'])
@api_response()
@monitor_performance('api_get_map_blocks')
@log_user_activity('获取地图方块数据')
@cache_result(expire=600)  # 缓存10分钟
def get_map_blocks(map_id):
    """获取地图的方块数据用于3D渲染"""
    try:
        map_data = MapData.query.get_or_404(map_id)

        if not map_data.is_parsed:
            return APIResponse.error("地图尚未解析完成", status_code=400)

        # 从缓存的JSON文件读取3D数据
        threejs_cache_path = os.path.join(
            current_app.config.get('MODELS_CACHE_FOLDER', 'models_cache'),
            f'threejs_data_{map_id}.json'
        )

        if os.path.exists(threejs_cache_path):
            with open(threejs_cache_path, 'r') as f:
                blocks_data = json.load(f)
            return APIResponse.success(data=blocks_data)
        else:
            # 如果缓存不存在，重新生成
            parser = MCAParser()
            blocks_data = parser.generate_threejs_data(map_data.file_path, map_id)
            return APIResponse.success(data=blocks_data)

    except Exception as e:
        log_error(f"获取地图方块数据失败: {str(e)}", extra={'map_id': map_id})
        return APIResponse.error("获取地图方块数据失败")

@bp.route('/maps/<int:map_id>/export/obj', methods=['GET'])
@api_response()
@monitor_performance('api_export_obj')
@log_user_activity('导出OBJ模型')
def export_map_obj(map_id):
    """导出地图为OBJ模���文件"""
    try:
        map_data = MapData.query.get_or_404(map_id)

        if not map_data.is_parsed:
            return APIResponse.error("地图尚未解析完成", status_code=400)

        # 生成OBJ文件
        from app.services.obj_exporter import OBJExporter
        exporter = OBJExporter()
        obj_file_path = exporter.export_map_to_obj(map_data)

        if obj_file_path and os.path.exists(obj_file_path):
            return APIResponse.success(data={
                'download_url': f'/api/download/{os.path.basename(obj_file_path)}',
                'filename': os.path.basename(obj_file_path),
                'file_size': os.path.getsize(obj_file_path)
            })
        else:
            return APIResponse.error("OBJ文件生成失败")

    except Exception as e:
        log_error(f"导出OBJ模型失败: {str(e)}", extra={'map_id': map_id})
        return APIResponse.error("导出OBJ模型失败")

@bp.route('/maps/<int:map_id>/export/obj/region', methods=['GET'])
@api_response()
@monitor_performance('api_export_region_obj')
@log_user_activity('导出区域OBJ模型')
def export_region_obj(map_id):
    """导出地图指定区域为OBJ模型文件"""
    try:
        map_data = MapData.query.get_or_404(map_id)

        if not map_data.is_parsed:
            return APIResponse.error("地图尚未解析完成", status_code=400)

        # 获取区域坐标参数
        min_x = request.args.get('min_x', type=int)
        min_y = request.args.get('min_y', type=int)
        min_z = request.args.get('min_z', type=int)
        max_x = request.args.get('max_x', type=int)
        max_y = request.args.get('max_y', type=int)
        max_z = request.args.get('max_z', type=int)

        if None in [min_x, min_y, min_z, max_x, max_y, max_z]:
            return APIResponse.error("缺少区域坐标参数", status_code=400)

        # 生成区域OBJ文件
        from app.services.obj_exporter import OBJExporter
        exporter = OBJExporter()
        obj_file_path = exporter.export_region_to_obj(
            map_data,
            (min_x, min_y, min_z),
            (max_x, max_y, max_z)
        )

        if obj_file_path and os.path.exists(obj_file_path):
            return APIResponse.success(data={
                'download_url': f'/api/download/{os.path.basename(obj_file_path)}',
                'filename': os.path.basename(obj_file_path),
                'file_size': os.path.getsize(obj_file_path)
            })
        else:
            return APIResponse.error("区域OBJ文件生成失败")

    except Exception as e:
        log_error(f"导出区域OBJ模型失败: {str(e)}", extra={'map_id': map_id})
        return APIResponse.error("导出区域OBJ模型失败")

@bp.route('/maps/<int:map_id>/parse', methods=['POST'])
@api_response()
@handle_exceptions('地图解析失败')
@monitor_performance('api_parse_map')
@log_user_activity('解析地图')
def parse_map(map_id):
    """解析地图文件"""
    map_data = MapData.query.get(map_id)
    if not map_data:
        return APIResponse.not_found(f'地图 {map_id} 不存在')

    if map_data.status == 'parsed':
        return APIResponse.error('地图已经解析过了', 'ALREADY_PARSED')

    parser = MCAParser()

    # 异步解析地图
    try:
        result = parser.parse_async(map_data.file_path)

        # 更新地图状态
        map_data.status = 'parsing'
        db.session.commit()

        return APIResponse.success({
            'task_id': result.get('task_id'),
            'message': '地图解析任务已启动'
        }, '解析任务创建成功')
    except Exception as e:
        map_data.status = 'error'
        map_data.error_message = str(e)
        db.session.commit()
        raise

@bp.route('/maps/<int:map_id>/annotations', methods=['GET'])
@api_response()
@monitor_performance('api_get_annotations')
def get_map_annotations(map_id):
    """获取地图的标注数据"""
    try:
        map_data = MapData.query.get(map_id)
        if not map_data:
            return APIResponse.not_found(f'地图 {map_id} 不存在')

        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 200)

        annotations_pagination = Annotation.query.filter_by(
            map_data_id=map_id
        ).paginate(page=page, per_page=per_page, error_out=False)

        annotations_data = [ann.to_dict() for ann in annotations_pagination.items]

        return APIResponse.paginated(
            annotations_data, page, per_page, annotations_pagination.total,
            '获取标注数据成功'
        )
    except Exception as e:
        log_error(e, context=f'获取地图标注: {map_id}')
        return APIResponse.internal_error('获取标注数据���败')

@bp.route('/annotations', methods=['POST'])
@api_response()
@validate_json_request(['map_data_id', 'annotation_type', 'coordinates'])
@handle_exceptions('创建标注失败')
@monitor_performance('api_create_annotation')
@log_user_activity('创建标注')
def create_annotation():
    """创建新标注"""
    data = request.get_json()

    # 验证地图存在
    map_data = MapData.query.get(data['map_data_id'])
    if not map_data:
        return APIResponse.not_found(f'地图 {data["map_data_id"]} 不存在')

    # 创建标注
    annotation = Annotation(
        map_data_id=data['map_data_id'],
        annotation_type=data['annotation_type'],
        coordinates=data['coordinates'],
        label=data.get('label', ''),
        description=data.get('description', ''),
        metadata=data.get('metadata', {})
    )

    db.session.add(annotation)
    db.session.commit()

    return APIResponse.created(annotation.to_dict(), '标注创建成功')

@bp.route('/training-jobs', methods=['GET'])
@api_response()
@monitor_performance('api_get_training_jobs')
def get_training_jobs():
    """获取训练任务列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)

        query = TrainingJob.query

        # 支持按状态过滤
        status = request.args.get('status')
        if status:
            query = query.filter(TrainingJob.status == status)

        jobs_pagination = query.order_by(
            TrainingJob.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

        jobs_data = [job.to_dict() for job in jobs_pagination.items]

        return APIResponse.paginated(
            jobs_data, page, per_page, jobs_pagination.total,
            '获取训练任务成功'
        )
    except Exception as e:
        log_error(e, context='获取训练任务列表')
        return APIResponse.internal_error('获取训练任务失败')

@bp.route('/training-jobs', methods=['POST'])
@api_response()
@validate_json_request(['map_data_id', 'model_type'])
@handle_exceptions('创建训练任务失败')
@monitor_performance('api_create_training_job')
@log_user_activity('创建训练任务')
def create_training_job():
    """创建新的训练任务"""
    data = request.get_json()

    # 验证地图存在
    map_data = MapData.query.get(data['map_data_id'])
    if not map_data:
        return APIResponse.not_found(f'地图 {data["map_data_id"]} 不存在')

    # 验证地图已解析
    if map_data.status != 'parsed':
        return APIResponse.validation_error('��图尚未解析完成')

    # 创建训练任务
    training_job = TrainingJob(
        map_data_id=data['map_data_id'],
        model_type=data['model_type'],
        parameters=data.get('parameters', {}),
        status='pending'
    )

    db.session.add(training_job)
    db.session.commit()

    return APIResponse.created(training_job.to_dict(), '训练任务创建成功')

@bp.route('/training-jobs/<int:job_id>', methods=['GET'])
@api_response()
@monitor_performance('api_get_training_job')
def get_training_job(job_id):
    """获取特定训练任务详情"""
    try:
        job = TrainingJob.query.get(job_id)
        if not job:
            return APIResponse.not_found(f'训练任务 {job_id} 不存在')

        return APIResponse.success(job.to_dict(), '获取训练任务详情成功')
    except Exception as e:
        log_error(e, context=f'获取训练任务详情: {job_id}')
        return APIResponse.internal_error('获取训练任务详情失败')

@bp.route('/system/stats', methods=['GET'])
@api_response()
@monitor_performance('api_system_stats')
@cache_result(expire=60)  # 缓存1分钟
def get_system_stats():
    """获取系统统计信息"""
    try:
        stats = {
            'maps': {
                'total': MapData.query.count(),
                'parsed': MapData.query.filter_by(status='parsed').count(),
                'parsing': MapData.query.filter_by(status='parsing').count(),
                'error': MapData.query.filter_by(status='error').count()
            },
            'annotations': {
                'total': Annotation.query.count()
            },
            'training_jobs': {
                'total': TrainingJob.query.count(),
                'pending': TrainingJob.query.filter_by(status='pending').count(),
                'running': TrainingJob.query.filter_by(status='running').count(),
                'completed': TrainingJob.query.filter_by(status='completed').count(),
                'failed': TrainingJob.query.filter_by(status='failed').count()
            }
        }

        return APIResponse.success(stats, '获取系统统计成功')
    except Exception as e:
        log_error(e, context='获取系统统计')
        return APIResponse.internal_error('获取系统统计失败')

@bp.route('/health', methods=['GET'])
@api_response()
def health_check():
    """健康检查接口"""
    try:
        # 检查数据库连接
        db.session.execute('SELECT 1')

        health_status = {
            'status': 'healthy',
            'database': 'connected',
            'timestamp': db.func.now().scalar().isoformat()
        }

        return APIResponse.success(health_status, '系统运行正常')
    except Exception as e:
        log_error(e, context='健康检查')
        return APIResponse.error('系统异常', 'UNHEALTHY', status_code=503)

@bp.route('/download/<filename>', methods=['GET'])
@monitor_performance('api_download_file')
def download_file(filename):
    """下载生成的文件"""
    try:
        from flask import send_from_directory
        export_dir = os.path.join('static', 'exports')
        return send_from_directory(export_dir, filename, as_attachment=True)
    except Exception as e:
        log_error(f"文件下载失败: {str(e)}", extra={'filename': filename})
        return APIResponse.error("文件下载失败", status_code=404)
