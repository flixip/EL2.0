# 瓦片图层管理 (Tile Layers)

Leaflet 支持通过 XYZ 模板加载各种在线瓦片服务。

## 1. 高德地图 (推荐)
速度快，符合中国地理习惯。

```typescript
const amapLayer = L.tileLayer('https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}', {
  subdomains: ['1', '2', '3', '4'],
  minZoom: 1,
  maxZoom: 18,
  attribution: '高德地图'
});
amapLayer.addTo(map);
```

## 2. OpenStreetMap (OSM)
国际通用，但国内加载可能较慢。

```typescript
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);
```

## 3. 注意事项
- 不同底图的坐标系可能不同（如 GCJ-02 与 WGS-84），在大比例尺下需注意坐标偏移校正。
