export interface SearchData {
    /** 数据集唯一标识符 */
    cid: string;
    /** 数据集名称 */
    name: string;
    /** 像素分辨率（单位：米） */
    pixel_size_num: number | null;
    /** 数据集开始日期，ISO 8601 格式 */
    date_start: string;
    /** 数据集结束日期，ISO 8601 格式或 '至今' */
    date_end: string | '至今';
}

export interface FilterImagesParams {
    /** 开始日期 (YYYY-MM-DD) */
    start_date: string;
    /** 结束日期 (YYYY-MM-DD) */
    end_date: string;
    /** 地理边界（字符串数组，如 ["湖北省", "武汉市"]） */
    bounds?: string[];
    /** 云量阈值 (0-100) */
    cloud?: number;
}

export interface ImageData {
    /** 影像ID */
    id: string;
}

export interface FilterImagesResponse {
    /** 状态 */
    status: string;
    /** 影像列表 */
    images: ImageData[];
    /** 影像集HTML表示 */
    html: string;
}

export interface VisParams {
    /** 波段组合（字符串数组） */
    bands: string[];
    /** 最小值（数值或数值数组） */
    min: number | number[];
    /** 最大值（数值或数值数组） */
    max: number | number[];
    /** 伽马校正（数值或数值数组，可选） */
    gamma?: number | number[];
}

export interface GetImageMapUrlResponse {
    /** 状态 */
    status: string;
    /** 地图URL */
    map_url: string;
}


export default {
    // step1 填写的表单数据 本地localstorage的key
    STEP1_FORM_DATA_KEY: 'imgGetStep1',
    // step2 选择区域的表单数据 本地localstorage的key
    STEP2_FORM_DATA_KEY: 'imgGetStep2',
    // 选中的数据集 本地localstorage的key
    SELECTED_DATASET_KEY: 'selectedDataset',
    // 搜索结果 本地localstorage的key
    SEARCH_RESULT_KEY: 'searchResult',
    // 筛选结果 本地localstorage的key
    FILTER_RESULT_KEY: 'filterResult',
    // 可视化参数 本地localstorage的key
    VISUAL_PARAMS_KEY: 'imgGetVisualParams',
    // 后端ImgGet接口的接口
    API_IMG_GET: 'api/imgGet',
    // 地理数据 API 路径
    API_GEO_URL: 'api/geodata/',
    // 地理数据映射表 API 路径
    API_GEODATA_MAP_URL: 'api/geodataMap',
    // 数据集搜索 API 路径
    API_DATASETS_SEARCH: 'api/geeinfo/search',
    // 数据集详情 API 路径
    API_DATASETS_DETAIL: 'api/geeinfo/detail/bands/name/',
    // 数据集筛选 API 路径
    API_DATASETS_FILTER: 'api/datasets/',
    // 获取地图 URL API 路径
    API_GET_MAP_URL: 'api/get_map_url',
    // 影像集筛选 API 路径
    API_IMG_ACT_FILTER: 'api/imgcAct/',
    // 影像地图 URL API 路径
    API_IMG_MAP_URL: 'api/imgAct/',
    // API 路径映射表
    pathmap: {
        all_prov_path: 'api/geodata/China_provs_all.geojson',
    },
    // 后端AIChat接口的接口
    API_AI_CHAT: 'api/aiChat',
    // 后端GEEFUNC接口的接口
    API_GEE_FUNC_MAP_URL: 'api/geefunc/mapurl',
    API_GEE_FUNC_FILTER_URL: 'api/geefunc/filter',
}


