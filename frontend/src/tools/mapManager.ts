import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { type Layer } from 'leaflet';
import { getGeojson, pathmap } from '@/tools/apiService';
import geoDataService, { type GeoDataItem } from '@/services/GeoDataService';
import { ref, shallowRef, computed, watch } from 'vue';
import TableManager from './tableManager';

// 地图初始化配置接口
interface MapConfig {
  center?: [number, number];
  zoom?: number;
  zoomControl?: boolean;
  attributionControl?: boolean;
}

// 可视化参数配置接口
export interface VisualizationConfig {
  startRGB: { r: number; g: number; b: number }; // 起始颜色（低值）
  endRGB: { r: number; g: number; b: number };   // 结束颜色（高值）
  opacity: number;      // 填充透明度
  gamma: number;        // Gamma 校正
  minValue: number;     // 最小值阈值
  maxValue: number;     // 最大值阈值
  showLabel: boolean;   // 是否显示标注
}

// 时间配置接口
export interface TimeConfig {
  yearIndex: number;    // 当前年份索引
  startYear: number;    // 起始年份
  yearRange: number;    // 年份范围
  isPlaying: boolean;   // 是否正在播放动画
}

/**
 * MapManager 地图管理器
 * 采用单例模式，集成 Vue 3 响应式系统
 * 解决跨组件状态同步与路由切换初始化问题
 */
export default class MapManager {
  private static instance: MapManager | null = null;
  private tableManager = TableManager.getInstance();
  
  // 使用 shallowRef 存储地图实例，避免深度响应式代理导致的性能问题
  public map = shallowRef<L.Map | null>(null);
  
  // 图层控制器引用
  private layerControl: L.Control.Layers | null = null;
  
  // 使用 ref 存储选中区域，使组件可以响应式地获取列表
  // 使用 any 是因为 info 可能包含不同结构的地理信息数据，但主要是 GeoDataItem
  private selectedRegions = ref<Map<string, { info: any; layer: L.Layer; labels?: L.LayerGroup }>>(new Map());

  // 可视化配置状态
  public mapConfig = ref<VisualizationConfig>({
    startRGB: { r: 230, g: 255, b: 237 },
    endRGB: { r: 4, g: 120, b: 87 },
    opacity: 0.7,
    gamma: 1.0,
    minValue: 0.2,
    maxValue: 0.4,
    showLabel: true
  });

  // 时间配置状态
  public timeConfig = ref<TimeConfig>({
    yearIndex: 0,
    startYear: 2000,
    yearRange: 0,
    isPlaying: false
  });

  // 当前选中的区县名称
  public selectedDistrict = ref<string | null>(null);

  private constructor() {
    // 监听 tableManager 的年份范围变化，同步到 timeConfig
    watch(() => this.tableManager.yearRange.value, (newVal) => {
      this.timeConfig.value.yearRange = newVal;
    });
  }

  /**
   * 获取单例实例
   * @returns {MapManager} MapManager 实例
   */
  public static getInstance(): MapManager {
    if (!MapManager.instance) {
      MapManager.instance = new MapManager();
    }
    return MapManager.instance;
  }

  /**
   * 初始化地图
   * 销毁实例，添加地图控制器，添加底图
   * @param {string | HTMLElement} containerId - 容器 ID 或 HTMLElement
   * @param {MapConfig} config - 地图配置项
   * @returns {L.Map | null} Leaflet 地图实例
   */
  public initMap(containerId: string | HTMLElement, config: MapConfig = {}): L.Map | null {
    // 如果已有实例，先销毁，确保路由切换时能重新挂载到新 DOM
    this.destroy();

    const {
      center = [34.3416, 108.9398],
      zoom = 5,
      zoomControl = true,
      attributionControl = false
    } = config;

    try {
      const mapInstance = L.map(containerId, {
        center,
        zoom,
        zoomControl,
        attributionControl,
        preferCanvas: true
      });

      // 初始化图层控制器
      this.layerControl = L.control.layers({}, {}).addTo(mapInstance);

      // 添加默认高德底图
      const amapLayer = L.tileLayer('https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}', {
        subdomains: ['1', '2', '3', '4'],
        minZoom: 1,
        maxZoom: 18,
        attribution: '高德地图'
      });

      amapLayer.addTo(mapInstance);
      this.layerControl.addOverlay(amapLayer, '高德地图');

      this.map.value = mapInstance;
      console.log('Map initialized successfully');
      return mapInstance;
    } catch (error) {
      console.error('Error initializing map:', error);
      this.map.value = null;
      return null;
    }
  }

  /**
   * 向控制器添加底图
   * @param {L.Layer} layer - 要添加的图层
   * @param {string} name - 图层名称
   * @param {boolean} show - 是否立即显示
   */
  public addBaseLayer(layer: L.Layer, name: string, show: boolean = false): void {
    if (this.layerControl) {
      this.layerControl.addBaseLayer(layer, name);
    }
    if (show && this.map.value) {
      layer.addTo(this.map.value);
    }
  }

  /**
   * 向控制器添加叠加层
   * @param {L.Layer} layer - 要添加的图层
   * @param {string} name - 图层名称
   * @param {boolean} show - 是否立即显示
   */
  public addOverlay(layer: L.Layer, name: string, show: boolean = false): void {
    if (this.layerControl) {
      this.layerControl.addOverlay(layer, name);
    }
    if (show && this.map.value) {
      layer.addTo(this.map.value);
    }
  }

  /**
   * 响应式获取选中区域列表
   * 看起来像方法，其实是执行后的方法，直接就返回选中区域的列表
   * @returns {any[]} 选中区域的数据列表
   */
  public get selectedRegionList() {
    return computed(() => Array.from(this.selectedRegions.value.values()).map(item => item.info));
  }

  /**
   * 处理区域选择
   * 在这里更新了响应式状态 selectedRegions，以region开头便于管理
   * @param {any} regionData - 区域数据，可能是 GeoDataItem 或其他包含地理信息的对象
   * @param {boolean} multiple - 是否支持多选，默认为 false
   * @param {any} style - 自定义样式对象
   * @returns {Promise<void>}
   */
  public async handleRegionSelected(regionData: any, multiple: boolean = false, style?: any): Promise<void> {
    if (!this.map.value) {
      throw new Error('地图未初始化');
    }
    console.log(regionData)
    try {
      if (!multiple) {
        this.clearSelectedRegions();
      }

      if (regionData.type === 'custom') return;

      // 1. 尝试直接从 regionData 中获取完整的地理数据项
      // 如果 regionData 本身就是 GeoDataItem (包含 path 属性)，或者包含完整的 data 属性
      // 这里使用类型断言 as any 是因为 regionData 结构不确定，我们需要检查 path 属性
      let geoDataItem: GeoDataItem | null = regionData.path ? (regionData as GeoDataItem) : (regionData.data && regionData.data.path ? regionData.data : null);
      let regionName = regionData.name || regionData.province;

      // 2. 如果没有直接获取到数据项，则根据名称查找
      if (!geoDataItem) {
        console.log('No direct geoDataItem found, searching by name:', regionName);
        geoDataItem = geoDataService.getGeoDataItemByName(regionName);
      }

      if (geoDataItem) {
        const geoJSONData = await geoDataService.loadGeoJSONData(geoDataItem);
        
        if (geoJSONData && geoJSONData.features.length > 0) {
          const regionLayer = L.geoJSON(geoJSONData as GeoJSON.GeoJsonObject, {
            style: (feature) => {
              // 优先使用具体 Feature 的名称，如果没有则回退到图层名
              const name = feature?.properties?.name || (geoDataItem as GeoDataItem).name;
              const data = this.tableManager.dataState.value.get(name);
              const val = data ? data[this.timeConfig.value.yearIndex] : null;
              
              return style || {
                color: '#333',
                weight: 1,
                opacity: 0.8,
                fillColor: val !== null ? this.getIndexColor(val) : '#ff4d4f',
                fillOpacity: this.mapConfig.value.opacity
              };
            },
            onEachFeature: (feature, layer) => {
              // 这里断言 geoDataItem 不为空，因为外层已经判断过
              const name = feature?.properties?.name || (geoDataItem as GeoDataItem).name;
              // 绑定弹窗
              layer.bindPopup(`<b>${name}</b>`);

              // 鼠标悬停效果
              // 使用 L.Path 类型断言，因为 GeoJSON 的 layer 通常是 Path (Polygon/Polyline)
              layer.on('mouseover', function (this: L.Path) {
                this.setStyle({
                  weight: 3,
                  color: '#fff',
                  fillOpacity: 0.9
                });
                this.bringToFront();
              });

              layer.on('mouseout', (e: L.LeafletMouseEvent) => {
                // 修复：不要使用 resetStyle，因为它会回退到图层创建时的初始样式（通常是无数据状态）
                // 而是重新计算并设置当前时间节点的正确样式
                // 使用 as any 访问 feature 属性，这是 Leaflet 事件目标的常见模式
                const featureName = (e.target as any).feature?.properties?.name || (geoDataItem as GeoDataItem).name;
                const data = this.tableManager.dataState.value.get(featureName);
                const val = data ? data[this.timeConfig.value.yearIndex] : null;
                
                // 断言为 L.Path 以访问 setStyle
                (e.target as L.Path).setStyle({
                  fillColor: val !== null ? this.getIndexColor(val) : '#ccc',
                  fillOpacity: this.mapConfig.value.opacity,
                  weight: 2,
                  color: '#333'
                });
              });

              // 双击缩放到区域并选中
              layer.on('dblclick', (e: L.LeafletMouseEvent) => {
                // 断言为 FeatureGroup 以访问 getBounds
                this.map.value?.fitBounds((e.target as L.FeatureGroup).getBounds());
                this.selectedDistrict.value = name;
              });

              // 单击选中
              layer.on('click', (e: L.LeafletMouseEvent) => {
                this.selectedDistrict.value = name;
              });
            }
          });

          regionLayer.addTo(this.map.value);
          
          // 添加到图层控制器
          this.layerControl?.addOverlay(regionLayer, geoDataItem.name);
          
          // 更新响应式状态
          this.selectedRegions.value.set(`region_${geoDataItem.id}`, {
            info: geoDataItem, 
            layer: regionLayer
          });

          // 加载新图层后，自动检查 TableManager 中是否有匹配的数据
          this.syncDataWithLayers();
          
          this.map.value.fitBounds(regionLayer.getBounds(), {
            padding: [50, 50],
            animate: true,
            duration: 1.5
          });
        }
      } else {
        console.error('Could not find GeoJSON data for region:', regionName);
        throw new Error(`未找到区域 "${regionName}" 的地理数据`);
      }
    } catch (error) {
      console.error('Error handling region selection:', error);
      throw error;
    }
  }

  /**
   * 加载中国省份 GeoJSON 图层
   * @returns {Promise<void>}
   */
  public async addChinaProvsGeojsonLayer(): Promise<void> {
    try {
      const data = await getGeojson(pathmap.all_prov_path);
      const chinaProvinceLayer = L.geoJSON(data, {
        style: {
          color: '#3388ff',
          weight: 2,
          fillColor: '#3388ff',
          fillOpacity: 0.3
        }
      });
      if (this.layerControl) {
        this.addOverlay(chinaProvinceLayer, '中国省界', true);
        this.selectedRegions.value.set('chinaProvince', {
          info: { id: 'chinaProvince', name: '中国省界' },
          layer: chinaProvinceLayer
        });
      }
    } catch (error) {
      console.error('Error loading China province layer:', error);
    }
  }

  /**
   * 清除特定区域或所有区域
   * @param {string | number} id - 区域 ID
   */
  public removeRegion(id: string | number): void {
    const key = `region_${id}`;
    const item = this.selectedRegions.value.get(key);
    if (item && this.map.value) {
      this.map.value.removeLayer(item.layer as Layer);
      this.layerControl?.removeLayer(item.layer as Layer);
      if (item.labels) {
        this.map.value.removeLayer(item.labels);
      }
      this.selectedRegions.value.delete(key);
      if (this.selectedDistrict.value === item.info.name) {
        this.selectedDistrict.value = null;
      }
    }
  }

  /**
   * 清除所有选中区域
   */
  public clearSelectedRegions(): void {
    if (this.map.value) {
      this.selectedRegions.value.forEach(item => {
        this.map.value?.removeLayer(item.layer as Layer);
        this.layerControl?.removeLayer(item.layer as Layer);
        if (item.labels) {
          this.map.value?.removeLayer(item.labels);
        }
      });
    }
    this.selectedRegions.value.clear();
    this.selectedDistrict.value = null;
  }

  /**
   * 重置地图视角
   */
  public resetMapView(): void {
    if (this.map.value) {
      this.map.value.setView([34.3416, 108.9398], 5, {
        animate: true,
        duration: 1.5
      });
    }
  }

  /**
   * 根据数值计算颜色 (插值 + Gamma 校正)
   * @param {number} value - 输入数值
   * @returns {string} RGB 颜色字符串
   */
  public getIndexColor(value: number): string {
    const { startRGB, endRGB, minValue, maxValue, gamma } = this.mapConfig.value;
    
    // 1. 钳位并归一化
    let t = (value - minValue) / (maxValue - minValue);
    t = Math.max(0, Math.min(1, t));
    
    // 2. Gamma 校正
    t = Math.pow(t, gamma);
    
    // 3. 线性插值计算 RGB
    const r = Math.round(startRGB.r + (endRGB.r - startRGB.r) * t);
    const g = Math.round(startRGB.g + (endRGB.g - startRGB.g) * t);
    const b = Math.round(startRGB.b + (endRGB.b - startRGB.b) * t);
    
    return `rgb(${r}, ${g}, ${b})`;
  }

  /**
   * 刷新所有已加载图层的样式和标注
   */
  public updateLayerStyles(): void {
    if (!this.map.value) return;

    this.selectedRegions.value.forEach((item, key) => {
      // 修复：在为该区域组重新添加标注前，先清空旧标注，防止叠加
      if (item.labels) {
        item.labels.clearLayers();
      }

      // 1. 更新图层样式
      if (item.layer instanceof L.GeoJSON) {
        item.layer.eachLayer((layer: any) => {
          // 针对 GeoJSON 图层，需要检查内部每个 Feature 的名称
          const featureName = layer.feature?.properties?.name || item.info.name;
          const data = this.tableManager.dataState.value.get(featureName);
          const val = data ? data[this.timeConfig.value.yearIndex] : null;

          layer.setStyle({
            fillColor: val !== null ? this.getIndexColor(val) : '#ccc',
            fillOpacity: this.mapConfig.value.opacity,
            weight: 2,
            color: '#333'
          });

          // 2. 更新标注 (Label)
          if (this.mapConfig.value.showLabel && val !== null) {
            if (!item.labels) {
              // 这里的 ! 断言 map.value 不为空，因为前面已经检查过
              item.labels = L.layerGroup().addTo(this.map.value!);
            }
            // 注意：每个 Feature 可能都需要一个独立的 Label
            // 这里简单处理：如果图层有多个 Feature，我们尝试在每个 Feature 中心点加 Label
            this.updateFeatureLabel(item.labels, layer, featureName, val);
          }
        });
      }
    });
  }

  /**
   * 为特定 Feature 更新或添加 Label
   * @param {L.LayerGroup} labelGroup - 标注图层组
   * @param {any} layer - 目标图层 (Feature)
   * @param {string} name - 区域名称
   * @param {number} value - 显示数值
   */
  private updateFeatureLabel(labelGroup: L.LayerGroup, layer: any, name: string, value: number): void {
    let center: L.LatLng | null = null;
    // 检查 layer 是否有 getBounds 方法 (Polygon/Polyline)
    if (layer.getBounds) {
      center = layer.getBounds().getCenter();
    } else if (layer.getLatLng) {
      // 检查 layer 是否有 getLatLng 方法 (Marker)
      center = layer.getLatLng();
    }

    if (center) {
      const labelHtml = `
        <div class="glass-dark px-2 py-1 rounded text-[10px] text-center shadow border border-white/20">
          <div class="font-bold text-emerald-400">${name}</div>
          <div class="text-white">${value.toFixed(4)}</div>
        </div>
      `;
      L.marker(center, {
        icon: L.divIcon({
          className: 'custom-div-icon',
          html: labelHtml,
          iconSize: [60, 40],
          iconAnchor: [30, 20]
        }),
        interactive: false
      }).addTo(labelGroup);
    }
  }

  /**
   * 同步数据与图层关联
   * 遍历现有图层，尝试在 TableManager 中查找匹配数据并应用
   */
  public syncDataWithLayers(): void {
    this.updateLayerStyles();
  }

  /**
   * 自动加载数据中缺失的图层
   * @param {string[]} regionNames - 区域名称列表
   * @returns {Promise<void>}
   */
  public async autoLoadMissingLayers(regionNames: string[]): Promise<void> {
    for (const name of regionNames) {
      // 检查是否已经加载
      const alreadyLoaded = Array.from(this.selectedRegions.value.values()).some(item => {
        if (item.info.name === name) return true;
        // 检查 GeoJSON 内部 Feature
        let found = false;
        if (item.layer instanceof L.GeoJSON) {
          item.layer.eachLayer((l: any) => {
            if (l.feature?.properties?.name === name) found = true;
          });
        }
        return found;
      });

      if (!alreadyLoaded) {
        const geoDataItem = geoDataService.getGeoDataItemByName(name);
        if (geoDataItem) {
          await this.handleRegionSelected(geoDataItem, true);
        }
      }
    }
  }

  /**
   * 销毁地图实例
   */
  public destroy(): void {
    if (this.map.value) {
      this.map.value.remove();
      this.map.value = null;
    }
    this.layerControl = null;
    // 注意：如果是单例且希望跨页面保留状态，则不清除 selectedRegions
    // 但图层引用必须失效，因为它们属于旧地图
    this.selectedRegions.value.clear();
  }
}
