#!/usr/bin/env python3
"""
CraftNE应用启动脚本
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 CraftNE - Minecraft地图处理和AI训练平台")
    print("=" * 50)
    print("📍 应用地址: http://127.0.0.1:5000")
    print("📍 本地访问: http://localhost:5000")
    print("🔧 调试模式: 已启用")
    print("=" * 50)
    print("💡 使用 Ctrl+C 停止服务器")
    print("")

    app.run(debug=True, host='127.0.0.1', port=5000)
