import gradio as gr
from train_model import train_model
from inference import generate_map
import socket
import os
import csv
from collections import Counter
from nbtlib import nbt
from data_preprocessor import preprocess_data  # 导入独立的数据预处理模块
from MTDCmca import process_files  # 新增: 导入解压处理模块
import os


def get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except (socket.error, OSError):
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def get_flagged_csv_files():
    flagged_dir = os.path.join('.gradio', 'flagged')
    if not os.path.exists(flagged_dir):
        return []
    return [f for f in os.listdir(flagged_dir) if f.endswith('.csv')]

def train_and_generate(input_data_files, config_file, description, epochs, learning_rate, batch_size):
    try:
        if config_file:
            config_path = os.path.join('.gradio', 'flagged', config_file)
            if not os.path.exists(config_path):  # 新增路径检查
                return f"配置文件不存在: {config_path}"
                
            with open(config_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    epochs = int(row.get('训练轮数 (Epochs)', epochs))
                    learning_rate = float(row.get('学习率 (Learning Rate)', learning_rate))
                    batch_size = int(row.get('批量大小 (Batch Size)', batch_size))
                    break
    except Exception as e:
        return f"配置解析失败: {str(e)}"

    # 输入验证
    if not input_data_files:
        return "未选择任何训练数据"
        
    input_folders = list({os.path.dirname(f) for f in input_data_files})
    model_path = 'models/craftne_model.pth'
    train_model(input_folders, model_path, epochs, learning_rate, batch_size)
    generate_map(model_path, description)
    return '生成的地图已保存为 generated_map.nbt'

def show_mca_info(selected_mca):  # 删除: , folders
    try:
        
        # 路径处理逻辑保持不变
        region_file_path = os.path.normpath(selected_mca)
        
        if not os.path.isfile(region_file_path):
            raise FileNotFoundError(f"找不到文件: {region_file_path}")
            
        region_file = nbt.load(region_file_path)
        return {
            "文件名": os.path.basename(region_file_path),
            "区块数量": len(region_file['Chunks']),
            "方块类型统计": Counter(
                block['id'].value 
                for chunk in region_file['Chunks'] 
                for block in chunk['Blocks']
            )
        }
    except Exception as e:
        return {"错误": str(e)}

def load_and_preview(folders):
    valid_files = []
    seen_files = set()
    
    if folders is None:
        return {"valid_files": []}, gr.update(choices=[], value=None)
    
    if folders:
        for folder in folders:
            # 统一处理为路径字符串（兼容不同平台）
            folder_path = folder if isinstance(folder, str) else folder.name
            
            # 递归查找文件夹下所有.mca文件
            for root, _, filenames in os.walk(folder_path):
                for filename in filenames:
                    if filename.endswith('.mca'):
                        full_path = os.path.join(root, filename)
                        if full_path not in seen_files:
                            valid_files.append(full_path)
                            seen_files.add(full_path)

    return {"valid_files": valid_files}, gr.update(
        choices=[(os.path.basename(f), f) for f in valid_files],
        value=valid_files[0] if valid_files else None
    )

def launch_ui():
    local_ip = get_local_ip()
    print(f"Web UI 管理地址: http://{local_ip}:7860")

    with gr.Blocks() as demo:
        with gr.Column():
            # 新增: MCA 解压标签页 (移动到最前面)
            with gr.Tab("MCA 解压"):
                mca_upload = gr.File(
                    label="上传 MCA 文件（可多选）",
                    file_count="multiple",
                    file_types=[".mca"],
                    height=100
                )
                output_dir = gr.Textbox(label="输出目录")
                convert_json = gr.Checkbox(label="生成 JSON 文件", value=False)
                threads = gr.Slider(minimum=1, maximum=16, step=1, value=4, label="线程数")
                decompress_button = gr.Button("开始解压")
                decompress_output = gr.Textbox(label="解压结果")

                decompress_button.click(
                    lambda files, out_dir, json_flag, thread_num: decompress_mca(
                        files, out_dir, json_flag, thread_num
                    ),
                    inputs=[mca_upload, output_dir, convert_json, threads],
                    outputs=decompress_output
                )

            # 数据预处理标签页 (原位置保持不变)
            with gr.Tab("数据预处理"):
                data_files = gr.File(
                    label="加载包含.mca的文件夹",
                    file_count="directory",
                    file_types=None,
                    height=100
                )
                mca_selector = gr.Dropdown(label="选择.mca文件", interactive=True)
                preview_area = gr.JSON(label="文件预览信息")
                processed_output_folder = gr.Textbox(label="处理后训练集输出地址")
                preprocess_button = gr.Button("预处理数据")
                preprocess_output = gr.Textbox(label="预处理结果")

                data_files.change(
                    load_and_preview,
                    inputs=data_files,
                    outputs=[gr.JSON(visible=False), mca_selector]
                )

                mca_selector.change(
                    show_mca_info,
                    inputs=[mca_selector],  # 删除: , data_files
                    outputs=preview_area
                )

                preprocess_button.click(
                    lambda files, output: preprocess_data(
                        [f.name for f in files] if isinstance(files, list) else [],  # 修改为提取文件对象的实际路径
                        output
                    ),
                    inputs=[data_files, processed_output_folder],
                    outputs=preprocess_output
                )

            with gr.Tab("训练参数"):
                config_file = gr.Dropdown(label="选择配置文件", choices=get_flagged_csv_files())
                description = gr.Textbox(label="描述")
                epochs = gr.Slider(minimum=1, maximum=100, step=1, label="训练轮数 (Epochs)")
                learning_rate = gr.Slider(minimum=0.0001, maximum=0.01, step=0.0001, label="学习率 (Learning Rate)")
                batch_size = gr.Slider(minimum=16, maximum=128, step=16, label="批量大小 (Batch Size)")
                train_button = gr.Button("开始训练")
                train_output = gr.Textbox(label="训练结果")

            with gr.Tab("推理部署"):
                model_path = gr.Textbox(label="模型路径", value="models/craftne_model.pth")
                generate_button = gr.Button("开始生成")
                generate_output = gr.Textbox(label="生成结果")

    demo.launch(server_name=local_ip)


# 新增: 解压处理函数
def decompress_mca(mca_files, output_dir, convert_json, threads):
    if not mca_files:
        return "未选择任何 MCA 文件"
    if not output_dir:
        return "未指定输出目录"
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    try:
        mca_paths = [f.name for f in mca_files]
        elapsed = process_files(mca_paths, output_dir, convert_json, threads)
        result = f"解压完成，耗时: {elapsed:.2f} 秒\n输出目录: {output_dir}"
        # 如果启用了JSON转换，检查转换结果
        if convert_json:
            json_count = len([f for f in os.listdir(output_dir) if f.endswith('.json')])
            result += f"\n成功生成 {json_count} 个 JSON 文件"
        return result
    except Exception as e:
        return f"解压失败: {str(e)}"


if __name__ == "__main__":
    launch_ui()














