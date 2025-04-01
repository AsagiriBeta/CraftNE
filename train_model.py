import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from data_loader import MinecraftDataLoader
import os

class CraftNEModel(nn.Module):
    def __init__(self):
        super(CraftNEModel, self).__init__()
        self.conv1 = nn.Conv3d(1, 32, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv3d(32, 64, kernel_size=3, stride=1, padding=1)
        self.fc1 = nn.Linear(64 * 8 * 8 * 8, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 3)

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = torch.relu(self.conv2(x))
        x = x.view(x.size(0), -1)
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x

def train_model(data_folder, model_save_path, epochs=10, learning_rate=0.001, batch_size=32):
    # 确保models目录存在
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    
    # 选择设备
    device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
    
    data_loader = MinecraftDataLoader(data_folder)
    data = data_loader.load_data()
    dataset = DataLoader(data, batch_size=batch_size, shuffle=True)
    
    model = CraftNEModel().to(device)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    
    for epoch in range(epochs):
        for batch in dataset:
            # 将输入数据转换为3D张量并移动到设备
            inputs = torch.tensor([block['position'] for block in batch], dtype=torch.float32).to(device)
            inputs = inputs.unsqueeze(1)  # 添加通道维度
            outputs = model(inputs)
            loss = criterion(outputs, inputs.squeeze(1))
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
    
    torch.save(model.state_dict(), model_save_path)