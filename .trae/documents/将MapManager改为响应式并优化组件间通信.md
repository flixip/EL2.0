# 修改计划：将MapManager改为响应式并优化组件间通信

## 问题分析
1. **导入方式问题**：在 `AddedDataList.vue` 和 `SearchSection.vue` 中，导入 `mapManagerRef` 的方式不正确
2. **本地状态冗余**：`AddedDataList.vue` 和 `SearchSection.vue` 中仍然有本地的 `layers` 变量，这些变量没有与 `mapManager` 中的数据保持同步
3. **响应式处理**：需要确保 `mapManager` 的数据变化能够及时反映到组件中

## 修改方案

### 1. 修改 MapContainer.vue
- 将 `mapManagerRef` 改为默认导出，方便其他组件导入
- 保持现有的响应式实现

### 2. 修改 AddedDataList.vue
- 修正导入方式，使用正确的默认导入
- 移除本地的 `layers` 变量，直接使用 `mapManager` 中的数据
- 确保 `addedGeoData` 始终与 `mapManager.getSelectedRegionList()` 保持同步
- 优化 `handleRemoveGeoData` 方法，直接操作 `mapManager`

### 3. 修改 SearchSection.vue
- 修正导入方式，使用正确的默认导入
- 移除本地的 `layers` 变量，直接使用 `mapManager` 中的数据
- 确保 `addedGeoData` 始终与 `mapManager.getSelectedRegionList()` 保持同步
- 优化 `handleAddGeoData` 方法，直接操作 `mapManager`

## 预期效果
- 组件间通信更加简洁高效
- 数据状态保持一致，避免冗余
- 响应式处理更加完善，确保地图数据变化能够及时反映到UI中
- 代码结构更加清晰，减少不必要的本地状态