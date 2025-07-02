"""
MCA解析器配置文件
"""

import os
from typing import Dict, Any

class MCAParserConfig:
    """MCA解析器配置类"""

    # 多线程配置
    MAX_WORKERS = int(os.environ.get('MCA_MAX_WORKERS', 4))  # 默认4个线程
    BATCH_SIZE = int(os.environ.get('MCA_BATCH_SIZE', 8))   # 默认每批8个区块

    # 内存优化配置
    MEMORY_BUFFER_SIZE = int(os.environ.get('MCA_BUFFER_SIZE', 10000))  # 缓冲区大小
    SAMPLE_RATE = int(os.environ.get('MCA_SAMPLE_RATE', 4))  # 方块采样率，每N个方块采样1个

    # 高度范围配置
    MIN_HEIGHT = int(os.environ.get('MCA_MIN_HEIGHT', 0))
    MAX_HEIGHT = int(os.environ.get('MCA_MAX_HEIGHT', 384))  # Minecraft 1.18+高度
    HEIGHT_SAMPLE_RATE = int(os.environ.get('MCA_HEIGHT_SAMPLE_RATE', 4))

    # 缓存配置
    ENABLE_CACHE = bool(os.environ.get('MCA_ENABLE_CACHE', True))
    CACHE_DIR = os.environ.get('MCA_CACHE_DIR', 'instance/cache')

    # 性能配置
    SKIP_AIR_BLOCKS = bool(os.environ.get('MCA_SKIP_AIR_BLOCKS', True))
    MAX_BLOCKS_PER_CHUNK = int(os.environ.get('MCA_MAX_BLOCKS_PER_CHUNK', 1000))

    # 预览配置
    PREVIEW_BLOCK_LIMIT = int(os.environ.get('MCA_PREVIEW_LIMIT', 1000))

    # 兼容性配置
    COMPATIBILITY_CHUNK_STEP = int(os.environ.get('MCA_COMPAT_CHUNK_STEP', 4))
    COMPATIBILITY_BLOCK_STEP = int(os.environ.get('MCA_COMPAT_BLOCK_STEP', 8))

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """获取所有配置"""
        return {
            'max_workers': cls.MAX_WORKERS,
            'batch_size': cls.BATCH_SIZE,
            'memory_buffer_size': cls.MEMORY_BUFFER_SIZE,
            'sample_rate': cls.SAMPLE_RATE,
            'min_height': cls.MIN_HEIGHT,
            'max_height': cls.MAX_HEIGHT,
            'height_sample_rate': cls.HEIGHT_SAMPLE_RATE,
            'enable_cache': cls.ENABLE_CACHE,
            'cache_dir': cls.CACHE_DIR,
            'skip_air_blocks': cls.SKIP_AIR_BLOCKS,
            'max_blocks_per_chunk': cls.MAX_BLOCKS_PER_CHUNK,
            'preview_block_limit': cls.PREVIEW_BLOCK_LIMIT,
            'compatibility_chunk_step': cls.COMPATIBILITY_CHUNK_STEP,
            'compatibility_block_step': cls.COMPATIBILITY_BLOCK_STEP
        }

    @classmethod
    def get_optimized_config_for_system(cls) -> Dict[str, Any]:
        """根据系统性能自动调整配置"""
        import psutil

        # 获取系统信息
        cpu_count = psutil.cpu_count()
        memory_gb = psutil.virtual_memory().total / (1024**3)

        # 根据系统资源调整配置
        if memory_gb >= 16:  # 大内存系统
            max_workers = min(cpu_count, 8)
            batch_size = 12
            buffer_size = 20000
            sample_rate = 2
        elif memory_gb >= 8:  # 中等内存系统
            max_workers = min(cpu_count, 6)
            batch_size = 8
            buffer_size = 15000
            sample_rate = 3
        else:  # 低内存系统
            max_workers = min(cpu_count, 4)
            batch_size = 4
            buffer_size = 8000
            sample_rate = 6

        return {
            'max_workers': max_workers,
            'batch_size': batch_size,
            'memory_buffer_size': buffer_size,
            'sample_rate': sample_rate,
            'min_height': cls.MIN_HEIGHT,
            'max_height': cls.MAX_HEIGHT,
            'height_sample_rate': cls.HEIGHT_SAMPLE_RATE,
            'enable_cache': cls.ENABLE_CACHE,
            'cache_dir': cls.CACHE_DIR,
            'skip_air_blocks': cls.SKIP_AIR_BLOCKS,
            'max_blocks_per_chunk': cls.MAX_BLOCKS_PER_CHUNK,
            'preview_block_limit': cls.PREVIEW_BLOCK_LIMIT
        }

# 预定义的性能配置
PERFORMANCE_PRESETS = {
    'fast': {
        'max_workers': 8,
        'batch_size': 16,
        'sample_rate': 8,
        'height_sample_rate': 8,
        'memory_buffer_size': 5000,
        'description': '快速模式：高速度，低精度'
    },
    'balanced': {
        'max_workers': 4,
        'batch_size': 8,
        'sample_rate': 4,
        'height_sample_rate': 4,
        'memory_buffer_size': 10000,
        'description': '平衡模式：中等速度和精度'
    },
    'detailed': {
        'max_workers': 2,
        'batch_size': 4,
        'sample_rate': 2,
        'height_sample_rate': 2,
        'memory_buffer_size': 20000,
        'description': '详细模式：低速度，高精度'
    },
    'memory_optimized': {
        'max_workers': 3,
        'batch_size': 6,
        'sample_rate': 6,
        'height_sample_rate': 6,
        'memory_buffer_size': 5000,
        'description': '内存优化模式：适用于低内存系统'
    }
}
