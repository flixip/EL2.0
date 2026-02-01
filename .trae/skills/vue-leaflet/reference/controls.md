# 地图控件管理 (Map Controls)

Leaflet 提供了标准的 UI 控件，如缩放条、比例尺、图层切换器。

## 1. 缩放控件与比例尺

```typescript
// 缩放控件 (推荐放在右下角)
L.control.zoom({ position: 'bottomright' }).addTo(map);

// 比例尺 (推荐禁用英制单位)
L.control.scale({ imperial: false }).addTo(map);
```

## 2. 图层切换控件 (L.Control.Layers)

```typescript
const baseMaps = {
  "高德矢量": L.tileLayer(/*...*/),
  "高德卫星": L.tileLayer(/*...*/)
};

const overlayMaps = {
  "业务点位": L.layerGroup([marker1, marker2]),
  "热力图": L.layerGroup()
};

L.control.layers(baseMaps, overlayMaps, { 
  collapsed: true // 初始是否折叠
}).addTo(map);
```
