<template>
  <div class="data-analyse-container">
    <!-- 左侧整合侧边栏 -->
    <DataSidebar ref="sidebarRef" />
    
    <!-- 右侧地图容器 -->
    <el-main class="map-container relative">
      <MapContainer ref="mapContainerRef" />
      <TimeAxis :visible="sidebarRef?.isTimeAxisEnabled" />
    </el-main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import MapContainer from '@/components/DataAnalyse/MapContainer.vue';
import DataSidebar from '@/components/DataAnalyse/DataSidebar.vue';
import TimeAxis from '@/components/DataAnalyse/TimeAxis.vue';

// 组件引用
const mapContainerRef = ref(null);
const sidebarRef = ref(null);
</script>

<style scoped>
.data-analyse-container {
  display: flex;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.map-container {
  flex: 1;
  padding: 0;
  margin: 0;
  overflow: hidden;
}
</style>

<style>
/* 全局样式调整 */
.el-aside {
  height: 100vh;
}

.el-main {
  height: 100vh;
  padding: 0;
}
</style>