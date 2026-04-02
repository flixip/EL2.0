from flask import Flask,request
from .geeFunc.baseTool import admin,import_FeatureCollection,import_ImageCollection,import_Image
import ee
from pathlib import Path
import sys
import uuid

project_root = str(Path(__file__).parent.parent)
# 把项目根目录加入sys.path
sys.path.append(project_root)

app = Flask(__name__)
# 一次鉴权
admin()

cache = {}  # 缓存数据集,存的应该都是实例
# 用id创建为唯一对象处理各种需求，因为数据是一定的创建多个对象对应的也是同一个数据集，对数据集的操作都在这个对象上进行
cache_type = {}  # 缓存数据集的类型,
# 因为falsk的数据传递的时候不能传递对象，所以专门弄一个cache_type来缓存数据集的类型,请求的时候来返回存储情况

def save_to_cache(key,value):
    cache[key] = value
    cache_type[key] = str(type(value))

@app.route('/check_cache')
def check_cache():
    return {'cache': cache_type}

@app.route('/operate',methods=['POST'])
def operate_cache():
    """
    该函数的目的是从cache中拿到对象然后操作它
    """
    uuid = request.json['uuid']
    operation = request.json['operation']
    params = request.json.get('params',{})
    
    obj = cache[uuid]
    func = getattr(obj,operation)
    result = func(**params)
    
    # 更新缓存中的对象，确保操作后的实例被保存
    if isinstance(result, (import_ImageCollection, ee.Image, import_Image)):
        save_to_cache(uuid, result)
        # 对于返回self的方法，只返回成功状态
        return {
            'status': 'success'
        }
    else:
        # 对于其他返回值，返回结果
        return {
            'status': 'success',
            'result': result
        }

@app.route('/filter/<uuid>',methods=['POST'])
def filter(uuid):
    """
    一次性筛选影像集
    参数:
        cid: 影像集ID
        start_date: 开始日期
        end_date: 结束日期
        bounds: 地理边界，格式为 [province, city]
        cloud: 云量阈值
    """
    cid = request.json['cid']
    start_date = request.json['start_date']
    end_date = request.json['end_date']
    bounds = request.json.get('bounds', None)
    cloud = request.json.get('cloud', 100)
        
    # 创建 import_ImageCollection 实例
    img_collection = import_ImageCollection(cid)
    
    # 筛选日期
    img_collection.filter_Date(start_date, end_date)
    
    # 筛选云量
    if cloud < 100:
        img_collection.collection = img_collection.collection.filter(ee.Filter.lt('CLOUD_COVER', cloud))
    
    # 筛选边界
    bounds_filtered = False
    if bounds:
        img_collection.filter_Bounds(bounds)
        bounds_filtered = True
    
    # 计算筛选后的影像数量
    count = img_collection.collection.size().getInfo()
    
    # 缓存筛选后的结果，直接覆盖原缓存
    save_to_cache(uuid, img_collection)
    
    return {
        'status': 'success',
        'count': count,
        'bounds_filtered': bounds_filtered
    }

@app.route('/imagecollection/<uuid>',methods=['POST'])
def get_imagecollection(uuid):
    cid = request.json['cid']

    # 创建 import_ImageCollection 实例
    collection = import_ImageCollection(cid)
    
    # 使用UUID作为缓存键
    save_to_cache(uuid, collection)
    return {
        'status': 'success',
        'uuid': uuid
    }

@app.route('/image/<uuid>',methods=['POST'])
def get_image(uuid):
    cid = request.json['cid']
    save_to_cache(uuid,import_Image(cid))
    return {
        'status': 'success'
    }

@app.route('/featurecollection',methods=['POST'])
def get_featurecollection():
    """接收geojson 的name：['province','city'],拿到json_path，然后构建import_FeatureCollection对象,这个考虑用name来作为key"""
    name = request.json['name']
    featurecollection = import_FeatureCollection(name)
    save_to_cache(''.join(name),featurecollection)
    return {
        'status': 'success'
    }

@app.route('/get_map_url',methods=['POST'])
def get_map_url():
    """
    获取影像的地图URL
    参数:
        image_id: 影像ID（单个）
        image_ids: 影像ID列表（多个）
        vis_params: 可视化参数
    """
    image_id = request.json.get('image_id')
    image_ids = request.json.get('image_ids')
    vis_params = request.json['vis_params']
    
    try:
        from geeFunc.baseTool import get_map_url as generate_map_url
        
        # 处理单个影像ID
        if image_id:
            url = generate_map_url(image_id, vis_params)
            return {
                'status': 'success',
                'result': url
            }
        # 处理多个影像ID
        elif image_ids:
            urls = []
            for img_id in image_ids:
                try:
                    url = generate_map_url(img_id, vis_params)
                    urls.append(url)
                except Exception as e:
                    urls.append(None)
            return {
                'status': 'success',
                'result': urls
            }
        else:
            return {
                'status': 'error',
                'message': 'No image ID provided'
            }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }


if __name__ == '__main__':
    app.run(debug=True,port=5001)
