#!/usr/bin/env python3
"""
AI模型推理模块
"""
import sys
import json
import os
from pathlib import Path
import base64
from io import BytesIO
from PIL import Image
import numpy as np

def generate_dummy_content(model_type, prompt, output_size=(256, 256)):
    """生成模拟内容（实际项目中替换为真实的AI模型）"""
    
    # 根据模型类型生成不同的内容
    if model_type == 'map':
        # 生成地图样式的图像
        img_array = np.random.randint(0, 255, (*output_size, 3), dtype=np.uint8)
        # 添加一些地形特征
        img_array[:, :, 1] = np.maximum(img_array[:, :, 1], 100)  # 增强绿色通道
        
    elif model_type == 'skin':
        # 生成皮肤样式的图像
        img_array = np.random.randint(50, 200, (64, 64, 3), dtype=np.uint8)
        # 模拟皮肤色调
        img_array[:, :, 0] = np.clip(img_array[:, :, 0] + 50, 0, 255)  # 增强红色
        
    elif model_type == 'texture':
        # 生成材质样式的图像
        img_array = np.random.randint(0, 255, (128, 128, 3), dtype=np.uint8)
        # 添加材质图案
        for i in range(0, 128, 16):
            img_array[i:i+2, :, :] = 128
            img_array[:, i:i+2, :] = 128
    
    else:
        img_array = np.random.randint(0, 255, (*output_size, 3), dtype=np.uint8)
    
    return Image.fromarray(img_array)

def image_to_base64(image):
    """将PIL图像转换为base64字符串"""
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def main():
    if len(sys.argv) < 4:
        print("Usage: python inference.py <model_type> <prompt> <model_path>")
        sys.exit(1)
    
    model_type = sys.argv[1]
    prompt = sys.argv[2]
    model_path = sys.argv[3]
    
    try:
        # 生成内容
        generated_image = generate_dummy_content(model_type, prompt)
        
        # 转换为base64
        image_base64 = image_to_base64(generated_image)
        
        # 保存到文件（可选）
        output_dir = Path(f"generated/{model_type}")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"generated_{len(list(output_dir.glob('*.png'))):06d}.png"
        generated_image.save(output_file)
        
        result = {
            'model_type': model_type,
            'prompt': prompt,
            'output_file': str(output_file),
            'image_data': image_base64,
            'status': 'completed'
        }
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        error_result = {
            'error': str(e),
            'status': 'failed'
        }
        print(json.dumps(error_result, indent=2), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()