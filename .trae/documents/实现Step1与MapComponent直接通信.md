# MapComponent.vue 代码优化方案

## 问题分析

分析了MapComponent.vue中的代码，发现以下未使用的内容：

1. **未使用的导入模块**：
   - `{ getGeojson, pathmap }` - 这些功能已移到MapManager中
   - `geoDataService` - 这些功能已移到MapManager中
   - `ref` - 导入但未使用

2. **未使用的变量**：
   - `layers` - 图层管理已移到MapManager中

3. **方法使用情况**：
   - `loadExtension()` - 被onMounted调用，有用
   - `addBaseControlandLayer(map)` - 被initMap调用，有用
   - `initMap()` - 被onMounted调用，有用
   - `handleRegionSelected(regionData)` - 被defineExpose暴露，有用
   - `clearSelectedRegionLayers()` - 被defineExpose暴露，有用
   - `resetMap()` - 被defineExpose暴露，有用

## 优化方案

1. **移除未使用的导入**：
   - 删除`{ getGeojson, pathmap }`导入
   - 删除`geoDataService`导入
   - 删除`ref`导入

2. **移除未使用的变量**：
   - 删除`layers`变量定义

3. **保持必要的方法**：
   - 保留所有被调用或暴露的方法
   - 确保方法逻辑正确

## 技术实现要点

1. **代码清理**：
   - 移除未使用的代码，提高代码可读性
   - 保持代码简洁性

2. **功能保持**：
   - 确保所有必要的功能正常工作
   - 保持与MapManager的正确交互

3. **向后兼容性**：
   - 确保暴露的方法接口不变
   - 确保父组件调用不受影响

## 预期效果

- 代码更加简洁，移除了未使用的内容
- 保持所有必要的功能
- 提高代码可读性和维护性

## 实现步骤

1. 修改MapComponent.vue，移除未使用的导入和变量
2. 运行诊断工具，确保代码没有语法错误
3. 测试功能是否正常工作
