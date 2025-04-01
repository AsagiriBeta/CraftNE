import gradio as gr
from train_model import train_model
from inference import generate_map
import socket
import os
import csv

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

def preprocess_data(input_data_folder, mca_file, output_folder):
    # 这里添加预处理逻辑
    if mca_file:
        # 处理上传的 .mca 文件
        pass
    if input_data_folder:
        # 处理数据文件夹中的 .mca 文件
        pass
    return f"数据已预处理并保存到 {output_folder}"

def launch_ui():
    local_ip = get_local_ip()
    print(f"Web UI 管理地址: http://{local_ip}:7860")  # 修改为 HTTP

    with gr.Blocks() as demo:
        with gr.Column():
            with gr.Tab("数据预处理"):
                data_folder = gr.Textbox(label="数据文件夹路径")
                mca_file_upload = gr.File(label="上传 .mca 文件")
                processed_output_folder = gr.Textbox(label="处理后训练集输出地址")
                preprocess_button = gr.Button("预处理数据")
                preprocess_output = gr.Textbox(label="预处理结果")

                preprocess_button.click(preprocess_data, inputs=[data_folder, mca_file_upload, processed_output_folder], outputs=preprocess_output)

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

        train_button.click(train_and_generate, inputs=[data_folder, config_file, description, epochs, learning_rate, batch_size], outputs=train_output)
        generate_button.click(generate_map, inputs=[model_path, description], outputs=generate_output)

    demo.launch(server_name=local_ip)

if __name__ == "__main__":
    launch_ui()