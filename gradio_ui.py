import gradio as gr
from train_model import train_model
from inference import generate_map
import socket
import os
import json
import csv  # 新增: 导入csv模块解决DictReader引用问题
from collections import Counter
from nbtlib import nbt
from MTDCmca import process_files
from data_loader import BLOCK_ID_MAP  # 新增导入方块ID映射表


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
            # 新增：解压处理标签页（移动到第一个位置）
            with gr.Tab("解压处理"):
                gr.Markdown("### MCA文件解压与JSON转换")
                mca_files_input = gr.Files(label="上传MCA文件（可多选）", file_types=[".mca"])
                output_dir_input = gr.Textbox(label="输出目录", value=os.path.join(project_root, 'data'))
                convert_json_checkbox = gr.Checkbox(label="转换为JSON格式", value=True)
                threads_slider = gr.Slider(minimum=1, maximum=8, step=1, value=4, label="并发线程数")
                decompress_button = gr.Button("开始解压")
                decompress_output = gr.Textbox(label="解压结果")

                decompress_button.click(
                    fn=decompress_mca,
                    inputs=[mca_files_input, output_dir_input, convert_json_checkbox, threads_slider],
                    outputs=decompress_output
                )
            
            # 修改点：重命名标签页并移除预处理相关组件
            with gr.Tab("训练"):  # 原数据预处理标签页重命名为数据预览
                gr.Markdown("### JSON数据预览")
                with gr.Row():
                    folder_selector = gr.Dropdown(  # 修改：改为文件夹选择器
                        label="选择包含JSON文件的文件夹",
                        choices=get_subfolders(data_folder),
                        value=get_subfolders(data_folder)[0] if get_subfolders(data_folder) else None,
                        interactive=True
                    )
                    refresh_btn = gr.Button("🔄", size="sm")  # 新增：刷新按钮
                    
                preview_area = gr.JSON(label="方块类型统计结果")

                # 绑定文件夹选择器和预览区域
                folder_selector.change(
                    fn=load_json_preview,
                    inputs=folder_selector,
                    outputs=preview_area
                )
                
                # 新增：刷新按钮功能
                refresh_btn.click(
                    fn=lambda: gr.update(choices=get_subfolders(data_folder)),
                    outputs=folder_selector
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

                # 修改点：将未定义的input_data_files替换为folder_selector.value
                train_button.click(
                    fn=train_and_generate,
                    inputs=[folder_selector, config_file, description, epochs, learning_rate, batch_size],
                    outputs=train_output
                )

            with gr.Tab("推理部署"):
                model_path = gr.Textbox(label="模型路径", value="models/craftne_model.pth")
                generate_button = gr.Button("开始生成")
                generate_output = gr.Textbox(label="生成结果")

        demo.launch(server_name=local_ip)


# 新增: 解压处理函数
def decompress_mca(mca_files, output_dir, convert_json, threads):
    if not mca_files:
        return "未选择任何 MCA 文件"
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    default_output_base = os.path.join(project_root, 'data')  # 主项目data目录
    
    results = []
    
    if not output_dir:  # 自动路径生成功能
        os.makedirs(default_output_base, exist_ok=True)  # 确保基础目录存在
        
        for mca_file in mca_files:
            # 修改点：强制转换为字符串确保路径类型正确
            mca_filename = os.path.basename(str(mca_file.name))  # 添加str()类型转换
            mca_name = os.path.splitext(mca_filename)[0]  # 去除.mca扩展名
            specific_output_dir = os.path.join(default_output_base, mca_name)
            
            try:
                os.makedirs(specific_output_dir, exist_ok=True)  # 创建独立子文件夹
                
                # 单文件处理逻辑（修改为传递具体输出路径）
                mca_path = str(mca_file.name)  # 统一路径类型
                elapsed = process_files([mca_path], specific_output_dir, convert_json, threads)
                
                # 新增：递归统计所有子目录中的JSON文件
                json_count = 0
                for root, _, files in os.walk(specific_output_dir):  # 类型已修正
                    json_count += sum(1 for f in files if f.endswith('.json'))
                
                results.append(f"{mca_name}: 耗时 {elapsed:.2f} 秒 -> 输出至 {specific_output_dir}\n成功生成 {json_count} 个 JSON 文件")
            except Exception as e:
                results.append(f"{mca_name}: 解压失败 - {str(e)}")
        
        return "\n".join(results)
    
    # 用户自定义路径处理逻辑保持兼容性
    else:
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        try:
            mca_paths = [f.name for f in mca_files]
            # 修改点：强制转换output_dir为字符串确保类型安全
            elapsed = process_files(mca_paths, str(output_dir), convert_json, threads)
            
            # 修改：精确统计每个MCA文件对应子文件夹的JSON文件
            json_count = 0
            for mca_path in mca_paths:
                mca_filename = os.path.basename(mca_path)
                mca_name = os.path.splitext(mca_filename)[0]  # 去除.mca扩展名
                # 修改点：对路径拼接进行类型强制转换
                specific_output_dir = os.path.join(str(output_dir), mca_name)
                
                if os.path.exists(specific_output_dir):
                    for root, _, files in os.walk(str(specific_output_dir)):
                        json_count += sum(1 for f in files if f.endswith('.json'))
            
            result = f"解压完成，耗时: {elapsed:.2f} 秒\n输出目录: {output_dir}"
            if convert_json:
                result += f"\n成功生成 {json_count} 个 JSON 文件"
            return result
        except Exception as e:
            return f"解压失败: {str(e)}"

# 新增：将load_json_preview定义移到所有UI组件定义之前
# 新增：获取JSON文件列表函数
def get_json_files(folder):
    if not os.path.exists(folder):
        return []
    json_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))
    return sorted(json_files)

# 新增：获取指定文件夹下的所有子文件夹名称
def get_subfolders(folder):
    """新增：获取指定文件夹下的所有子文件夹名称"""
    if not os.path.exists(folder):
        return []
    subfolders = []
    for name in os.listdir(folder):
        full_path = os.path.join(folder, name)
        if os.path.isdir(full_path):
            subfolders.append(name)
    return sorted(subfolders)

# 修改：更新JSON预览函数，适配新版数据结构
def load_json_preview(folder_name=None):
    """修正JSON预览函数适配新版数据结构"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(project_root, 'data')
    
    if not folder_name:
        subfolders = get_subfolders(data_folder)
        if not subfolders:
            return {"提示": "data文件夹中暂无子文件夹"}
        folder_name = subfolders[0]
    
    folder_path = os.path.join(data_folder, folder_name)
    
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return {"错误": f"文件夹不存在: {folder_path}"}
    
    block_counter = Counter()
    file_count = 0
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = json.load(f)
                    
                    # 关键修改：正确遍历Level.Sections下的Blocks字段
                    if content.get("Level", {}).get("Sections"):
                        for section in content["Level"]["Sections"]:
                            blocks = section.get("Blocks", [])
                            if blocks:
                                block_names = [BLOCK_ID_MAP.get(b, "minecraft:air") for b in blocks]
                                block_counter.update(block_names)
                    
                    file_count += 1
                except Exception as e:
                    print(f"读取文件失败: {file_path}, 错误: {str(e)}")
    
    return {
        "文件夹路径": folder_path,
        "统计的JSON文件数量": file_count,
        "方块类型统计": dict(block_counter)
    }

if __name__ == "__main__":
    launch_ui()

