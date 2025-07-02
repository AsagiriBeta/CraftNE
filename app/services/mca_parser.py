"""
MCA文件解析服务 - 多线程优化版本
"""

import os
import json
import logging
import gc
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Tuple, Optional, Union
from collections import Counter
from dataclasses import dataclass
import time
from mca import Region

# 导入配置
try:
    from config.mca_parser_config import MCAParserConfig, PERFORMANCE_PRESETS
except ImportError:
    # 如果配置文件不存在，使用默认配置
    class MCAParserConfig:
        MAX_WORKERS = 4
        BATCH_SIZE = 8
        MEMORY_BUFFER_SIZE = 10000
        SAMPLE_RATE = 4
        MIN_HEIGHT = 0
        MAX_HEIGHT = 384
        HEIGHT_SAMPLE_RATE = 4
        SKIP_AIR_BLOCKS = True
        MAX_BLOCKS_PER_CHUNK = 1000
        PREVIEW_BLOCK_LIMIT = 1000
        COMPATIBILITY_CHUNK_STEP = 4
        COMPATIBILITY_BLOCK_STEP = 8

    PERFORMANCE_PRESETS = {
        'balanced': {
            'max_workers': 4,
            'batch_size': 8,
            'sample_rate': 4,
            'height_sample_rate': 4,
            'memory_buffer_size': 10000,
            'description': '平衡模式：中等速度和精度'
        }
    }

logger = logging.getLogger(__name__)

@dataclass
class ChunkData:
    """区块数据类"""
    chunk_x: int
    chunk_z: int
    blocks: List[Dict]
    block_types: Dict[str, int]

class MemoryOptimizedBuffer:
    """内存优化的缓冲区"""

    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.buffer = []
        self.lock = threading.Lock()

    def add_blocks(self, blocks: List[Dict]) -> List[Dict]:
        """添加方块数据，返回需要写入缓存的数据"""
        with self.lock:
            self.buffer.extend(blocks)
            if len(self.buffer) >= self.max_size:
                # 返回缓冲区数据并清空
                data_to_write = self.buffer.copy()
                self.buffer.clear()
                gc.collect()  # 强制垃圾回收
                return data_to_write
            return []

    def flush(self) -> List[Dict]:
        """清空缓冲区并返回所有数据"""
        with self.lock:
            data = self.buffer.copy()
            self.buffer.clear()
            return data

def serialize_nbt_data(obj) -> Any:
    """
    将NBT数据转换为可序列化的Python对象（优化版本）
    """
    # 简化序列化，只保留关键信息
    if hasattr(obj, 'value'):
        return serialize_nbt_data(obj.value)
    elif isinstance(obj, dict):
        # 只序列化重要的键值对
        result = {}
        important_keys = {'Name', 'Properties', 'id', 'x', 'y', 'z'}
        for key, value in obj.items():
            if str(key) in important_keys:
                result[str(key)] = serialize_nbt_data(value)
        return result
    elif isinstance(obj, (list, tuple)):
        # 限制列表长度，避免内存爆炸
        return [serialize_nbt_data(item) for item in obj[:100]]
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    else:
        return str(obj) if obj is not None else None

class MCAParser:
    """MCA文件解析器 - ��线程优化版本"""

    def __init__(self, performance_preset: str = 'balanced', custom_config: Dict = None):
        """
        初始化MCA解析器

        Args:
            performance_preset: 性能预设 ('fast', 'balanced', 'detailed', 'memory_optimized')
            custom_config: 自定义配置字典
        """
        self.block_mapping = self._load_block_mapping()

        # 加载配置
        if custom_config:
            config = custom_config
        elif performance_preset in PERFORMANCE_PRESETS:
            config = PERFORMANCE_PRESETS[performance_preset]
            logger.info(f"使用性能预设: {performance_preset} - {config.get('description', '')}")
        else:
            # 根据系统自动优化配置
            config = MCAParserConfig.get_optimized_config_for_system()
            logger.info("使用系统自动优化配置")

        # 设置参数
        self.max_workers = config.get('max_workers', MCAParserConfig.MAX_WORKERS)
        self.batch_size = config.get('batch_size', MCAParserConfig.BATCH_SIZE)
        self.sample_rate = config.get('sample_rate', MCAParserConfig.SAMPLE_RATE)
        self.height_sample_rate = config.get('height_sample_rate', MCAParserConfig.HEIGHT_SAMPLE_RATE)
        self.min_height = config.get('min_height', MCAParserConfig.MIN_HEIGHT)
        self.max_height = config.get('max_height', MCAParserConfig.MAX_HEIGHT)
        self.skip_air_blocks = config.get('skip_air_blocks', MCAParserConfig.SKIP_AIR_BLOCKS)
        self.max_blocks_per_chunk = config.get('max_blocks_per_chunk', MCAParserConfig.MAX_BLOCKS_PER_CHUNK)

        # 创建内存缓冲区
        buffer_size = config.get('memory_buffer_size', MCAParserConfig.MEMORY_BUFFER_SIZE)
        self.memory_buffer = MemoryOptimizedBuffer(buffer_size)

        logger.info(f"解析器配置: workers={self.max_workers}, batch_size={self.batch_size}, "
                   f"sample_rate={self.sample_rate}, buffer_size={buffer_size}")

    @staticmethod
    def _load_block_mapping() -> Dict[str, int]:
        """加载方块ID映射"""
        return {
            'minecraft:air': 0,
            'minecraft:stone': 1,
            'minecraft:grass_block': 2,
            'minecraft:dirt': 3,
            'minecraft:cobblestone': 4,
            'minecraft:oak_planks': 5,
            'minecraft:oak_log': 17,
            'minecraft:oak_leaves': 18,
            'minecraft:water': 9,
            'minecraft:lava': 11,
            'minecraft:sand': 12,
            'minecraft:gravel': 13,
            'minecraft:gold_ore': 14,
            'minecraft:iron_ore': 15,
            'minecraft:coal_ore': 16,
        }

    def parse_file(self, file_path: str, map_data_id: int) -> Dict:
        """
        多线程解析MCA文件
        """
        try:
            logger.info(f"开始多线程解析MCA文件: {file_path}")
            start_time = time.time()

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"MCA文件不存在: {file_path}")

            # 读取MCA文件
            region = Region.from_file(file_path)

            # 收集所有有效的区块坐标
            valid_chunks = self._find_valid_chunks(region)
            logger.info(f"发现 {len(valid_chunks)} 个有效区块")

            if not valid_chunks:
                logger.warning("未找到有效区块")
                return self._empty_result()

            # 分批处理区块
            chunk_batches = [valid_chunks[i:i + self.batch_size]
                           for i in range(0, len(valid_chunks), self.batch_size)]

            # 多线程处理
            all_blocks = []
            total_block_types = Counter()
            processed_chunks = 0

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # 提交所有批处理任务
                future_to_batch = {
                    executor.submit(self._process_chunk_batch, region, batch, map_data_id): batch
                    for batch in chunk_batches
                }

                # 处理完成的任务
                for future in as_completed(future_to_batch):
                    try:
                        batch_result = future.result()
                        if batch_result:
                            processed_chunks += len(batch_result.get('chunks', []))

                            # 将数据添加到内存缓冲区
                            batch_blocks = batch_result.get('blocks', [])
                            buffer_data = self.memory_buffer.add_blocks(batch_blocks)

                            # 如果缓冲区满了，写入缓存
                            if buffer_data:
                                self._write_to_cache_async(map_data_id, buffer_data)

                            # 更新统计信息
                            batch_types = batch_result.get('block_types', {})
                            total_block_types.update(batch_types)

                            # 只保留少量数据用于预览
                            all_blocks.extend(batch_blocks[:100])

                            logger.info(f"已处理 {processed_chunks} 个区块")

                    except Exception as e:
                        logger.error(f"批处理失败: {str(e)}")
                        continue

            # 处��剩余的缓冲区数据
            remaining_data = self.memory_buffer.flush()
            if remaining_data:
                self._write_to_cache_async(map_data_id, remaining_data)

            # 生成Three.js数据
            threejs_result = self._generate_threejs_data_async(map_data_id)

            end_time = time.time()
            logger.info(f"解析完成，耗时: {end_time - start_time:.2f}秒")

            return {
                'success': True,
                'chunk_count': processed_chunks,
                'block_count': sum(total_block_types.values()),
                'block_types': dict(total_block_types),
                'blocks': all_blocks[:1000],  # 只返回前1000个用于预览
                'threejs_success': threejs_result.get('success', False),
                'processing_time': end_time - start_time
            }

        except Exception as e:
            logger.error(f"MCA文件解析失败: {file_path}, 错误: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'chunk_count': 0,
                'block_count': 0,
                'block_types': {},
                'blocks': []
            }
        finally:
            # 清理内存
            gc.collect()

    def _find_valid_chunks(self, region: Region) -> List[Tuple[int, int]]:
        """快速查找有效区块坐标"""
        valid_chunks = []

        # 使用更快的方法检查区块是否存在
        for chunk_x in range(32):
            for chunk_z in range(32):
                try:
                    # 快速检查区块是否存在，不加载整个数据
                    if region.chunk_exists(chunk_x, chunk_z):
                        valid_chunks.append((chunk_x, chunk_z))
                except:
                    # 如果没有chunk_exists方法，尝试获取区块
                    try:
                        chunk = region.get_chunk(chunk_x, chunk_z)
                        if chunk is not None:
                            valid_chunks.append((chunk_x, chunk_z))
                    except:
                        continue

        return valid_chunks

    def _process_chunk_batch(self, region: Region, chunk_coords: List[Tuple[int, int]],
                           map_data_id: int) -> Optional[Dict]:
        """处理一批区块"""
        try:
            batch_blocks = []
            batch_block_types = Counter()
            processed_chunks = []

            for chunk_x, chunk_z in chunk_coords:
                try:
                    chunk = region.get_chunk(chunk_x, chunk_z)
                    if chunk is None:
                        continue

                    # 解析区块（使用优化的方法）
                    chunk_blocks = self._parse_chunk_optimized(chunk, chunk_x, chunk_z)

                    if chunk_blocks:
                        batch_blocks.extend(chunk_blocks)
                        processed_chunks.append((chunk_x, chunk_z))

                        # 统计方块类型
                        for block in chunk_blocks:
                            block_type = block.get('block_type', 'unknown')
                            batch_block_types[block_type] += 1

                except Exception as e:
                    logger.debug(f"跳过区块 ({chunk_x}, {chunk_z}): {str(e)}")
                    continue

            return {
                'chunks': processed_chunks,
                'blocks': batch_blocks,
                'block_types': dict(batch_block_types)
            }

        except Exception as e:
            logger.error(f"批处理失败: {str(e)}")
            return None

    def _parse_chunk_optimized(self, chunk, chunk_x: int, chunk_z: int) -> List[Dict]:
        """优化的区块解析方法"""
        try:
            blocks = []
            block_count = 0

            # 使用配置的采样率和高度范围
            for x in range(0, 16, self.sample_rate):
                for z in range(0, 16, self.sample_rate):
                    for y in range(self.min_height, self.max_height, self.height_sample_rate):
                        try:
                            block = chunk.get_block(x, y, z)

                            if block and hasattr(block, 'id'):
                                block_name = str(block.id)

                                # 根据配置决定是否跳过空气方块
                                if self.skip_air_blocks and 'air' in block_name.lower():
                                    continue

                                block_data = {
                                    'x': chunk_x * 16 + x,
                                    'y': y,
                                    'z': chunk_z * 16 + z,
                                    'block_type': block_name,
                                    'block_id': self.block_mapping.get(block_name, 0)
                                }

                                # 只保存重要的属性
                                if hasattr(block, 'properties') and block.properties:
                                    props = {}
                                    for key, value in block.properties.items():
                                        if key in ['facing', 'waterlogged', 'half']:
                                            props[key] = str(value)
                                    if props:
                                        block_data['properties'] = props

                                blocks.append(block_data)
                                block_count += 1

                                # 限制每个区块的方块数量，防止内存溢出
                                if block_count >= self.max_blocks_per_chunk:
                                    logger.debug(f"区块 ({chunk_x}, {chunk_z}) 达到方块数量限制: {block_count}")
                                    break

                        except Exception:
                            continue

                    if block_count >= self.max_blocks_per_chunk:
                        break
                if block_count >= self.max_blocks_per_chunk:
                    break

            return blocks

        except Exception as e:
            logger.debug(f"区块解析失败 ({chunk_x}, {chunk_z}): {str(e)}")
            return []

    def _write_to_cache_async(self, map_data_id: int, blocks_data: List[Dict]):
        """异步写入缓存"""
        try:
            cache_dir = os.path.join('instance', 'cache')
            os.makedirs(cache_dir, exist_ok=True)

            cache_file = os.path.join(cache_dir, f'map_{map_data_id}_blocks.json')

            # 追加模式写入，避免内存占用过高
            existing_data = []
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except:
                    existing_data = []

            existing_data.extend(blocks_data)

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, separators=(',', ':'))

        except Exception as e:
            logger.error(f"写入缓存失败: {str(e)}")

    def _generate_threejs_data_async(self, map_data_id: int) -> Dict:
        """异步生成Three.js数据"""
        try:
            # 这里可以实现Three.js数据生成逻辑
            # 为了避免阻塞，可以使用Celery任务异步处理
            return {'success': True}
        except Exception as e:
            logger.error(f"生成Three.js数据失败: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _empty_result(self) -> Dict:
        """返��空结果"""
        return {
            'success': False,
            'chunk_count': 0,
            'block_count': 0,
            'block_types': {},
            'blocks': [],
            'error': 'No valid chunks found'
        }

    # ...existing methods for compatibility...
    def _validate_chunk(self, chunk) -> bool:
        """验证区块数据是否有效"""
        try:
            if hasattr(chunk, 'nbt'):
                nbt_data = chunk.nbt
                if 'Level' in nbt_data:
                    level = nbt_data['Level']
                    return 'xPos' in level and 'zPos' in level
                elif 'xPos' in nbt_data and 'zPos' in nbt_data:
                    return True
            return True
        except Exception as e:
            logger.debug(f"区块验证失败: {str(e)}")
            return False

    def _parse_with_compatibility_mode(self, region: Region, file_path: str, map_data_id: int) -> Dict:
        """兼容性模式解析（原有的单线程方法作为后备）"""
        try:
            logger.info("使用兼容性模式解析")
            blocks_data = []
            chunk_count = 0
            block_types = {}

            # 简化的单线程解析，只处理少量区块
            for chunk_x in range(0, 32, 4):  # 每4个区块采样1个
                for chunk_z in range(0, 32, 4):
                    try:
                        chunk = region.get_chunk(chunk_x, chunk_z)
                        if chunk is None:
                            continue

                        if not self._validate_chunk(chunk):
                            continue

                        chunk_count += 1
                        chunk_blocks = self._parse_chunk_safe(chunk, chunk_x, chunk_z)
                        blocks_data.extend(chunk_blocks)

                        for block in chunk_blocks:
                            block_type = block['block_type']
                            block_types[block_type] = block_types.get(block_type, 0) + 1

                    except Exception as e:
                        continue

            # 保存到缓存
            self._save_to_cache(map_data_id, blocks_data)

            return {
                'success': True,
                'chunk_count': chunk_count,
                'block_count': len(blocks_data),
                'block_types': block_types,
                'blocks': blocks_data[:1000],
                'threejs_success': False
            }

        except Exception as e:
            logger.error(f"兼容性模式解析失败: {str(e)}")
            return self._empty_result()

    def _parse_chunk_safe(self, chunk, chunk_x: int, chunk_z: int) -> List[Dict]:
        """安全解析单个区块（原有方法的简化版本）"""
        try:
            blocks = []

            # 简化的方块采样
            for x in range(0, 16, 8):  # 降低采样率
                for z in range(0, 16, 8):
                    for y in range(0, 256, 8):  # 兼容旧版本高度
                        try:
                            block = chunk.get_block(x, y, z)
                            if block and hasattr(block, 'id'):
                                block_name = str(block.id)

                                if 'air' not in block_name.lower():
                                    blocks.append({
                                        'x': chunk_x * 16 + x,
                                        'y': y,
                                        'z': chunk_z * 16 + z,
                                        'block_type': block_name,
                                        'block_id': self.block_mapping.get(block_name, 0)
                                    })
                        except:
                            continue

            return blocks

        except Exception as e:
            logger.debug(f"安全解析失败 ({chunk_x}, {chunk_z}): {str(e)}")
            return []

    def _save_to_cache(self, map_data_id: int, blocks_data: List[Dict]) -> bool:
        """保存解���结果到缓存"""
        try:
            cache_dir = os.path.join('instance', 'cache')
            os.makedirs(cache_dir, exist_ok=True)

            cache_file = os.path.join(cache_dir, f'map_{map_data_id}_blocks.json')

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(blocks_data, f, ensure_ascii=False, separators=(',', ':'))

            logger.info(f"缓存已保存: {cache_file}")
            return True

        except Exception as e:
            logger.error(f"保存��存失败: {str(e)}")
            return False

    def generate_threejs_data(self, file_path: str, map_data_id: int) -> Dict:
        """生成Three.js格式数据（简化版本）"""
        try:
            cache_file = os.path.join('instance', 'cache', f'map_{map_data_id}_blocks.json')

            if not os.path.exists(cache_file):
                return {'success': False, 'error': 'Cache file not found'}

            # 读取缓存数据
            with open(cache_file, 'r', encoding='utf-8') as f:
                blocks_data = json.load(f)

            # 简化的Three.js数据生成
            threejs_data = {
                'geometries': [],
                'materials': [],
                'blocks': []
            }

            # 只处理前1000个方块以避免内存问题
            for block in blocks_data[:1000]:
                threejs_data['blocks'].append({
                    'position': [block['x'], block['y'], block['z']],
                    'type': block['block_type'],
                    'id': block['block_id']
                })

            # 保存Three.js数据
            threejs_cache_file = os.path.join('instance', 'cache', f'map_{map_data_id}_threejs.json')
            with open(threejs_cache_file, 'w', encoding='utf-8') as f:
                json.dump(threejs_data, f, ensure_ascii=False, separators=(',', ':'))

            return {'success': True, 'data': threejs_data}

        except Exception as e:
            logger.error(f"生成Three.js数据失败: {str(e)}")
            return {'success': False, 'error': str(e)}
