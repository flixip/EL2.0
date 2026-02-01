# 事件监听与处理 (Event Handling)

Leaflet 对象（Map, Layer, Marker 等）都继承自 `Evented` 类，支持标准的事件驱动模型。

## 常用地图事件

```typescript
const initMapEvents = (map: L.Map) => {
  // 1. 点击事件：获取坐标
  map.on('click', (e: L.LeafletMouseEvent) => {
    console.log(`纬度: ${e.latlng.lat}, 经度: ${e.latlng.lng}`);
  });

  // 2. 缩放事件：响应层级变化
  map.on('zoomend', () => {
    console.log('当前缩放层级:', map.getZoom());
  });

  // 3. 移动事件：监控中心点变化
  map.on('moveend', () => {
    console.log('当前地图中心:', map.getCenter());
  });
};
```

## 常用图层事件
图层事件通常在创建图层或在 `onEachFeature` 中绑定。

```typescript
marker.on('mouseover', (e) => {
  marker.openPopup();
});
```
