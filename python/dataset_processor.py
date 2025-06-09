#!/usr/bin/env python3
"""
数据集处理模块
"""
import sys
import os
import json
from pathlib import Path
from PIL import Image
import numpy as np

def process_images(dataset_path, output_path, target_size=(256, 256)):
    """处理图像数据集"""
    input_dir = Path(dataset_path)
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    processed_count = 0
    supported_formats = {'.png', '.jpg', '.jpeg', '.bmp'}
    
    for img_path in input_dir.rglob('*'):
        if img_path.suffix.lower() in supported_formats:
            try:
                with Image.open(img_path) as img:
                    # 转换为RGB
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # 调整尺寸
                    img_resized = img.resize(target_size, Image.Resampling.LANCZOS)
                    
                    # 保存处理后的图像
                    output_file = output_dir / f"processed_{processed_count:06d}.png"
                    img_resized.save(output_file, 'PNG')
                    processed_count += 1
                    
            except Exception as e:
                print(f"Error processing {img_path}: {e}", file=sys.stderr)
    
    return processed_count

def main():
    if len(sys.argv) < 3:
        print("Usage: python dataset_processor.py <dataset_path> <model_type>")
        sys.exit(1)
    
    dataset_path = sys.argv[1]
    model_type = sys.argv[2]
    
    if not os.path.exists(dataset_path):
        print(f"Dataset path does not exist: {dataset_path}", file=sys.stderr)
        sys.exit(1)
    
    output_path = f"processed_data/{model_type}"
    processed_count = process_images(dataset_path, output_path)
    
    result = {
        'model_type': model_type,
        'input_path': dataset_path,
        'output_path': output_path,
        'processed_files': processed_count,
        'status': 'completed'
    }
    
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()