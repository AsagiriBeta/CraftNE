"""
MCA解析器使用示例
演示如何使用多线程优化的MCA文件解析器
"""

import os
import logging
from app.services.mca_parser import MCAParser

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def demo_basic_usage():
    """基本使用示例"""
    print("=== 基本使用示例 ===")

    # 创建解析器实例 - 使用默认的平衡模式
    parser = MCAParser()

    # 查找MCA文件
    mca_files = []
    upload_dir = "app/static/uploads"
    if os.path.exists(upload_dir):
        for file in os.listdir(upload_dir):
            if file.endswith('.mca'):
                mca_files.append(os.path.join(upload_dir, file))

    if not mca_files:
        print("未找到MCA文件，请先上传一些MCA文件到 app/static/uploads 目录")
        return

    # 解析第一个MCA文件
    mca_file = mca_files[0]
    print(f"解析文件: {mca_file}")

    result = parser.parse_file(mca_file, map_data_id=1)

    if result['success']:
        print(f"✅ 解析成功!")
        print(f"   区块数量: {result['chunk_count']}")
        print(f"   方块数量: {result['block_count']}")
        print(f"   处理时间: {result.get('processing_time', 0):.2f}秒")
        print(f"   方块类型数: {len(result['block_types'])}")

        # 显示前5种最常见的方块类型
        if result['block_types']:
            sorted_types = sorted(result['block_types'].items(), key=lambda x: x[1], reverse=True)
            print("   主要方块类型:")
            for block_type, count in sorted_types[:5]:
                print(f"     {block_type}: {count}")
    else:
        print(f"❌ 解析失败: {result.get('error', '未知错误')}")

def demo_performance_presets():
    """性能预设示例"""
    print("\n=== 性能预设示例 ===")

    # 查找MCA文件
    mca_files = []
    upload_dir = "app/static/uploads"
    if os.path.exists(upload_dir):
        for file in os.listdir(upload_dir):
            if file.endswith('.mca'):
                mca_files.append(os.path.join(upload_dir, file))

    if not mca_files:
        print("未找到MCA文件")
        return

    mca_file = mca_files[0]
    presets = ['fast', 'balanced', 'detailed', 'memory_optimized']

    for preset in presets:
        print(f"\n--- 测试 {preset} 模式 ---")
        parser = MCAParser(performance_preset=preset)

        result = parser.parse_file(mca_file, map_data_id=2)

        if result['success']:
            print(f"✅ {preset} 模式 - 耗时: {result.get('processing_time', 0):.2f}秒")
            print(f"   区块: {result['chunk_count']}, 方块: {result['block_count']}")
        else:
            print(f"❌ {preset} 模式失败: {result.get('error', '未知错误')}")

def demo_custom_config():
    """自定义配置示例"""
    print("\n=== 自定义配置示例 ===")

    # 自定义配置：高性能但内存使用较少
    custom_config = {
        'max_workers': 6,           # 6个线程
        'batch_size': 12,           # 每批12个区块
        'sample_rate': 2,           # 每2个方块采样1个（高精度）
        'height_sample_rate': 2,    # 高度采样率
        'memory_buffer_size': 8000, # 较小的缓冲区
        'skip_air_blocks': True,    # 跳过空气方块
        'max_blocks_per_chunk': 500 # 限制每个区块的方块数
    }

    parser = MCAParser(custom_config=custom_config)

    # 查找MCA文件
    mca_files = []
    upload_dir = "app/static/uploads"
    if os.path.exists(upload_dir):
        for file in os.listdir(upload_dir):
            if file.endswith('.mca'):
                mca_files.append(os.path.join(upload_dir, file))

    if not mca_files:
        print("未找到MCA文件")
        return

    mca_file = mca_files[0]
    result = parser.parse_file(mca_file, map_data_id=3)

    if result['success']:
        print(f"✅ 自定义配置成功!")
        print(f"   处理时间: {result.get('processing_time', 0):.2f}秒")
        print(f"   区块数量: {result['chunk_count']}")
        print(f"   方块数量: {result['block_count']}")
    else:
        print(f"❌ 自定义配置失败: {result.get('error', '未知错误')}")

def demo_memory_monitoring():
    """内存监控示例"""
    print("\n=== 内存监控示例 ===")

    try:
        import psutil
        import time

        # 监控解析过程中的内存使用
        process = psutil.Process()

        # 获取初始内存使用
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"初始内存使用: {initial_memory:.2f} MB")

        # 使用内存优化模式
        parser = MCAParser(performance_preset='memory_optimized')

        # 查找MCA文件
        mca_files = []
        upload_dir = "app/static/uploads"
        if os.path.exists(upload_dir):
            for file in os.listdir(upload_dir):
                if file.endswith('.mca'):
                    mca_files.append(os.path.join(upload_dir, file))

        if not mca_files:
            print("未找到MCA文件")
            return

        mca_file = mca_files[0]

        # 开始解析
        start_time = time.time()
        result = parser.parse_file(mca_file, map_data_id=4)
        end_time = time.time()

        # 获取峰值内存使用
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory

        print(f"解析完成:")
        print(f"   耗时: {end_time - start_time:.2f}秒")
        print(f"   峰值内存: {peak_memory:.2f} MB")
        print(f"   内存增加: {memory_increase:.2f} MB")

        if result['success']:
            print(f"   解析结果: {result['chunk_count']} 区块, {result['block_count']} 方块")

    except ImportError:
        print("需要安装psutil包来监控内存使用: pip install psutil")

def main():
    """主函数"""
    print("MCA解析器多线程优化演示")
    print("=" * 50)

    try:
        # 基本使用
        demo_basic_usage()

        # 性能预设对比
        demo_performance_presets()

        # 自定义配置
        demo_custom_config()

        # 内存监控
        demo_memory_monitoring()

    except Exception as e:
        print(f"演示过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
