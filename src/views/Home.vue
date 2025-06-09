<template>
  <div class="home">
    <el-row :gutter="24">
      <el-col :span="24">
        <div class="welcome-section">
          <h2>欢迎使用 CraftNE</h2>
          <p>一个专为Minecraft设计的AI开发工具包，提供地图、皮肤和材质的智能生成功能。</p>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="24" class="feature-cards">
      <el-col :span="8">
        <el-card class="feature-card" @click="$router.push('/map')">
          <template #header>
            <div class="card-header">
              <el-icon size="24"><MapLocation /></el-icon>
              <span>地图生成</span>
            </div>
          </template>
          <div class="card-content">
            <p>使用AI技术生成各种类型的Minecraft地图，支持自定义参数和风格。</p>
            <ul>
              <li>训练集处理</li>
              <li>模型训练</li>
              <li>地图推理生成</li>
            </ul>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="feature-card" @click="$router.push('/skin')">
          <template #header>
            <div class="card-header">
              <el-icon size="24"><Avatar /></el-icon>
              <span>皮肤生成</span>
            </div>
          </template>
          <div class="card-content">
            <p>智能生成独特的Minecraft角色皮肤，支持多种风格和自定义选项。</p>
            <ul>
              <li>皮肤数据处理</li>
              <li>风格训练</li>
              <li>个性化生成</li>
            </ul>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="feature-card" @click="$router.push('/texture')">
          <template #header>
            <div class="card-header">
              <el-icon size="24"><Picture /></el-icon>
              <span>材质生成</span>
            </div>
          </template>
          <div class="card-content">
            <p>为Minecraft物品和方块生成高质量的材质贴图。</p>
            <ul>
              <li>材质数据预处理</li>
              <li>纹理模型训练</li>
              <li>材质包生成</li>
            </ul>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="24" class="status-section">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon><Monitor /></el-icon>
              <span>系统状态</span>
            </div>
          </template>
          <div class="status-grid">
            <div class="status-item">
              <div class="status-label">活跃任务</div>
              <div class="status-value">{{ activeTasks }}</div>
            </div>
            <div class="status-item">
              <div class="status-label">完成任务</div>
              <div class="status-value">{{ completedTasks }}</div>
            </div>
            <div class="status-item">
              <div class="status-label">Python环境</div>
              <div class="status-value">
                <el-tag :type="pythonStatus === 'Ready' ? 'success' : 'danger'">
                  {{ pythonStatus }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { MapLocation, Avatar, Picture, Monitor } from "@element-plus/icons-vue";
import { invoke } from "@tauri-apps/api/core";

const activeTasks = ref(0);
const completedTasks = ref(0);
const pythonStatus = ref("检查中...");

onMounted(async () => {
  try {
    const tasks = await invoke("get_tasks");
    const taskList = tasks as any[];
    activeTasks.value = taskList.filter((task: any) => task.status === "running").length;
    completedTasks.value = taskList.filter((task: any) => task.status === "completed").length;
  } catch (error) {
    console.error("Failed to fetch tasks:", error);
  }

  try {
    await invoke("start_python_script", { 
      scriptName: "check_environment", 
      args: [] 
    });
    pythonStatus.value = "Ready";
  } catch (error) {
    pythonStatus.value = "Error";
  }
});
</script>

<style scoped>
.welcome-section {
  text-align: center;
  padding: 40px 0;
}

.welcome-section h2 {
  color: #303133;
  margin-bottom: 16px;
}

.feature-cards {
  margin-top: 30px;
}

.feature-card {
  cursor: pointer;
  transition: all 0.3s ease;
  height: 280px;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: bold;
}

.card-content ul {
  list-style: none;
  padding: 0;
  margin-top: 15px;
}

.card-content li {
  padding: 5px 0;
  border-left: 3px solid #409eff;
  padding-left: 10px;
  margin-bottom: 8px;
}

.status-section {
  margin-top: 30px;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.status-item {
  text-align: center;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.status-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.status-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}
</style>