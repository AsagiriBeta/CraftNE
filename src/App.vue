<template>
  <div id="app">
    <el-container class="app-container">
      <el-header class="app-header">
        <div class="header-content">
          <h1 class="app-title">
            <el-icon><Cpu /></el-icon>
            CraftNE
          </h1>
          <div class="header-subtitle">Minecraft AI Development Toolkit</div>
        </div>
      </el-header>
      
      <el-container>
        <el-aside width="250px" class="sidebar">
          <el-menu
            :default-active="$route.path"
            router
            mode="vertical"
            class="nav-menu"
          >
            <el-menu-item index="/">
              <el-icon><House /></el-icon>
              <span>首页</span>
            </el-menu-item>
            <el-menu-item index="/map">
              <el-icon><MapLocation /></el-icon>
              <span>地图生成</span>
            </el-menu-item>
            <el-menu-item index="/skin">
              <el-icon><Avatar /></el-icon>
              <span>皮肤生成</span>
            </el-menu-item>
            <el-menu-item index="/texture">
              <el-icon><Picture /></el-icon>
              <span>材质生成</span>
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
import { House, MapLocation, Avatar, Picture, Cpu } from "@element-plus/icons-vue";
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
  align-items: center;
  gap: 15px;
}

.app-title {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 24px;
  font-weight: bold;
}

.header-subtitle {
  font-size: 14px;
  opacity: 0.8;
}

.sidebar {
  background-color: #f5f7fa;
  border-right: 1px solid #e4e7ed;
}

.nav-menu {
  border: none;
}

.main-content {
  padding: 20px;
  background-color: #ffffff;
}
</style>