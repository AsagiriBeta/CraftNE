import os
import json
import csv
from io import TextIOBase
from data_loader import MinecraftDataLoader

def preprocess_data(folders, output_folder, output_format='json'):
    # 新增文件夹存在性检查
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # 统一处理输入参数为列表
    if not isinstance(folders, list):
        folders = [folders]
    
    all_data = []
    for folder in folders:
        # 处理可能的文件路径对象
        folder_path = folder if isinstance(folder, str) else folder.name
        if not os.path.isdir(folder_path):
            continue
            
        loader = MinecraftDataLoader(folder_path)
        data = loader.load_data()
        all_data.extend(data)
    
    # 生成输出文件路径
    output_file = os.path.join(output_folder, f"processed_data.{output_format}")
    
    # 数据持久化存储
    if output_format == 'json':
        with open(output_file, 'w', encoding='utf-8') as f:  # type: TextIOBase
            json.dump(all_data, f, indent=2)
    elif output_format == 'csv':
        raise ValueError("CSV格式不支持当前数据结构，请使用JSON格式")
    else:
        raise ValueError(f"不支持的格式: {output_format}")
    
    return f"预处理完成，共处理{len(all_data)}条记录，输出文件: {output_file}"