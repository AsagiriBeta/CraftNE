<template>
  <div id="app">
    <el-container class="app-container">
      <el-header class="app-header">
        <div class="header-content">
          <h1 class="app-title">
            <el-icon><Cpu /></el-icon>
            CraftNE - Minecraft AI Toolkit
          </h1>
          <div class="header-actions">
            <el-button @click="openSettings" type="primary" plain>
              <el-icon><Setting /></el-icon>
              Settings
            </el-button>
          </div>
        </div>
      </el-header>
      
      <el-container>
        <el-aside width="200px" class="sidebar">
          <el-menu
            :default-active="activeTab"
            @select="handleMenuSelect"
            class="sidebar-menu"
          >
            <el-menu-item index="skin">
              <el-icon><Avatar /></el-icon>
              <span>Skin Generator</span>
            </el-menu-item>
            <el-menu-item index="item">
              <el-icon><Box /></el-icon>
              <span>Item Texture</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Cpu, Setting, Avatar, Box } from '@element-plus/icons-vue'

const router = useRouter()
const activeTab = ref('skin')

const handleMenuSelect = (key: string) => {
  activeTab.value = key
  router.push(`/${key}`)
}

const openSettings = () => {
  // 打开设置页面
}
</script>

<style scoped>
.app-container {
  height: 100vh;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.app-title {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 24px;
  font-weight: 600;
}

.sidebar {
  background: #f5f5f5;
  border-right: 1px solid #e0e0e0;
}

.sidebar-menu {
  border: none;
  background: transparent;
}

.main-content {
  background: #fafafa;
  padding: 20px;
}
</style>