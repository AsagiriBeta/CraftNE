"""
OBJ模型导出服务
将Minecraft地图数据导出为OBJ 3D模型文件
"""

import os
import json
import logging
from typing import Dict, List, Tuple
from app.models.map_data import MapData

logger = logging.getLogger(__name__)

class OBJExporter:
    """OBJ模型导出器"""

    def __init__(self):
        self.vertices = []
        self.faces = []
        self.materials = {}
        self.vertex_index = 1  # OBJ文件中顶点索引从1开始

    def export_map_to_obj(self, map_data: MapData) -> str:
        """
        将地图数据导出为OBJ文件

        Args:
            map_data: 地图数据对象

        Returns:
            OBJ文件路径
        """
        try:
            # 清空之前的数据
            self.vertices = []
            self.faces = []
            self.materials = {}
            self.vertex_index = 1

            # 读取Three.js缓存数据
            threejs_cache_path = os.path.join('models_cache', f'threejs_data_{map_data.id}.json')

            if not os.path.exists(threejs_cache_path):
                logger.error(f"Three.js缓存文件不存在: {threejs_cache_path}")
                return None

            with open(threejs_cache_path, 'r') as f:
                threejs_data = json.load(f)

            blocks = threejs_data.get('blocks', [])
            if not blocks:
                logger.warning("没有找到方块数据")
                return None

            logger.info(f"开始导出OBJ模型，方块数量: {len(blocks)}")

            # 生成材质库
            self._generate_materials(threejs_data.get('materials', {}))

            # 处理每个方块
            for i, block in enumerate(blocks):
                if i % 1000 == 0:
                    logger.info(f"处理进度: {i}/{len(blocks)}")

                self._add_block_to_obj(block)

            # 生成输出文件路径
            output_dir = os.path.join('static', 'exports')
            os.makedirs(output_dir, exist_ok=True)

            obj_filename = f"map_{map_data.id}_{map_data.filename.replace('.mca', '')}.obj"
            mtl_filename = f"map_{map_data.id}_{map_data.filename.replace('.mca', '')}.mtl"

            obj_path = os.path.join(output_dir, obj_filename)
            mtl_path = os.path.join(output_dir, mtl_filename)

            # 写入OBJ文件
            self._write_obj_file(obj_path, mtl_filename)

            # 写入材质文件
            self._write_mtl_file(mtl_path)

            logger.info(f"OBJ模型导出完成: {obj_path}")
            return obj_path

        except Exception as e:
            logger.error(f"导出OBJ模型失败: {str(e)}")
            return None

    def _generate_materials(self, materials_config: Dict):
        """生成材质配置"""
        for block_type, config in materials_config.items():
            self.materials[block_type] = {
                'name': block_type.replace('minecraft:', '').replace(':', '_'),
                'color': config.get('color', '#CCCCCC'),
                'transparent': config.get('transparent', False),
                'emissive': config.get('emissive', False)
            }

    def _add_block_to_obj(self, block: Dict):
        """将单个方块添加到OBJ数据中"""
        x, y, z = block['x'], block['y'], block['z']
        block_type = block['block_type']

        # 定义立方体的8个顶点（相对于方块中心）
        cube_vertices = [
            (x-0.5, y-0.5, z-0.5),  # 0: 左下后
            (x+0.5, y-0.5, z-0.5),  # 1: 右下后
            (x+0.5, y+0.5, z-0.5),  # 2: 右上后
            (x-0.5, y+0.5, z-0.5),  # 3: 左上后
            (x-0.5, y-0.5, z+0.5),  # 4: 左下前
            (x+0.5, y-0.5, z+0.5),  # 5: 右下前
            (x+0.5, y+0.5, z+0.5),  # 6: 右上前
            (x-0.5, y+0.5, z+0.5),  # 7: 左上前
        ]

        # 添加顶点
        start_vertex_index = self.vertex_index
        for vertex in cube_vertices:
            self.vertices.append(vertex)
            self.vertex_index += 1

        # 定义立方体的6个面（使用顶点索引）
        # 每个面使用两个三角形
        cube_faces = [
            # 后面 (z-)
            (start_vertex_index, start_vertex_index+1, start_vertex_index+2, start_vertex_index+3),
            # 前面 (z+)
            (start_vertex_index+4, start_vertex_index+7, start_vertex_index+6, start_vertex_index+5),
            # 左面 (x-)
            (start_vertex_index, start_vertex_index+3, start_vertex_index+7, start_vertex_index+4),
            # 右面 (x+)
            (start_vertex_index+1, start_vertex_index+5, start_vertex_index+6, start_vertex_index+2),
            # 下面 (y-)
            (start_vertex_index, start_vertex_index+4, start_vertex_index+5, start_vertex_index+1),
            # 上面 (y+)
            (start_vertex_index+3, start_vertex_index+2, start_vertex_index+6, start_vertex_index+7),
        ]

        # 添加面（每个四边形分成两个三角形）
        material_name = self.materials.get(block_type, {}).get('name', 'default')

        for face in cube_faces:
            # 将四边形分成两个三角形
            self.faces.append({
                'vertices': [face[0], face[1], face[2]],
                'material': material_name
            })
            self.faces.append({
                'vertices': [face[0], face[2], face[3]],
                'material': material_name
            })

    def _write_obj_file(self, obj_path: str, mtl_filename: str):
        """写入OBJ文件"""
        with open(obj_path, 'w') as f:
            # 写入文件头
            f.write("# CraftNE Minecraft Map Export\n")
            f.write("# Generated by CraftNE OBJ Exporter\n\n")

            # 引用材质库
            f.write(f"mtllib {mtl_filename}\n\n")

            # 写入顶点
            f.write("# Vertices\n")
            for vertex in self.vertices:
                f.write(f"v {vertex[0]:.6f} {vertex[1]:.6f} {vertex[2]:.6f}\n")
            f.write("\n")

            # 按材质分组写入面
            current_material = None
            f.write("# Faces\n")

            for face in self.faces:
                if face['material'] != current_material:
                    current_material = face['material']
                    f.write(f"usemtl {current_material}\n")

                vertices = face['vertices']
                f.write(f"f {vertices[0]} {vertices[1]} {vertices[2]}\n")

    def _write_mtl_file(self, mtl_path: str):
        """写入材质文件"""
        with open(mtl_path, 'w') as f:
            f.write("# CraftNE Minecraft Materials\n")
            f.write("# Generated by CraftNE OBJ Exporter\n\n")

            for block_type, material in self.materials.items():
                material_name = material['name']
                color = material['color']

                # 将十六进制颜色转换为RGB
                if color.startswith('#'):
                    color = color[1:]

                try:
                    r = int(color[0:2], 16) / 255.0
                    g = int(color[2:4], 16) / 255.0
                    b = int(color[4:6], 16) / 255.0
                except:
                    r, g, b = 0.8, 0.8, 0.8  # 默认灰色

                f.write(f"newmtl {material_name}\n")
                f.write(f"Kd {r:.6f} {g:.6f} {b:.6f}\n")  # 漫反射颜色
                f.write(f"Ka {r*0.3:.6f} {g*0.3:.6f} {b*0.3:.6f}\n")  # 环境光颜色

                if material['emissive']:
                    f.write(f"Ke {r*0.5:.6f} {g*0.5:.6f} {b*0.5:.6f}\n")  # 发光颜色

                if material['transparent']:
                    f.write("d 0.7\n")  # 透明度
                else:
                    f.write("d 1.0\n")

                f.write("illum 2\n")  # 光照模型
                f.write("\n")

    def export_region_to_obj(self, map_data: MapData, min_coords: Tuple[int, int, int],
                            max_coords: Tuple[int, int, int]) -> str:
        """
        导出地图指定区域为OBJ文件

        Args:
            map_data: 地图数据对象
            min_coords: 最小坐标 (x, y, z)
            max_coords: 最大坐标 (x, y, z)

        Returns:
            OBJ文件路径
        """
        try:
            # 读取Three.js缓存数据
            threejs_cache_path = os.path.join('models_cache', f'threejs_data_{map_data.id}.json')

            if not os.path.exists(threejs_cache_path):
                return None

            with open(threejs_cache_path, 'r') as f:
                threejs_data = json.load(f)

            all_blocks = threejs_data.get('blocks', [])

            # 过滤指定区域的方块
            min_x, min_y, min_z = min_coords
            max_x, max_y, max_z = max_coords

            region_blocks = [
                block for block in all_blocks
                if (min_x <= block['x'] <= max_x and
                    min_y <= block['y'] <= max_y and
                    min_z <= block['z'] <= max_z)
            ]

            if not region_blocks:
                logger.warning("指定区域没有方块数据")
                return None

            # 创建临时的Three.js数据
            region_data = {
                'blocks': region_blocks,
                'materials': threejs_data.get('materials', {})
            }

            # 临时保存区域数据
            temp_cache_path = os.path.join('models_cache', f'temp_region_{map_data.id}.json')
            with open(temp_cache_path, 'w') as f:
                json.dump(region_data, f)

            # 生成OBJ文件
            self.vertices = []
            self.faces = []
            self.materials = {}
            self.vertex_index = 1

            self._generate_materials(region_data['materials'])

            for block in region_blocks:
                self._add_block_to_obj(block)

            # 生成输出文件
            output_dir = os.path.join('static', 'exports')
            os.makedirs(output_dir, exist_ok=True)

            obj_filename = f"map_{map_data.id}_region_{min_x}_{min_y}_{min_z}_to_{max_x}_{max_y}_{max_z}.obj"
            mtl_filename = obj_filename.replace('.obj', '.mtl')

            obj_path = os.path.join(output_dir, obj_filename)
            mtl_path = os.path.join(output_dir, mtl_filename)

            self._write_obj_file(obj_path, mtl_filename)
            self._write_mtl_file(mtl_path)

            # 清理临时文件
            if os.path.exists(temp_cache_path):
                os.remove(temp_cache_path)

            logger.info(f"区域OBJ模型导出完成: {obj_path}")
            return obj_path

        except Exception as e:
            logger.error(f"导出区域OBJ模型失败: {str(e)}")
            return None
