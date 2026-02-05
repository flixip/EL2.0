<template>
  <div ref="mapContainer" class="w-full h-full relative overflow-hidden"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import MapManager from '@/tools/mapManager';

const mapContainer = ref(null);
const mapManager = MapManager.getInstance();

onMounted(() => {
  if (mapContainer.value) {
    // 使用 MapManager 的默认配置初始化地图
    mapManager.initMap(mapContainer.value);
  }
});

onUnmounted(() => {
  mapManager.destroy();
});

// 暴露 MapManager 实例，方便特殊情况下的父组件访问
defineExpose({
  getMapManager: () => mapManager
});
</script>

