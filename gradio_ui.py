import gradio as gr
from train_model import train_model
from inference import generate_map
import socket
import os
import csv
from collections import Counter
from nbtlib import nbt
from data_preprocessor import preprocess_data  # 导入独立的数据预处理模块


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

def train_and_generate(input_data_folder, config_file, description, epochs, learning_rate, batch_size):
    try:
        if config_file:
            config_path = os.path.join('.gradio', 'flagged', config_file)
            with open(config_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 优先使用CSV中的配置参数
                    epochs = int(row.get('训练轮数 (Epochs)', epochs))
                    learning_rate = float(row.get('学习率 (Learning Rate)', learning_rate))
                    batch_size = int(row.get('批量大小 (Batch Size)', batch_size))
                    break  # 只读取第一行配置
    except Exception as e:
        return f"配置解析失败: {str(e)}"

    model_path = 'models/craftne_model.pth'
    train_model(input_data_folder, model_path, epochs, learning_rate, batch_size)
    generate_map(model_path, description)
    return '生成的地图已保存为 generated_map.nbt'

def load_and_preview(folders):
    # 只显示文件夹名称，而不是完整路径
    folder_list = [os.path.basename(f) for f in folders]
    return {"folders": folder_list}, gr.update(choices=folder_list)

def update_mca_list(selected_folder, folders):
    # 根据选择的文件夹名称找到对应的完整路径
    full_path = next(f for f in folders if os.path.basename(f) == selected_folder)
    # 确保 full_path 是文件夹路径，而不是文件路径
    if os.path.isfile(full_path):
        full_path = os.path.dirname(full_path)
    mca_files = [f for f in os.listdir(full_path) if f.endswith('.mca')]
    return gr.update(choices=mca_files)

def show_mca_info(selected_mca, selected_folder):
    try:
        region_file = nbt.load(os.path.join(selected_folder, selected_mca))
        return {
            "文件名": selected_mca,
            "区块数量": len(region_file['Chunks']),
            "方块类型统计": Counter(
                block['id'].value 
                for chunk in region_file['Chunks'] 
                for block in chunk['Blocks']
            )
        }
    except Exception as e:
        return {"错误": str(e)}

def launch_ui():
    local_ip = get_local_ip()
    print(f"Web UI 管理地址: http://{local_ip}:7860")  # 修改为 HTTP

    with gr.Blocks() as demo:
        with gr.Column():
            with gr.Tab("数据预处理"):
                data_folders = gr.File(label="选择训练集文件夹", file_count="directory", file_types=[".mca"], height=100)
                folder_selector = gr.Dropdown(label="已加载文件夹", interactive=True)
                mca_selector = gr.Dropdown(label="选择.mca文件", interactive=True)
                preview_area = gr.JSON(label="文件预览信息")
                processed_output_folder = gr.Textbox(label="处理后训练集输出地址")
                preprocess_button = gr.Button("预处理数据")
                preprocess_output = gr.Textbox(label="预处理结果")

                data_folders.change(
                    load_and_preview,
                    inputs=data_folders,
                    outputs=[gr.JSON(visible=False), folder_selector]
                )

                folder_selector.change(
                    update_mca_list,
                    inputs=[folder_selector, data_folders],
                    outputs=mca_selector
                )

                mca_selector.change(
                    show_mca_info,
                    inputs=[mca_selector, folder_selector],
                    outputs=preview_area
                )

                preprocess_button.click(preprocess_data, inputs=[data_folders, processed_output_folder], outputs=preprocess_output)

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

        train_button.click(train_and_generate, inputs=[data_folders, config_file, description, epochs, learning_rate, batch_size], outputs=train_output)
        generate_button.click(generate_map, inputs=[model_path, description], outputs=generate_output)

    demo.launch(server_name=local_ip)

if __name__ == "__main__":
    launch_ui()

