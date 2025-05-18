import os
import re
from collections import Counter
from mca import Region

class MinecraftDataLoader:
    def __init__(self, data_folder):
        self.data_folder = data_folder

    @staticmethod
    def analyze_mca_file(file_path):
        try:
            region = Region.from_file(file_path)
            # 初始化必要变量
            block_counter = Counter()
            chunk_count = 0
            filename = os.path.basename(file_path)
            if match := re.match(r"^r\.(-?\d+)\.(-?\d+)\.mca$", os.path.basename(file_path)):
                region_x, region_z = map(int, match.groups())
                region_info = {"区域坐标X": region_x, "区域坐标Z": region_z}
            else:
                return {"错误": "无效的区域文件命名格式"}
            # 新增基于区域坐标的区块遍历逻辑
            for local_x in range(32):
                for local_z in range(32):
                    chunk_x = region_x * 32 + local_x
                    chunk_z = region_z * 32 + local_z
                    chunk_count += 1
                    chunk = region.get_chunk(chunk_x, chunk_z)
                    for block_x in range(16):
                        for block_z in range(16):
                            for y in range(-64, 320):
                                # 使用相对坐标获取区块内方块
                                try:
                                    # 使用相对坐标获取区块内方块
                                    block = chunk.get_block(block_x, y, block_z)
                                    if block is not None:  # 检查方块是否有效
                                        key = block.id
                                        block_counter[key] += 1
                                except Exception:
                                    continue

            # 重构统计数据结构，按id聚合
            block_stats = [
                {
                    "id": block_id,
                    "properties": None,  # 按需求暂时不区分属性
                    "count": count
                }
                for block_id, count in block_counter.items()
            ]

            return {
                "文件名": filename,
                **region_info,
                "区块数量": chunk_count,
                "方块类型统计": block_stats
            }
        except Exception as e:
            return {"错误": f"{str(e)}"}