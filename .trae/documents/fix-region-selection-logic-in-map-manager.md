# 修复搜索添加图层时区域识别错误的问题

## 1. 分析原因

在 `MapManager.ts` 的 `handleRegionSelected` 方法中，获取区域名称的逻辑存在缺陷：

```typescript
const regionName = regionData.province || regionData.name;
```

当搜索结果是一个城市（如“武汉市”）时，返回的数据对象同时包含 `name`（武汉市）和 `province`（湖北省）。由于逻辑中优先使用了 `province` 属性，导致 `regionName` 变成了“湖北省”，随后加载了整个省的矢量数据。

## 2. 修复方案

* **优化识别逻辑**：*在* *`MapManager.ts`* *中改*进区域识别策略。

  * 优先检查传入对象是否已经是完整的 `GeoDataItem`（具有 `path` 属性）。如果是，则直接使用，避免重复查找。

  * 如果需要按名称查找，优先使用 `name` 属性，将 `province` 作为备选（兼容旧代码中某些地方将区域名存放在 `province` 字段的情况）。

* **类型安全**：利用 TypeScript 类型检查确保数据处理的准确性。

## 3. 具体改动

* 修改 [mapManager.ts](file:///e:/github/EL2.0/frontend/src/tools/mapManager.ts) 中的 `handleRegionSelected` 方法。

* 确保在 `ImgGet`（使用级联选择器）和 `DataAnalyse`（使用搜索框）两种场景下都能准确识别选中的具体行政区划。

## 4. 验证

* 在数据分析页面搜索“武汉”，确认添加的是武汉市边界而非湖北省。

* 确认 ImgGet 页面原有的级联选择功能依然正常。

