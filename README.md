# CraftNE - Minecraft地图处理和AI训练平台

CraftNE是一个基于Python Flask + Three.js的Web应用程序，专门用于处理Minecraft地图文件并训练AI模型。

## 功能特性

- 🗺️ **MCA文件解析**: 使用mcapy包解析Minecraft区块文件
- 🎮 **3D可视化**: 基于Three.js的交互式3D地图预览
- 🏷️ **数据标注**: Web界面进行3D区域标注，制作训练集
- 🤖 **AI训练**: 集成3D扩散模型训练功能
- ✨ **地图生成**: 通过提示词生成新的Minecraft地图
- 📊 **可视化分析**: 丰富的数据统计和可视化

## 技术栈

### 后端
- **Flask**: Web框架
- **SQLAlchemy**: 数据库ORM
- **Celery**: 异步任务处理
- **Redis**: 缓存和消息队列
- **PyTorch**: AI模型训练

### 前端
- **Three.js**: 3D渲染和可视化
- **Bootstrap**: UI框架
- **JavaScript ES6+**: 现代前端开发

### 数据处理
- **mcapy**: Minecraft文件解析
- **NumPy**: 数值计算
- **Pandas**: 数据处理

## 快速开始

### 环境要求

- Python 3.8+
- Redis Server
- Node.js (可选，用于前端开发)

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/AsagiriBeta/CraftNE.git
cd CraftNE
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件，配置数据库和Redis连接
```

5. **初始化数据库**
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. **启动Redis服务**
```bash
redis-server
```

7. **启动Celery Worker**
```bash
celery -A celery_worker.celery worker --loglevel=info
```

8. **启动应用**
```bash
python run.py
```

访问 http://localhost:5000 开始使用！

## 使用指南

### 1. 上传MCA文件

1. 访问上传页面
2. 选择Minecraft的.mca文件
3. 等待文件解析完成

### 2. 3D预览

1. 在地图列表中选择已解析的地图
2. 点击"3D预览"查看三维模型
3. 使用鼠标进行旋转、缩放、平移操作

### 3. 数据标注

1. 在3D预览中框选要标注的区域
2. 为区域添加标签和描述
3. 保存标注数据

### 4. AI训练

1. 准备标注数据集
2. 配置训练参数
3. 启动训练任务
4. 监控训练进度

### 5. 地图生成

1. 输入描述性提示词
2. 选择生成参数
3. 生成新的地图
4. 下载或预览结果

## 项目结构

```
CraftNE/
├── app/                    # 主应用代码
│   ├── models/            # 数据模型
│   ├── views/             # 路由和视图
│   ├── services/          # 业务逻辑服务
│   ├── utils/             # 工具函数
│   └── static/            # 静态资源
├── config/                # 配置文件
├── tests/                 # 测试代码
├── requirements.txt       # Python依赖
└── README.md             # 项目文档
```

## API文档

### 文件上传API
```
POST /upload/api/upload
```
上传MCA文件

### 地图数据API
```
GET /upload/api/maps/{id}
```
获取地图详细信息

### 标注API
```
GET /annotation/api/annotations/{map_id}
POST /annotation/api/annotations
```
获取和创建标注数据

## 开发指南

### 添加新的方块类型支持

1. 在 `app/services/mca_parser.py` 中添加新的方块类型处理
2. 在 `app/static/js/map_viewer.js` 中添加对应的材质定义

### 自定义AI模型

1. 继承 `app/services/model_trainer.py` 中的基础训练器
2. 实现自定义的训练逻辑
3. 在配置中注册新的模型类型

### 扩展标注功能

1. 修改 `app/models/annotation.py` 添加新的标注字段
2. 更新前端标注界面
3. 相应地更新API接口

## 贡献指南

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- 项目维护者: AsagiriBeta
- 项目链接: https://github.com/AsagiriBeta/CraftNE
- 问题反馈: https://github.com/AsagiriBeta/CraftNE/issues

## 致谢

- [mcapy](https://github.com/matcool/mcapy) - Minecraft文件解析
- [Three.js](https://threejs.org/) - 3D图形库
- [Flask](https://flask.palletsprojects.com/) - Web框架
- Minecraft社区 - 提供测试数据和反馈