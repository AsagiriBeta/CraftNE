import torch
import nbtlib
from train_model import CraftNEModel

def generate_map(model_path, description):
    # 选择设备
    device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
    
    model = CraftNEModel().to(device)
    model.load_state_dict(torch.load(model_path))
    model.eval()
    
    # 根据描述生成地图的逻辑（简化版）
    print(f"根据描述 '{description}' 生成地图")
    
    # 生成随机输入（实际应根据描述编码生成）
    with torch.no_grad():
        latent_input = torch.randn(1, 1, 8, 8, 8).to(device)
        output_cube = model(latent_input).squeeze().cpu().numpy()
    
    # 转换为NBT格式
    nbt_file = nbtlib.File()
    blocks = []
    for x in range(8):
        for y in range(8):
            for z in range(8):
                # 将连续值转换为离散块类型
                block_value = output_cube[x, y, z]
                if block_value > 0.5:  # 阈值分割
                    blocks.append(nbtlib.Compound({
                        'id': nbtlib.String('minecraft:stone'),
                        'state': nbtlib.Int(0),
                        'x': nbtlib.Int(x),
                        'y': nbtlib.Int(y),
                        'z': nbtlib.Int(z)
                    }))
    
    nbt_file['Blocks'] = nbtlib.List(blocks)
    nbt_file.save('generated_map.nbt')