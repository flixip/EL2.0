'''
接收唯一参数imgid,就可以确定唯一影像,
imgid确实有某种特殊格式，但是考虑通过筛选拿到imgid或者直接输入imgid来确定，而非自行构造。

本路由模块控制由唯一imgid确定的影像的行为：
1. 接收可视化参数，返回影像地图URL

定义可视化参数形状
{
    "bands": ["B4", "B3", "B2"],  # 波段组合
    "min": 0,             # 最小值
    "max": 0.3,    # 最大值
    "gamma": 1            # 伽马校正
}

定义返回参数形状

{
    "status": "success",
    "map_url": "",
    "info": {}（可选）
}

'''

from flask import Blueprint, jsonify, request

bp = Blueprint('imgAct', __name__)

@bp.route('/imgAct/<path:img_id>/mapurl', methods=['POST'])
def get_image_map_url(img_id):
    '''
    获取影像地图URL
    参数:    
        img_id: 影像ID
        body: 可视化参数
            bands: 波段组合（字符串数组）
            min: 最小值（数值或数值数组）
            max: 最大值（数值或数值数组）
            gamma: 伽马校正（数值或数值数组，可选）
    '''
    # 获取请求体参数
    data = request.json
    
    # 提取可视化参数
    vis_params = data.get('vis_params', data)
    
    try:
        # 使用 AwesEE 包获取地图URL
        from geeservice.AwesEE import get_map_urls
        result = get_map_urls(img_id, vis_params)
        
        return jsonify({
            'status': 'success',
            'map_url': result,
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

from geeservice.utils import get_map_urls

@bp.route('/geefunc/mapurl', methods=['POST'])    
def get_map_url():
    '''
    获取数据集地图URL
    参数:    
        cid: 数据集ID
        body: 可视化参数
            bands: 波段组合（字符串数组）
            min: 最小值（数值或数值数组）
            max: 最大值（数值或数值数组）
            gamma: 伽马校正（数值或数值数组，可选）
    '''
    args = request.json
    cids = args.get('cid', [])
    vis_params = args.get('vis_params', {})
    try:
        result = get_map_urls(cids, vis_params)
        return jsonify({
            'status': 'success',
            'map_url': result,
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })
