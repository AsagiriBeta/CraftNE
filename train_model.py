import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from data_loader import MinecraftDataLoader
import os

class CraftNEModel(nn.Module):
    def __init__(self, cube_size=8):
        super(CraftNEModel, self).__init__()
        self.cube_size = cube_size
        # 输入通道改为1（单色立方体），输出通道为类别数
        self.conv1 = nn.Conv3d(1, 32, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv3d(32, 64, kernel_size=3, stride=1, padding=1)
        # 输出为相同尺寸的立方体
        self.final_conv = nn.Conv3d(64, 1, kernel_size=1)  # 1通道输出

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = torch.relu(self.conv2(x))
        x = self.final_conv(x)
        return x

def train_model(data_folder, model_save_path, epochs=10, learning_rate=0.001, batch_size=32):
    # 确保models目录存在
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    
    # 选择设备
    device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
    
    data_loader = MinecraftDataLoader(data_folder)
    data = data_loader.load_data()
    
    # 添加collate函数将列表转换为张量
    def collate_fn(batch):
        return torch.tensor(batch, dtype=torch.float32)
    
    dataset = DataLoader(data, batch_size=batch_size, shuffle=True, collate_fn=collate_fn)
    
    model = CraftNEModel().to(device)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    
    for epoch in range(epochs):
        for batch in dataset:
            inputs = batch.unsqueeze(1).to(device)
            outputs = model(inputs)
            # 使用MSE损失比较整个立方体结构
            loss = criterion(outputs, inputs)  # 直接比较输入输出结构
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
    
    torch.save(model.state_dict(), model_save_path)