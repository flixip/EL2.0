---
name: "vue-leaflet"
description: "Handles Leaflet map integration in Vue 3. Provides simplified API index and detailed implementation references. Invoke for any map-related features."
---

# Vue 3 Leaflet Skill Index

This skill manages map integration using Leaflet. **CRITICAL: Always consult the [Reference Folder](file:///e:/github/EL2.0/.trae/skills/vue-leaflet/reference) for detailed implementation logic and best practices before generating code.**

## 1. Core API Summary

### **Map Lifecycle**
- `L.map(el: HTMLElement, options: L.MapOptions): L.Map` - Initialize map.
- `map.remove(): void` - Destroy map instance (onUnmounted).

### **Layer Management**
- `L.tileLayer(url: string, options: any): L.TileLayer` - Standard tile provider.
- `L.geoJSON(data: any, options: L.GeoJSONOptions): L.GeoJSON` - Vector data.
- `layer.addTo(map: L.Map): L.Layer` - Attach layer to map.

### **Navigation & Events**
- `map.setView(center: L.LatLngExpression, zoom: number): L.Map` - Jump to view.
- `map.flyTo(center: L.LatLngExpression, zoom?: number): L.Map` - Smooth transition.
- `map.on(event: string, fn: Function): L.Map` - Event listener.

## 2. Implementation References

Refer to the following documents for recommended operations:

- [**Setup**](file:///e:/github/EL2.0/.trae/skills/vue-leaflet/reference/setup.md): Installation and core CSS import.
- [**Plugins**](file:///e:/github/EL2.0/.trae/skills/vue-leaflet/reference/plugins.md): Strategies for loading ESM or Legacy plugins.
- [**Map Initialization**](file:///e:/github/EL2.0/.trae/skills/vue-leaflet/reference/map-initialization.md): Standard Vue 3 setup and performance tips.
- [**Tile Layers**](file:///e:/github/EL2.0/.trae/skills/vue-leaflet/reference/tile-layers.md): Recommended Chinese and Global tile providers.
- [**GeoJSON**](file:///e:/github/EL2.0/.trae/skills/vue-leaflet/reference/geojson.md): Data loading, styling, and feature interaction.
- [**Events**](file:///e:/github/EL2.0/.trae/skills/vue-leaflet/reference/events.md): Handling clicks, zoom, and layer-specific events.
- [**Controls**](file:///e:/github/EL2.0/.trae/skills/vue-leaflet/reference/controls.md): UI components like zoom, scale, and layer switchers.

## 3. Workflow Requirement

1.  Identify the required map feature (e.g., "Add a search plugin").
2.  Open the corresponding reference file in `.trae/skills/vue-leaflet/reference/`.
3.  Implement the feature following the documented templates and "Performance Best Practices".
