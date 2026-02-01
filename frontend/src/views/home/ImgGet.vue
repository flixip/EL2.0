<template>
  <div 
  class="flex h-full w-full"
  >
    <!-- 地图区域 -->
    <div
    class="flex-1 max-h-full p-2">
      <MapComponent ref="mapComponentRef" />
    </div>
    
    <!-- 右侧面板 -->
    <div
    class="max-h-full max-w-[500px] ">
      <RightPanel />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import MapComponent from '@/components/ImgGet/MapComponent.vue';
import RightPanel from '@/components/ImgGet/RightPanel.vue';

const mapComponentRef = ref(null);
</script>

