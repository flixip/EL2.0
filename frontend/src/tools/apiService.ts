import axios from "axios";
import config, { type FilterImagesParams, type FilterImagesResponse, type VisParams, type GetImageMapUrlResponse } from '@/config';
import { getSelectedDataset, getStep2FormData, getVisualParams } from './storageManager';
import { searchDatasets, getBandNames } from '@A/geoinfoApi';

export const filterImagesFromStorage = async () => {
  console.log('开始从本地存储获取数据并发送到后端进行筛选');
  const selectedDataset = getSelectedDataset();
  const step2Data = getStep2FormData();

  if (!selectedDataset || !step2Data) {
    console.error('本地存储中未找到数据');
    throw new Error('No data found in localStorage');
  }

  const { start_date, end_date, bounds, cloud } = step2Data;
  console.log('开始调用筛选接口');
  const result = await filterImages(selectedDataset.cid, {
    start_date,
    end_date,
    bounds,
    cloud
  });
  console.log('筛选结果:', result);
  console.log('从本地存储获取数据并发送到后端进行筛选完成');
  return result;
};

export const filterImages = async (datasetId: string, params: {
  start_date: string;
  end_date: string;
  bounds?: string[];
  cloud?: number;
}) => {
  console.log('开始筛选影像:', datasetId, params);
  try {
    const response = await axios.post(`${config.API_DATASETS_FILTER}${encodeURIComponent(datasetId)}/filter`, params);
    console.log('影像筛选结果:', response.data);
    return response.data;
  } catch (error) {
    console.error('Failed to filter images:', error);
    throw error;
  }
};

export const getMapUrls = async (imageIds: string | string[], visParams: any) => {
  console.log('开始获取影像地图URL:', imageIds, visParams);
  try {
    const response = await axios.post(config.API_GET_MAP_URL, {
      image_id: typeof imageIds === 'string' ? imageIds : undefined,
      image_ids: typeof imageIds === 'string' ? undefined : imageIds,
      vis_params: visParams
    });
    console.log('地图URL获取结果:', response.data);
    return response.data;
  } catch (error) {
    console.error('Failed to get map urls:', error);
    throw error;
  }
};

export const getMapUrlsFromStorage = async () => {
  console.log('开始从本地获取visparams和imageIds并发送到后端获取地图URL');
  try {
    const visParams = getVisualParams();
    if (!visParams) {
      console.error('本地存储中未找到可视化参数');
      throw new Error('No visualization parameters found in localStorage');
    }

    const basic = visParams.basic;
    if (!basic) {
      console.error('本地存储中未找到基本可视化参数');
      throw new Error('No basic visualization parameters found in localStorage');
    }

    const { selectedImages, bands, max, min } = basic;
    if (!selectedImages || selectedImages.length === 0) {
      console.error('本地存储中未找到选中的影像');
      throw new Error('No selected images found in localStorage');
    }

    const simplifiedVisParams = { bands, max, min };

    const response = await axios.post(config.API_GET_MAP_URL, {
      image_ids: selectedImages,
      vis_params: simplifiedVisParams
    });
    console.log('地图URL获取结果:', response.data);
    return response.data;
  } catch (error) {
    console.error('Failed to get map urls from storage:', error);
    throw error;
  }
};

export const filterImagesByCid = async (cid: string, params: FilterImagesParams): Promise<FilterImagesResponse> => {
  console.log('开始筛选影像集:', cid, params);
  try {
    const response = await axios.post(`${config.API_IMG_ACT_FILTER}${encodeURIComponent(cid)}/filter`, params);
    console.log('影像集筛选结果:', response.data);
    return response.data;
  } catch (error) {
    console.error('Failed to filter images by cid:', error);
    throw error;
  }
};

export const getImageMapUrl = async (imgId: string, visParams: VisParams): Promise<GetImageMapUrlResponse> => {
  console.log('开始获取影像地图URL:', imgId, visParams);
  try {
    const response = await axios.post(`${config.API_IMG_MAP_URL}${encodeURIComponent(imgId)}/mapurl`, visParams);
    console.log('影像地图URL获取结果:', response.data);
    return response.data;
  } catch (error) {
    console.error('Failed to get image map url:', error);
    throw error;
  }
};

declare global {
  interface Window {
    searchDatasets: (params: any) => Promise<any>;
    getDatasetDetail: (datasetId: string) => Promise<any>;
    filterImages: (datasetId: string, params: any) => Promise<any>;
    filterImagesFromStorage: () => Promise<any>;
    getMapUrls: (imageIds: string | string[], visParams: any) => Promise<any>;
    getMapUrlsFromStorage: () => Promise<any>;
    filterImagesByCid: (cid: string, params: any) => Promise<any>;
    getImageMapUrl: (imgId: string, visParams: any) => Promise<any>;
  }
}

window.searchDatasets = searchDatasets;
window.getDatasetDetail = getBandNames;
window.filterImages = filterImages;
window.filterImagesFromStorage = filterImagesFromStorage;
window.getMapUrls = getMapUrls;
window.getMapUrlsFromStorage = getMapUrlsFromStorage;
window.filterImagesByCid = filterImagesByCid;
window.getImageMapUrl = getImageMapUrl;
