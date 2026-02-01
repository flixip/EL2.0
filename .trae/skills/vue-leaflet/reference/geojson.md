# GeoJSON 数据加载与样式 (GeoJSON Data)

Leaflet 内置了强大的 GeoJSON 支持，可用于展示矢量面、线和点要素。

## 综合示例

```typescript
const addGeoJSON = (map: L.Map, data: any) => {
  L.geoJSON(data, {
    // 1. 样式定义 (仅限面和线)
    style: (feature) => ({
      color: feature?.properties.color || '#3388ff',
      weight: 2,
      opacity: 1,
      fillOpacity: 0.2
    }),

    // 2. 点要素渲染 (默认是 Marker，常改为 CircleMarker)
    pointToLayer: (feature, latlng) => {
      return L.circleMarker(latlng, {
        radius: 8,
        fillColor: "#ff7800",
        color: "#000",
        weight: 1,
        fillOpacity: 0.8
      });
    },

    // 3. 交互与弹出层绑定
    onEachFeature: (feature, layer) => {
      if (feature.properties && feature.properties.name) {
        layer.bindPopup(`<b>名称:</b> ${feature.properties.name}`);
      }
      layer.on('click', () => {
        console.log('要素点击:', feature);
      });
    }
  }).addTo(map);
};
```
