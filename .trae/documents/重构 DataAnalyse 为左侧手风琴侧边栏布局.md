## 重构 DataAnalyse 布局：整合左侧手风琴侧边栏

### 1. 创建全新的 `DataSidebar.vue` 组件
- **文件位置**: `frontend/src/components/DataAnalyse/DataSidebar.vue`
- **核心逻辑**:
    - 采用 `NodePanel.vue` 的可折叠侧边栏设计（宽度在 64/16 之间切换）。
    - 侧边栏头部包含标题“数据分析与管理”及收缩/展开按钮。
    - **内容区域**：使用 `el-collapse` 实现手风琴效果，包含以下四个部分：
        1. **数据管理 (Data Management)**：整合 `SearchSection.vue` 和 `AddedDataList.vue`。
        2. **数据可视化 (Visualization)**：整合原 `DataPanel.vue` 的图表统计逻辑。
        3. **图层配置 (Configuration)**：整合原 `DataPanel.vue` 的颜色、透明度、阈值调整。
        4. **数据导入 (Import)**：整合原 `DataPanel.vue` 的 CSV 上传与映射逻辑。
    - **折叠状态**：侧边栏收缩时，仅显示代表各功能的图标，悬停显示 Tooltip。

### 2. 重构 `DataAnalyse.vue` 视图
- **操作**:
    - 移除原有的 `el-aside` 结构。
    - 在左侧引入 `DataSidebar.vue`。
    - 移除右侧悬浮的 `DataPanel.vue`。
    - 更新 `TimeAxis.vue` 的显示逻辑，使其与 `DataSidebar` 的时间轴开关关联。

### 3. 样式与交互优化
- **Tailwind 规范**: 统一侧边栏背景色、边框和阴影。
- **动画**: 确保侧边栏展开/收起时，内容文字和图标平滑过渡（opacity/scale）。
- **组件清理**: 在确认 `DataSidebar.vue` 正常工作后，删除或归档 `DataPanel.vue`。

### 4. 依赖同步
- 确保 `DataSidebar.vue` 正确引入 `MapManager` 并管理其响应式状态。
- 确保 `Chart.js` 的生命周期在侧边栏切换时正确处理（挂载/销毁）。