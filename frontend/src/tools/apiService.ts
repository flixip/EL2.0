import axios from "axios";

// 地理数据 API 路径
const API_GEO_URL = 'api/geodata/';

// 地理数据映射表 API 路径
const API_GEODATA_MAP_URL = 'api/geodataMap';

export const pathmap = {
    all_prov_path: API_GEO_URL + 'China_provs_all.geojson',
};

// 获取 GeoJSON 数据
export const getGeojson = async (path: string) => {
    try {
        const response = await axios.get(path);
        return response.data;
    } catch (error) {
        console.error('Error loading GeoJSON:', error);
        return null;
    }
};

// 获取地理数据映射表
export const getGeoDataMap = async () => {
    try {
        const response = await axios.get(API_GEODATA_MAP_URL);
        return response.data;
    } catch (error) {
        console.error('Failed to load geo data map:', error);
        throw error;
    }
};

// 获取指定路径的 GeoJSON 数据
export const getGeoJSONData = async (path: string) => {
    try {
        const response = await axios.get(path);
        return response.data;
    } catch (error) {
        console.error('Failed to load GeoJSON data:', error);
        throw error;
    }
};

// 生成地理数据 URL
export const generateGeoDataUrl = (item: any) => {
    return API_GEO_URL + item.path;
};