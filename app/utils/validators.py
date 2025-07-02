"""
文件类型校验工具
"""
from flask import current_app

def allowed_file(filename):
    """判断文件扩展名是否允许"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'mca', 'mcr'})
    return ext in allowed

