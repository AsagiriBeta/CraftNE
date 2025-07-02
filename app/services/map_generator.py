"""地图生成服务模块"""

import logging
from typing import Dict, Any, Optional
import uuid
import os
from datetime import datetime

from app.utils.logging_config import log_info, log_error


class MapGenerator:
    """地图生成器类，负责根据提示词生成地图"""

    def __init__(self):
        """初始化地图生成器"""
        self.logger = logging.getLogger(__name__)

    def generate(self, prompt: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        根据提示词生成地图

        Args:
            prompt: 地图生成提示词
            parameters: 生成参数

        Returns:
            生成结果字典，包含地图数据和元信息
        """
        try:
            if parameters is None:
                parameters = {}

            log_info(f"开始生成地图", {
                'prompt': prompt,
                'parameters': parameters
            })

            # 生成唯一ID
            map_id = str(uuid.uuid4())

            # 默认参数
            default_params = {
                'size': parameters.get('size', '256x256'),
                'biome': parameters.get('biome', 'plains'),
                'structures': parameters.get('structures', True),
                'seed': parameters.get('seed', None)
            }

            # 模拟地图生成过程
            # 这里可以集成实际的地图生成算法
            map_data = self._generate_map_data(prompt, default_params)

            result = {
                'map_id': map_id,
                'prompt': prompt,
                'parameters': default_params,
                'map_data': map_data,
                'created_at': datetime.now().isoformat(),
                'status': 'success'
            }

            log_info(f"地图生成完成", {
                'map_id': map_id,
                'prompt': prompt
            })

            return result

        except Exception as e:
            log_error(e, context=f"地图生成失败: {prompt}")
            raise

    def _generate_map_data(self, prompt: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        内部方法：生成实际的地图数据

        Args:
            prompt: 提示词
            parameters: 生成参数

        Returns:
            地图数据字典
        """
        # 解析大小参数
        size_str = parameters.get('size', '256x256')
        try:
            width, height = map(int, size_str.split('x'))
        except ValueError:
            width, height = 256, 256

        # 生成基础地图数据结构
        map_data = {
            'dimensions': {
                'width': width,
                'height': height
            },
            'biome': parameters.get('biome', 'plains'),
            'structures': parameters.get('structures', True),
            'seed': parameters.get('seed'),
            'blocks': self._generate_blocks(width, height, parameters),
            'metadata': {
                'generator_version': '1.0.0',
                'prompt_hash': hash(prompt),
                'generation_method': 'procedural'
            }
        }

        return map_data

    def _generate_blocks(self, width: int, height: int, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成方块数据

        Args:
            width: 地图宽度
            height: 地图高度
            parameters: 生成参数

        Returns:
            方块数据字典
        """
        biome = parameters.get('biome', 'plains')

        # 根据生物群系选择基础方块类型
        biome_blocks = {
            'plains': {'grass': 60, 'dirt': 30, 'stone': 10},
            'desert': {'sand': 70, 'sandstone': 20, 'stone': 10},
            'forest': {'grass': 40, 'dirt': 35, 'wood': 15, 'leaves': 10},
            'mountain': {'stone': 60, 'dirt': 25, 'gravel': 15},
            'ocean': {'water': 80, 'sand': 15, 'stone': 5}
        }

        blocks = biome_blocks.get(biome, biome_blocks['plains'])

        # 生成简化的方块分布
        block_data = {
            'total_blocks': width * height,
            'distribution': blocks,
            'layers': self._generate_layers(width, height, biome)
        }

        return block_data

    def _generate_layers(self, width: int, height: int, biome: str) -> list:
        """
        生成地层数据

        Args:
            width: 地图宽度
            height: 地图高度
            biome: 生物群系

        Returns:
            地层列表
        """
        # 生成基础地层结构
        layers = []

        if biome == 'ocean':
            layers = [
                {'y': 0, 'block': 'bedrock', 'thickness': 1},
                {'y': 1, 'block': 'stone', 'thickness': 50},
                {'y': 51, 'block': 'dirt', 'thickness': 10},
                {'y': 61, 'block': 'sand', 'thickness': 3},
                {'y': 64, 'block': 'water', 'thickness': 20}
            ]
        elif biome == 'mountain':
            layers = [
                {'y': 0, 'block': 'bedrock', 'thickness': 1},
                {'y': 1, 'block': 'stone', 'thickness': 80},
                {'y': 81, 'block': 'dirt', 'thickness': 5},
                {'y': 86, 'block': 'grass', 'thickness': 1}
            ]
        else:  # plains, forest, desert等
            surface_block = 'grass' if biome in ['plains', 'forest'] else 'sand'
            layers = [
                {'y': 0, 'block': 'bedrock', 'thickness': 1},
                {'y': 1, 'block': 'stone', 'thickness': 60},
                {'y': 61, 'block': 'dirt', 'thickness': 3},
                {'y': 64, 'block': surface_block, 'thickness': 1}
            ]

        return layers
