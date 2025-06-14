<template>
  <div class="item-generator">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="generator-card">
          <template #header>
            <div class="card-header">
              <span>Item Texture Generator</span>
              <el-tag type="success">32x32</el-tag>
            </div>
          </template>
          
          <div class="generator-form">
            <div class="form-section">
              <label class="form-label">Model Path</label>
              <el-input
                v-model="modelPath"
                placeholder="Select item texture model..."
                readonly
              >
                <template #append>
                  <el-button @click="selectModel" :icon="FolderOpened">
                    Browse
                  </el-button>
                </template>
              </el-input>
            </div>
            
            <div class="form-section">
              <label class="form-label">Item Category</label>
              <el-select v-model="itemCategory" placeholder="Select category" style="width: 100%">
                <el-option label="Tools" value="tools" />
                <el-option label="Weapons" value="weapons" />
                <el-option label="Armor" value="armor" />
                <el-option label="Blocks" value="blocks" />
                <el-option label="Food" value="food" />
                <el-option label="Materials" value="materials" />
                <el-option label="Decorative" value="decorative" />
              </el-select>
            </div>
            
            <div class="form-section">
              <label class="form-label">Prompt</label>
              <el-input
                v-model="prompt"
                type="textarea"
                :rows="4"
                placeholder="Describe the item texture you want to generate..."
                maxlength="500"
                show-word-limit
              />
            </div>
            
            <div class="form-section">
              <label class="form-label">Style Options</label>
              <el-row :gutter="10">
                <el-col :span="12">
                  <el-select v-model="textureStyle" placeholder="Style" style="width: 100%">
                    <el-option label="Vanilla" value="vanilla" />
                    <el-option label="Realistic" value="realistic" />
                    <el-option label="Cartoon" value="cartoon" />
                    <el-option label="Medieval" value="medieval" />
                    <el-option label="Modern" value="modern" />
                  </el-select>
                  <div class="input-label">Texture Style</div>
                </el-col>
                <el-col :span="12">
                  <el-slider
                    v-model="detail"
                    :min="1"
                    :max="10"
                    show-stops
                    show-input
                    :show-input-controls="false"
                  />
                  <div class="input-label">Detail Level</div>
                </el-col>
              </el-row>
            </div>
            
            <div class="action-buttons">
              <el-button
                type="primary"
                @click="generateTexture"
                :loading="generating"
                :disabled="!canGenerate"
                size="large"
              >
                <el-icon><Loading /></el-icon>
                Generate Texture
              </el-button>
              
              <el-button
                v-if="generatedImage"
                @click="saveTexture"
                :icon="Download"
                size="large"
              >
                Save
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="preview-card">
          <template #header>
            <span>Preview</span>
          </template>
          
          <div class="preview-content">
            <div v-if="generating" class="loading-state">
              <el-icon class="is-loading"><Loading /></el-icon>
              <p>Generating texture...</p>
              <el-progress :percentage="progress" />
            </div>
            
            <div v-else-if="generatedImage" class="generated-result">
              <div class="texture-preview">
                <img :src="generatedImage" alt="Generated Texture" />
                <div class="texture-info">
                  <p><strong>Resolution:</strong> 32x32</p>
                  <p><strong>Category:</strong> {{ itemCategory }}</p>
                  <p><strong>Style:</strong> {{ textureStyle }}</p>
                  <p><strong>Generation Time:</strong> {{ generationTime }}s</p>
                </div>
              </div>
            </div>
            
            <div v-else class="empty-state">
              <el-icon><Box /></el-icon>
              <p>No texture generated yet</p>
              <p class="hint">Configure settings and generate an item texture</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  FolderOpened, 
  Download,
  Loading, 
  Box 
} from '@element-plus/icons-vue'
import { useItemStore } from '@/stores/itemStore'
import { useModelManager } from '@/composables/useModelManager'

const itemStore = useItemStore()
const { selectModelFile, generateItemTexture } = useModelManager()

const modelPath = ref('')
const prompt = ref('')
const itemCategory = ref('')
const textureStyle = ref('vanilla')
const detail = ref(5)
const generating = ref(false)
const progress = ref(0)
const generatedImage = ref('')
const generationTime = ref(0)

const canGenerate = computed(() => {
  return modelPath.value && prompt.value.trim() && itemCategory.value
})

const selectModel = async () => {
  try {
    const path = await selectModelFile()
    if (path) {
      modelPath.value = path
      ElMessage.success('Model selected successfully')
    }
  } catch (error) {
    ElMessage.error('Failed to select model')
  }
}

const generateTexture = async () => {
  if (!canGenerate.value) return
  
  generating.value = true
  progress.value = 0
  
  try {
    const progressInterval = setInterval(() => {
      if (progress.value < 90) {
        progress.value += Math.random() * 15
      }
    }, 400)
    
    const enhancedPrompt = `${prompt.value}, ${itemCategory.value}, ${textureStyle.value} style, detail level ${detail.value}`
    const result = await generateItemTexture(enhancedPrompt, modelPath.value)
    
    clearInterval(progressInterval)
    progress.value = 100
    
    if (result.success && result.image_data) {
      const base64 = btoa(String.fromCharCode(...result.image_data))
      generatedImage.value = `data:image/png;base64,${base64}`
      generationTime.value = result.generation_time
      
      ElMessage.success('Texture generated successfully!')
    } else {
      throw new Error(result.error_message || 'Generation failed')
    }
  } catch (error) {
    ElMessage.error(`Generation failed: ${error}`)
  } finally {
    generating.value = false
  }
}

const saveTexture = async () => {
  if (!generatedImage.value) return
  
  try {
    await itemStore.saveTexture(generatedImage.value)
    ElMessage.success('Texture saved successfully!')
  } catch (error) {
    ElMessage.error('Failed to save texture')
  }
}
</script>

<style scoped>
.item-generator {
  height: 100%;
}

.generator-card, .preview-card {
  height: 600px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.generator-form {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-weight: 600;
  color: #333;
}

.input-label {
  font-size: 12px;
  color: #666;
  text-align: center;
  margin-top: 5px;
}

.action-buttons {
  display: flex;
  gap: 10px;
  margin-top: auto;
}

.preview-content {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-state {
  text-align: center;
  color: #666;
}

.loading-state .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.generated-result {
  text-align: center;
}

.texture-preview img {
  max-width: 200px;
  max-height: 200px;
  image-rendering: pixelated;
  border: 2px solid #ddd;
  border-radius: 8px;
}

.texture-info {
  margin-top: 16px;
  text-align: left;
  color: #666;
}

.empty-state {
  text-align: center;
  color: #999;
}

.empty-state .el-icon {
  font-size: 64px;
  margin-bottom: 16px;
  color: #ddd;
}

.hint {
  font-size: 14px;
  color: #ccc;
}
</style>