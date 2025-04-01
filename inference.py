import torch
import nbtlib
from train_model import CraftNEModel

def generate_map(model_path, description):
    # 选择设备
    device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
    
    model = CraftNEModel().to(device)
    model.load_state_dict(torch.load(model_path))
    model.eval()
    
    # 根据描述生成地图的逻辑
    # 这里假设描述是一个字符串，模型会根据描述生成一个地图
    # 实际实现需要更复杂的逻辑
    print(f"根据描述 '{description}' 生成地图")
    generated_blocks = model(torch.randn(100, 3).to(device))
    
    # 将生成的方块保存为NBT文件
    nbt_file = nbtlib.File()
    nbt_file['blocks'] = nbtlib.List([nbtlib.Compound({
        'id': nbtlib.String('minecraft:stone'),
        'state': nbtlib.Int(0),
        'x': nbtlib.Int(x),
        'y': nbtlib.Int(y),
        'z': nbtlib.Int(z)
    }) for x, y, z in generated_blocks.cpu().numpy()])
    
    nbt_file.save('generated_map.nbt')

if __name__ == "__main__":
    generate_map('models/craftne_model.pth', '生成一个山洞')