<template>
  <div ref="mapContainer" class="h-full w-full relative overflow-hidden"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import MapManager from '@/tools/mapManager';
import L from 'leaflet';
import '@/assets/leaflet.ChineseTmsProviders.js';

const mapContainer = ref(null);
const mapManager = MapManager.getInstance();

const loadExtension = () => {
  // 动态加载Leaflet Draw插件
  if (!document.querySelector('script[src*="leaflet.draw"]')) {
    const drawScript = document.createElement('script');
    drawScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.2/leaflet.draw.js';
    document.body.appendChild(drawScript);

    const drawCss = document.createElement('link');
    drawCss.href = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.2/leaflet.draw.css';
    drawCss.rel = 'stylesheet';
    document.head.appendChild(drawCss);
  }

  // 动态加载Fullscreen插件
  if (!document.querySelector('script[src*="Control.FullScreen"]')) {
    const fullscreenScript = document.createElement('script');
    fullscreenScript.src = 'https://cdn.jsdelivr.net/npm/leaflet.fullscreen@3.0.0/Control.FullScreen.min.js';
    document.body.appendChild(fullscreenScript);

    const fullscreenCss = document.createElement('link');
    fullscreenCss.href = 'https://cdn.jsdelivr.net/npm/leaflet.fullscreen@3.0.0/Control.FullScreen.css';
    fullscreenCss.rel = 'stylesheet';
    document.head.appendChild(fullscreenCss);
  }
};

const addBaseControlandLayer = (map) => {
  try {
    const baseLayers = {
     
      '高德卫星': L.tileLayer.chinaProvider('GaoDe.Satellite.Map', {
        maxZoom: 18,
        minZoom: 3
      }),
      'Google地图': L.tileLayer.chinaProvider('Google.Normal.Map', {
        maxZoom: 18,
        minZoom: 3
      }),
      'Google卫星': L.tileLayer.chinaProvider('Google.Satellite.Map', {
        maxZoom: 18,
        minZoom: 3
      })
    };
    
    // 将这些底图添加到 MapManager 管理的控制器中
    Object.entries(baseLayers).forEach(([name, layer]) => {
      mapManager.addBaseLayer(layer, name);
    });

  } catch (error) {
    console.warn('China baseLayers not loaded:', error);
  }

  try {
    if (L.control.fullscreen) {
      map.addControl(L.control.fullscreen());
    }
  } catch (error) {
    console.warn('Fullscreen plugin not loaded:', error);
  }

  try {
    if (L.Control.Draw) {
      map.addControl(new L.Control.Draw({
        position: 'topleft',
        draw: {
          polygon: true,
          polyline: false,
          circle: false,
          marker: false,
          rectangle: true,
        }
      }));
    }
  } catch (error) {
    console.warn('Draw plugin not loaded:', error);
  }
};

const initMap = async () => {
  if (mapContainer.value) {
    const mapInstance = mapManager.initMap(mapContainer.value, {
      center: [34.3416, 108.9398],
      zoom: 5,
      zoomControl: true,
      attributionControl: false
    });

    if (mapInstance) {
      addBaseControlandLayer(mapInstance);
      await mapManager.addChinaProvsGeojsonLayer();
    }
  }
};

onMounted(() => {
  loadExtension();
  initMap();
});

onUnmounted(() => {
  mapManager.destroy();
});


</script>
