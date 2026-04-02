'''
接收唯一参数cid,就可以确定唯一数据集,
cid确实有某种特殊格式，但是考虑通过筛选拿到cid或者直接输入cid来确定，而非自行构造。

本路由模块控制由唯一cid确定的数据集的行为：
1. 接收筛选参数筛选具体影像列表
2. 返回筛选结果-> 影像id列表、影像集html (info可选)

定义影像筛选参数形状
{
    "start_date": "2023-01-01",  # 开始日期
    "end_date": "2023-12-31",    # 结束日期
    "bounds": ["湖北省", "武汉市"],  # 地理边界（字符串数组）先省后市，接收el表单的字符串数组
    "cloud": 20  # 云量阈值
}

定义返回参数形状

{
    "status": "success",
    "images": [],
    "html": ""
}

'''

from flask import Blueprint, jsonify, request

bp = Blueprint('imgcAct', __name__)

@bp.route('/imgcAct/<path:cid>/filter', methods=['POST'])
def filter_images(cid):
    '''
    筛选影像列表
    参数:    
        cid: 数据集ID
        body: 筛选参数
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            bounds: 地理边界（字符串数组，如 ["湖北省", "武汉市"]）
            cloud: 云量阈值 (0-100)
    '''
    # 获取请求体参数
    data = request.json
    
    # 提取筛选参数
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    bounds = data.get('bounds')
    cloud = data.get('cloud', 100)
    
    # 验证必要参数
    if not all([start_date, end_date, bounds]):
        return jsonify({
            'status': 'error',
            'message': 'Missing required parameters'
        }), 400
    
    # 验证bounds参数类型
    if not isinstance(bounds, list):
        return jsonify({
            'status': 'error',
            'message': 'bounds must be a list of strings'
        }), 400
    
    # 验证cloud参数范围
    if not (0 <= cloud <= 100):
        return jsonify({
            'status': 'error',
            'message': 'cloud must be between 0 and 100'
        }), 400
    
    try:
        # 使用 AwesEE 包进行筛选
        from geeservice.AwesEE import FImageCollection
        
        # 创建影像集并进行筛选
        collection = FImageCollection(cid)
        collection.filter(
            start_date=start_date,
            end_date=end_date,
            bounds=bounds,
            cloud=cloud
        ).scaleAndOffset()
        
        # 获取影像 ID 列表
        image_ids = collection.get_image_ids()
        
        # 获取影像集的 HTML 表示
        html_representation = collection._repr_html_()
        
        # 构造简化的响应格式
        images = [{'id': id} for id in image_ids]
        
        return jsonify({
            'status': 'success',
            'images': images,
            'html': html_representation
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

from geeservice.utils import fliter_img_id,get_filtered_info

@bp.route('/geefunc/filter', methods=['POST'])
def get_img_ids():
    '''
    获取数据集筛选结果
    参数:    
        cid: 数据集ID
        filter_params: 筛选参数
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            bounds: 地理边界（字符串数组，如 ["湖北省", "武汉市"]）
            cloud: 云量阈值 (0-100)
            **kwargs: 其他筛选参数，后续考虑增加功能
    '''
    args = request.json
    cid = args.get('cid')
    filter_params = args.get('filter_params')
    ids = fliter_img_id(cid,**filter_params)
    info = get_filtered_info(cid,info_type='gethtml')
    
    return jsonify({
        'status': 'success',
        'ids': ids,
        'info':{
            'type':"html",
            'content':info
        },
        
    })