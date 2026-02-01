# 修复 DataAnalyse 地图逻辑

依据 `vue-leaflet` Skill 规范，对地图容器组件及业务页面进行重构，核心目标是确保性能稳定（避免响应式代理 map 实例）并统一地图初始化流程。

## 1. 优化 MapContainer.vue

* **初始化增强**：在 `initMap` 中自动挂载高德地图瓦片图层，提供基础底图。

* **性能保护**：确保 `map` 实例保持为普通变量，不被 `ref` 或 `reactive` 包装。

* **安全暴露**：从 `defineExpose` 中移除原始 `map` 实例，改为暴露受控的方法（如 `addLayer`, `removeLayer`, `fitBounds`），防止父组件误将其变为响应式对象。

## 2. 重构 DataAnalyse.vue

* **解耦逻辑**：移除冗余的 `onUnmounted` 销毁逻辑，由 `MapContainer` 自行管理生命周期。

* **API 适配**：通过 `MapContainer` 暴露的方法来操作图层，不再直接操作 `map` 实例。

* <br />

## 3. 验证

* 检查地图是否能正确加载底图。

* 验证 GeoJSON 数据添加后是否能正确缩放至要素范围且样式符合预期。

* 确认组件销毁时无内存泄漏风险。

