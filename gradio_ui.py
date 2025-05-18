import gradio as gr
from train_model import train_model
from inference import generate_map
import socket
import os
import csv  # 新增: 导入csv模块解决DictReader引用问题
from data_loader import MinecraftDataLoader  # 新增: 解决MinecraftDataLoader未解析引用问题


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

def show_mca_info(selected_mca):
    try:
        region_file_path = os.path.normpath(selected_mca)
        if not os.path.isfile(region_file_path):
            raise FileNotFoundError(f"找不到文件: {region_file_path}")

        # 使用 data_loader 分析 MCA 文件（已通过正确导入解决引用问题）
        loader = MinecraftDataLoader(data_folder="")  # 只使用分析功能，忽略 data_folder
        return loader.analyze_mca_file(region_file_path)

    except Exception as e:
        return {"错误": str(e)}

# 新增：MCA文件预览函数
def load_mca_preview(mca_file):
    """处理MCA文件上传后的实时预览"""
    if not mca_file:
        return {"提示": "请上传MCA文件"}
    
    try:
        # 获取文件路径并调用show_mca_info处理
        file_path = mca_file.name if hasattr(mca_file, 'name') else str(mca_file)
        return show_mca_info(file_path)
    except Exception as e:
        return {"错误": str(e)}

def load_and_preview(folders):
    valid_files = []
    seen_files = set()
    
    if folders is None:
        return {"valid_files": []}, gr.update(choices=[], value=None)
    
    if folders:
        for folder in folders:
            folder_path = folder if isinstance(folder, str) else folder.name
            
            # 修改点1：添加str()类型转换
            for root, _, filenames in os.walk(str(folder_path)):
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
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(project_root, 'data')

    with gr.Blocks() as demo:
        with gr.Column():
            # 修改点：训练标签页重构为MCA文件直接预览
            with gr.Tab("训练"):  
                gr.Markdown("### MCA文件分析")
                with gr.Row():
                    mca_file_input = gr.File(label="上传MCA文件", file_types=[".mca"])
                
                preview_area = gr.JSON(label="MCA文件统计信息")

                # 绑定MCA文件上传和预览区域
                mca_file_input.change(
                    fn=load_mca_preview,
                    inputs=mca_file_input,
                    outputs=preview_area
                )

                # 新增训练参数模块（原训练参数标签页内容迁移至此）
                gr.Markdown("### 训练参数")
                config_file = gr.Dropdown(label="选择配置文件", choices=get_flagged_csv_files())
                description = gr.Textbox(label="描述")
                epochs = gr.Slider(minimum=1, maximum=100, step=1, label="训练轮数 (Epochs)")
                learning_rate = gr.Slider(minimum=0.0001, maximum=0.01, step=0.0001, label="学习率 (Learning Rate)")
                batch_size = gr.Slider(minimum=16, maximum=128, step=16, label="批量大小 (Batch Size)")
                train_button = gr.Button("开始训练")
                train_output = gr.Textbox(label="训练结果")

                train_button.click(
                    fn=train_and_generate,
                    inputs=[mca_file_input, config_file, description, epochs, learning_rate, batch_size],
                    outputs=train_output
                )

            with gr.Tab("推理部署"):
                model_path = gr.Textbox(label="模型路径", value="models/craftne_model.pth")
                generate_button = gr.Button("开始生成")
                generate_output = gr.Textbox(label="生成结果")

        demo.launch(server_name=local_ip)

if __name__ == "__main__":
    launch_ui()

