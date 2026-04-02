import axios from 'axios';
import config from '@/config';

const mapUrl = config.API_GEE_FUNC_MAP_URL
const filterUrl = config.API_GEE_FUNC_FILTER_URL


export const getMapUrl = async (
    cid: string[] | string, 
    vis_params: any): Promise<any> => {
        console.log('开始获取地图URL:', cid, vis_params,mapUrl)
        const response = await axios.post(mapUrl, { cid, vis_params })
        return response.data    
    }

interface getFilterImgcResponse {
    /** 状态 */
    status: string;
    /** 筛选影像id */
    ids: string[];
    /** 筛选信息 */
    info: any;
}

export const getFilterImg = async (
    input:{
        cid: string, 
        filter_params: any
    }
    
): Promise<getFilterImgcResponse> => {

        const {cid,filter_params} = input 

        console.log('开始获取筛选结果:', cid, filter_params,filterUrl)
        const response = await axios.post(filterUrl, { cid, filter_params })
        console.log('筛选结果:', response.data)
        return response.data    
    }


const test_params = {
    cid: 'COPERNICUS/S2_SR_HARMONIZED',
    filter_params: {
        start_date: '2023-01-01',
        end_date: '2023-01-31',
        bounds: ['湖北省', '武汉市'],
        cloud: 50,
    }

}


declare global {
    interface Window {
        geefuncApi: {
            getMapUrl: (cid: string[] | string, vis_params: any) => Promise<any>;
            getFilterImg: (cid: string, filter_params: any) => Promise<any>;
        }
        testParams: {testfilter_params: typeof test_params}
    }
}

window.geefuncApi = {
    getMapUrl,
    getFilterImg,
}

window.testParams = {
    testfilter_params: test_params
}
