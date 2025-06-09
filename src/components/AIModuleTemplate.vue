<template>
  <div class="ai-module">
    <el-tabs v-model="activeTab" type="card">
      <!-- 训练集处理 -->
      <el-tab-pane label="训练集处理" name="dataset">
        <div class="tab-content">
          <el-form :model="datasetForm" label-width="120px">
            <el-form-item label="数据集路径">
              <el-input v-model="datasetForm.path" placeholder="选择数据集文件夹">
                <template #append>
                  <el-button @click="selectDatasetPath">浏览</el-button>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="数据格式">
              <el-select v-model="datasetForm.format">
                <el-option label="PNG Images" value="png" />
                <el-option label="NBT Files" value="nbt" />
                <el-option label="Schematic" value="schematic" />
              </el-select>
            </el-form-item>
            <el-form-item label="预处理选项">
              <el-checkbox-group v-model="datasetForm.preprocessing">
                <el-checkbox value="resize">尺寸标准化</el-checkbox>
                <el-checkbox value="augment">数据增强</el-checkbox>
                <el-checkbox value="normalize">归一化</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="processDataset" :loading="processing">
                处理数据集
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 训练 -->
      <el-tab-pane label="训练" name="training">
        <div class="tab-content">
          <el-form :model="trainingForm" label-width="120px">
            <el-form-item label="模型架构">
              <el-select v-model="trainingForm.architecture">
                <el-option label="GAN" value="gan" />
                <el-option label="VAE" value="vae" />
                <el-option label="Diffusion" value="diffusion" />
              </el-select>
            </el-form-item>
            <el-form-item label="训练轮数">
              <el-input-number v-model="trainingForm.epochs" :min="1" :max="1000" />
            </el-form-item>
            <el-form-item label="批次大小">
              <el-input-number v-model="trainingForm.batchSize" :min="1" :max="128" />
            </el-form-item>
            <el-form-item label="学习率">
              <el-input-number 
                v-model="trainingForm.learningRate" 
                :min="0.0001" 
                :max="0.1" 
                :step="0.0001"
                :precision="4" 
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="startTraining" :loading="training">
                开始训练
              </el-button>
              <el-button @click="stopTraining" :disabled="!training">
                停止训练
              </el-button>
            </el-form-item>
          </el-form>

          <div v-if="training" class="training-progress">
            <h4>训练进度</h4>
            <el-progress :percentage="trainingProgress" />
            <div class="progress-info">
              <span>轮次: {{ currentEpoch }}/{{ trainingForm.epochs }}</span>
              <span>损失: {{ currentLoss }}</span>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 推理 -->
      <el-tab-pane label="推理" name="inference">
        <div class="tab-content">
          <el-form :model="inferenceForm" label-width="120px">
            <el-form-item label="模型文件">
              <el-input v-model="inferenceForm.modelPath" placeholder="选择训练好的模型">
                <template #append>
                  <el-button @click="selectModelPath">浏览</el-button>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="生成提示">
              <el-input 
                v-model="inferenceForm.prompt" 
                type="textarea" 
                :rows="3"
                placeholder="描述你想要生成的内容..."
              />
            </el-form-item>
            <el-form-item label="生成数量">
              <el-input-number v-model="inferenceForm.count" :min="1" :max="10" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="startInference" :loading="inferencing">
                开始生成
              </el-button>
            </el-form-item>
          </el-form>

          <div v-if="inferenceResults.length > 0" class="inference-results">
            <h4>生成结果</h4>
            <div class="results-grid">
              <div 
                v-for="(result, index) in inferenceResults" 
                :key="index" 
                class="result-item"
              >
                <img :src="result" :alt="`Result ${index + 1}`" />
                <div class="result-actions">
                  <el-button size="small" @click="downloadResult(result, index)">
                    下载
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { invoke } from "@tauri-apps/api/core";
import { ElMessage } from "element-plus";

interface Props {
  moduleType: string;
  trainingOptions: any;
}

const props = defineProps<Props>();
const emit = defineEmits(["start-training", "start-inference"]);

const activeTab = ref("dataset");
const processing = ref(false);
const training = ref(false);
const inferencing = ref(false);
const trainingProgress = ref(0);
const currentEpoch = ref(0);
const currentLoss = ref("0.000");
const inferenceResults = ref<string[]>([]);

// 表单数据
const datasetForm = ref({
  path: "",
  format: "png",
  preprocessing: ["resize", "normalize"]
});

const trainingForm = ref({
  architecture: "gan",
  epochs: props.trainingOptions.epochs || 100,
  batchSize: props.trainingOptions.batchSize || 32,
  learningRate: props.trainingOptions.learningRate || 0.001
});

const inferenceForm = ref({
  modelPath: "",
  prompt: "",
  count: 1
});

// 方法
const selectDatasetPath = async () => {
  // TODO: 使用Tauri的文件对话框
  ElMessage.info("请手动输入数据集路径");
};

const selectModelPath = async () => {
  // TODO: 使用Tauri的文件对话框
  ElMessage.info("请手动输入模型文件路径");
};

const processDataset = async () => {
  processing.value = true;
  try {
    await invoke("process_dataset", {
      datasetPath: datasetForm.value.path,
      modelType: props.moduleType
    });
    ElMessage.success("数据集处理完成!");
  } catch (error) {
    ElMessage.error(`数据集处理失败: ${error}`);
  } finally {
    processing.value = false;
  }
};

const startTraining = async () => {
  training.value = true;
  try {
    const taskId = await invoke("create_training_task", {
      modelType: props.moduleType,
      config: trainingForm.value
    });
    
    ElMessage.success("训练任务已开始!");
    emit("start-training", trainingForm.value);
    
    // 模拟训练进度
    simulateTrainingProgress();
  } catch (error) {
    ElMessage.error(`训练启动失败: ${error}`);
    training.value = false;
  }
};

const stopTraining = () => {
  training.value = false;
  trainingProgress.value = 0;
  currentEpoch.value = 0;
  ElMessage.info("训练已停止");
};

const simulateTrainingProgress = () => {
  const interval = setInterval(() => {
    if (!training.value) {
      clearInterval(interval);
      return;
    }
    
    trainingProgress.value += 1;
    currentEpoch.value = Math.floor((trainingProgress.value / 100) * trainingForm.value.epochs);
    currentLoss.value = (Math.random() * 0.1 + 0.05).toFixed(3);
    
    if (trainingProgress.value >= 100) {
      training.value = false;
      ElMessage.success("训练完成!");
      clearInterval(interval);
    }
  }, 500);
};

const startInference = async () => {
  inferencing.value = true;
  try {
    const result = await invoke("generate_content", {
      modelType: props.moduleType,
      prompt: inferenceForm.value.prompt,
      modelPath: inferenceForm.value.modelPath
    });
    
    // 模拟生成结果
    inferenceResults.value = Array.from({ length: inferenceForm.value.count }, 
      (_, i) => `data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==`
    );
    
    ElMessage.success("生成完成!");
    emit("start-inference", inferenceForm.value);
  } catch (error) {
    ElMessage.error(`生成失败: ${error}`);
  } finally {
    inferencing.value = false;
  }
};

const downloadResult = (result: string, index: number) => {
  // TODO: 实现文件下载
  ElMessage.success(`结果 ${index + 1} 已保存`);
};
</script>

<style scoped>
.ai-module {
  max-width: 1000px;
}

.tab-content {
  padding: 20px 0;
}

.training-progress {
  margin-top: 30px;
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background-color: #f8f9fa;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  font-size: 14px;
  color: #606266;
}

.inference-results {
  margin-top: 30px;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.result-item {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.result-item img {
  width: 100%;
  height: 150px;
  object-fit: cover;
}

.result-actions {
  padding: 10px;
  text-align: center;
}
</style>