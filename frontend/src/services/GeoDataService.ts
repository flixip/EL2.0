import { getGeoDataMap, getGeoJSONData, generateGeoDataUrl } from '@/tools/apiService';

// 地理数据类型定义
export interface GeoDataItem {
  id: string;
  name: string;
  type: 'province' | 'city';
  path: string;
  province?: string; // 城市所属省份
}

export interface GeoJSONData {
  type: string;
  features: any[];
}

// 地理数据映射表接口
interface GeoDataMap {
  China_provs: {
    [provinceName: string]: {
      json: string;
      二级区划: {
        [cityName: string]: string;
      };
    };
  };
}

// 地理数据检索服务类
export class GeoDataService {
  private static instance: GeoDataService;
  private provinces: GeoDataItem[] = [];
  private cities: GeoDataItem[] = [];
  private geoDataMap: GeoDataMap | null = null;
  private loaded: boolean = false;
  private isdebug: boolean;

  private constructor(debug: boolean = true) {
    this.isdebug = debug;
  }

  // 单例模式
  public static getInstance(): GeoDataService {
    if (!GeoDataService.instance) {
      GeoDataService.instance = new GeoDataService();
    }
    return GeoDataService.instance;
  }

  // 初始化数据
  public async initialize(): Promise<void> {
    if (this.loaded) {
      console.log('GeoDataService already initialized');
      return;
    }

    try {
      console.log('Initializing GeoDataService...');
      // 加载地理数据映射表
      await this.loadGeoDataMap();
      console.log('Geo data map loaded successfully');
      // 加载省份数据
      this.loadProvinces();
      console.log('Provinces loaded successfully');
      // 加载城市数据
      this.loadCities();
      console.log('Cities loaded successfully');
      this.loaded = true;
      console.log('GeoDataService initialized successfully');
    } catch (error) {
      console.error('Failed to initialize geo data service:', error);
      const errorMessage = error instanceof Error ? error.message : '未知错误';
      throw new Error(`地理数据服务初始化失败: ${errorMessage}`);
    }
  }

  // 检查初始化状态
  public isInitialized(): boolean {
    return this.loaded;
  }

  // 获取初始化状态
  public getInitializedStatus(): boolean {
    return this.loaded;
  }

  // 加载地理数据映射表
  private async loadGeoDataMap(): Promise<void> {
    try {
      // 使用 apiService 中的方法获取地理数据映射表
      this.geoDataMap = await getGeoDataMap();
      if (this.isdebug) {
        console.log('Geo data map loaded successfully:', this.geoDataMap);
      }
    } catch (error) {
      console.error('Failed to load geo data map:', error);
      throw error;
    }
  }

  // 加载省份数据
  private loadProvinces(): void {
    if (!this.geoDataMap) return;

    const provinceNames = Object.keys(this.geoDataMap.China_provs);
    this.provinces = provinceNames.map((name, index) => ({
      id: `province_${index + 1}`,
      name,
      type: 'province' as const,
      path: `China_provs/${name}/${this.geoDataMap!.China_provs[name]!.json}`
    }));
    if (this.isdebug) {
      console.log('Provinces loaded successfully:', this.provinces);
    }
  }

  // 加载城市数据
  private loadCities(): void {
    if (!this.geoDataMap) return;

    let cityId = 1;
    Object.entries(this.geoDataMap.China_provs).forEach(([provinceName, provinceData]) => {
      Object.entries(provinceData.二级区划).forEach(([cityName, cityJson]) => {
        this.cities.push({
          id: `city_${cityId++}`,
          name: cityName,
          type: 'city' as const,
          path: `China_provs/${provinceName}/二级区划/${cityJson}`,
          province: provinceName
        });
      });
    });
    if (this.isdebug) {
      console.log('Cities loaded successfully:', this.cities);  
    }
  }

  // 搜索地理数据
  public search(query: string): GeoDataItem[] {
    if (!query || query.trim() === '') {
      return [];
    }

    const lowerQuery = query.toLowerCase().trim();
    const results: GeoDataItem[] = [];

    // 搜索省份
    this.provinces.forEach(province => {
      if (province.name.toLowerCase().includes(lowerQuery)) {
        results.push(province);
      }
    });

    // 搜索城市
    this.cities.forEach(city => {
      if (city.name.toLowerCase().includes(lowerQuery)) {
        results.push(city);
      }
    });

    // 去重并限制结果数量
    const uniqueResults = this.removeDuplicates(results);
    return uniqueResults.slice(0, 10);
  }

  // 加载地理数据
  public async loadGeoJSONData(item: GeoDataItem): Promise<GeoJSONData> {
    try {
      // 使用 apiService 中的方法获取 GeoJSON 数据
      const url = this.generateGeoDataUrl(item);
      const data = await getGeoJSONData(url);
      return data;
    } catch (error) {
      console.error(`Failed to load GeoJSON data for ${item.name}:`, error);
      // 返回模拟数据
      return {
        type: 'FeatureCollection',
        features: []
      };
    }
  }

  // 生成地理数据URL
  public generateGeoDataUrl(item: GeoDataItem): string {
    // 使用 apiService 中的方法生成 URL
    return generateGeoDataUrl(item);
  }

  // 移除重复项
  private removeDuplicates(items: GeoDataItem[]): GeoDataItem[] {
    const seen = new Set<string>();
    return items.filter(item => {
      const key = `${item.type}_${item.name}`;
      if (seen.has(key)) {
        return false;
      }
      seen.add(key);
      return true;
    });
  }

  // 获取所有省份
  public getProvinces(): GeoDataItem[] {
    return [...this.provinces];
  }

  // 获取指定省份的城市
  public getCitiesByProvince(provinceName: string): GeoDataItem[] {
    return this.cities.filter(city => city.province === provinceName);
  }

  // 根据名称获取地理数据项
  public getGeoDataItemByName(name: string): GeoDataItem | null {
    // 先搜索省份
    const province = this.provinces.find(p => p.name === name);
    if (province) {
      return province;
    }
    // 再搜索城市
    return this.cities.find(c => c.name === name) || null;
  }

  // 获取地理数据映射表
  public getGeoDataMap(): GeoDataMap | null {
    return this.geoDataMap;
  }
}

// 导出默认实例
export default GeoDataService.getInstance();