## 实现 DataAnalyse 多功能数据面板

### 1. 扩展 MapManager 核心状态

* **文件**: `frontend/src/tools/mapManager.ts`

* **操作**:

  * 增加 `mapConfig` 响应式对象（颜色、NDVI 范围、Gamma、透明度）。

  * 增加 `timeConfig` 响应式对象（当前年份、范围）。

  * 增加 `updateLayerStyles()` 方法，用于统一刷新所有 GeoJSON 图层的样式和 Label。

  * 实现 `getIndexColor` 工具函数，支持线性插值和 Gamma 校正。

### 2. 创建示例数据与工具类

* **文件**: `frontend/src/data/sampleData.ts`

* **内容**: 迁移原项目的 `ndviData` 和 `boundsDict`，作为默认演示数据。

### 3. 开发 DataPanel 多功能面板

* **文件**: `frontend/src/components/DataAnalyse/DataPanel.vue`

* **功能**:

  * 使用 `el-collapse` 实现手风琴切换。

  * **可视化统计**: 集成 Chart.js 展示趋势。

  * **样式调整**: 实时修改 MapManager 中的 `mapConfig`。

  * **数据解析**: 实现 CSV/Excel 上传逻辑，支持字段关联（Mapping）。

### 4. 开发 TimeAxis 时间轴组件

* **文件**: `frontend/src/components/DataAnalyse/TimeAxis.vue`

* **功能**:

  * 实现悬浮底部的时间滑块。

  * 与 MapManager 的 `timeConfig.yearIndex` 绑定。

### 5. 地图交互集成

* **文件**: `frontend/src/tools/mapManager.ts`

* **逻辑**:

  * 在 `handleRegionSelected` 中增加 Hover (缩放/阴影) 和双击选中逻辑。

  * 实现动态 HTML 标注 (L.marker) 显示数据值。

### 6. UI/UX 优化

* **规范**: 严格执行 Tailwind CSS 编排规范。

* **交互**: 确保侧边栏收起时，数据面板能自适应或平滑过渡。

