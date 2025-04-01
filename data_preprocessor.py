import os
import json
import csv
from io import TextIOBase
from data_loader import MinecraftDataLoader

def preprocess_data(folders, output_folder, output_format='json'):
    for folder in folders:
        loader = MinecraftDataLoader(folder)
        data = loader.load_data()
        output_file = os.path.join(output_folder, os.path.basename(folder) + '.' + output_format)

        if output_format == 'json':
            with open(output_file, 'w', encoding='utf-8') as f:  # type: TextIOBase
                json.dump(data, f)
        elif output_format == 'csv':
            with open(output_file, 'w', newline='', encoding='utf-8') as f:  # type: TextIOBase
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        else:
            raise ValueError(f"不支持的格式: {output_format}")
    
    return "预处理完成"