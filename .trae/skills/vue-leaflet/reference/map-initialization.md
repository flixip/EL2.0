# 地图初始化与生命周期 (Map Initialization & Lifecycle)

在 Vue 3 中初始化 Leaflet 地图需要严格遵循生命周期钩子，以确保 DOM 已就绪且避免内存泄漏。

## 标准模板

```vue
<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue';
import L from 'leaflet';

const mapContainer = ref<HTMLElement | null>(null);
let map: L.Map | null = null; // 核心建议：不要用 ref 代理 map 实例

onMounted(() => {
  if (!mapContainer.value) return;

  // 1. 初始化实例
  map = L.map(mapContainer.value, {
    center: [39.9042, 116.4074], // [纬度, 经度]
    zoom: 12,
    zoomControl: false, // 推荐禁用默认，手动添加以便控制位置
    attributionControl: false // 推荐隐藏，除非有版权强制要求
  });

  // 2. 挂载底图等后续操作...
});

onUnmounted(() => {
  // 重要：组件销毁时必须手动移除地图实例，防止内存泄漏
  if (map) {
    map.remove();
    map = null;
  }
});
</script>

<template>
  <!-- 容器必须有明确的高度 -->
  <div ref="mapContainer" class="w-full h-[600px]"></div>
</template>
```

## 核心建议
- **避免使用 `ref` 或 `reactive` 包装 `map` 实例**：Leaflet 实例内部有大量的相互引用，Vue 的响应式代理会大幅降低地图渲染性能，甚至导致崩溃。
