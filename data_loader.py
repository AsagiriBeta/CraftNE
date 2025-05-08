import os
import json
# 修改点：从独立文件导入方块ID映射表
from block_id_map import BLOCK_ID_MAP

class MinecraftDataLoader:
    def __init__(self, data_folder, cube_size=16):
        self.data_folder = data_folder
        self.block_map = BLOCK_ID_MAP  # 使用导入的映射表
        self.cube_size = cube_size
        
    def load_data(self):
        # 修改加载逻辑以返回带方块名称的数据结构
        data = []
        for filename in os.listdir(self.data_folder):
            if filename.endswith('.json'):
                with open(os.path.join(self.data_folder, filename)) as f:
                    raw_data = json.load(f)
                    # 将原始数值转换为方块名称
                    processed = self._process_chunk(raw_data)
                    data.append(processed)
        return data
        
    def _process_chunk(self, chunk_data):
        # 处理单个区块数据
        if 'Level' in chunk_data and 'Sections' in chunk_data['Level']:
            for section in chunk_data['Level']['Sections']:
                if 'Blocks' in section:
                    # 应用方块ID映射
                    section['BlockNames'] = [self.block_map.get(b, "minecraft:air") for b in section['Blocks']]
        return chunk_data

    def create_cube(self, chunk):
        size = self.cube_size
        cube = [[[0 for _ in range(size)] for _ in range(size)] for _ in range(size)]
        
        # 修改：支持新版JSON结构，遍历所有Section的Blocks
        sections = chunk.get('Sections', [])
        for section in sections:
            blocks = section.get('Blocks', [])
            if not blocks:
                continue
                
            # 获取当前Section的Y轴偏移量（每个Section包含16层）
            section_y = section.get('Y', 0) * 16  # 修改：乘以16获取实际Y轴偏移
            
            # 遍历当前Section的方块数据
            for index, block_id in enumerate(blocks):
                # 计算三维坐标（修改为正确公式）
                x = index % 16  # X轴每16个单位循环
                y = (index // 16) % 16 + section_y  # Y轴每16个单位循环并加上偏移量
                z = index // (16 * 16)  # Z轴每256个单位循环
                
                # 填充立方体数据（修改为直接使用cube_size进行归一化）
                if 0 <= x < size and 0 <= y < size and 0 <= z < size:
                    cube[x][y][z] = block_id
        
        return cube

    def normalize_position(self, x, y, z):
        size = self.cube_size
        return (
            (x % size + size) % size,
            (y % size + size) % size,
            (z % size + size) % size
        )