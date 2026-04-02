import ee
import geemap
import json
from pathlib import Path
import eemont
from typing import Dict

PROJECT_PATH = Path(__file__).parent.parent.parent
SRC_PATH = PROJECT_PATH / 'dataloader' / 'admini_division_src'

PROJECT_ID = "my-project-70786-459711"



def admin():
    ee.Authenticate()
    ee.Initialize(project=PROJECT_ID)
    print(f"\033[36m == \"{PROJECT_ID}\" Administered successfully. == \033[0m")

class import_FeatureCollection:
    def __init__(self, bounds:str | list[str,]):
        '''
        这个featurecollection类主要是为了边距筛选而设计的  
        bounds: 可以是一个字符串，也可以是一个列表  
        是字符串时需要填文件路径，如果是列表就填[province,city]
        '''
        self.geojson = self.getGeojson(self._bounds_check(bounds))
        self.name = self.geojson.get('name',str(bounds).split('\\')[-1].split('.')[0])
        self.features = None
    
    
    def _bounds_check(self,bounds:str | list[str,]) -> Path:
        "输入检查"
        if isinstance(bounds, str) and Path(bounds).exists():
            return Path(bounds)
        elif isinstance(bounds, list):
            return self.get_bounds_json_path(bounds)
        else:
            raise ValueError("bounds must be a string or a list of strings")
    
    def get_bounds_json_path(self,bounds_name:list[str]) -> Path | None:
        '''
        认为必须输入一个列表，如果为省份，则为省名  
        如果为市名，则列表第一个为省名，第二个为城市名  
        因此如果列表长为1，则为省份，长为2，则为城市
        '''
        if len(bounds_name) == 1:
            return SRC_PATH / f'ChinaGeodata/China_provs/{bounds_name[0]}/{bounds_name[0]}.json'
        elif len(bounds_name) == 2:
            return SRC_PATH / f'ChinaGeodata/China_provs/{bounds_name[0]}/二级区划/{bounds_name[1]}.json'
        else:
            return None
    
    def getGeojson(self, json_file:str) -> dict:
        '''
        读取本地json文件，返回解析后的json字典
        '''
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if data.get('type') == 'FeatureCollection':
            return data
        else:
            raise ValueError("JSON file does not contain a FeatureCollection")
    
    def addtoMap(self,map:geemap.Map) -> geemap.Map:
        """
        推荐的能加到地图的貌似也就feature/featurecollection/和image，
        但是Image需要设置可视化参数，选取波段，拉伸值等，所以还是只接收这两个
        """
        if not self.features:
            self.getFeatureCollection()
        map.addLayer(self.features, {},self.name)
        map.centerObject(self.features, 10)
        return map
    
    def getFeatureCollection(self):
        self.features = ee.FeatureCollection(self.geojson)
        return self
    
    def getFeature(self,index):
        try:
           feature = self.geojson.get('features')[index]
        except :
            raise IndexError(f"Index {index} out of range.")
        self.features = ee.Feature(feature)
        self.name = feature.get('properties').get('name','不知名图层')
        return self

class import_ImageCollection:
    # 制作单例组模式，便于复用
    _instances: Dict[str,'import_ImageCollection'] = {}
    
    def __init__(self, dataset_id: str):
        self.dataset_id = dataset_id
        self.collection = ee.ImageCollection(dataset_id)
        self.ids = []
        self.selected_ids = []
        self.bounds_filtered = False
    
    @classmethod
    def get_instance(cls, cid):
        if cid not in cls._instances:
            cls._instances[cid] = import_ImageCollection(cid)
        return cls._instances[cid]
        
        

    def filter_Date(self, t0: str, t1: str) -> 'import_ImageCollection':
        '''
        专门用于 GEE 影像集的时间筛选方法
        '''
        self.collection = self.collection.filterDate(t0, t1)
        return self

    def filter_Bounds(self, geometry) -> 'import_ImageCollection':
        '''
        支持输入 ee.FeatureCollection、import_FeatureCollection 类或 [province, city] 格式的地理边界对影像集进行筛选
        '''
        # 处理 [province, city] 格式的地理边界
        if isinstance(geometry, list) and len(geometry) == 2:
            featurecollection = import_FeatureCollection(geometry)
            featurecollection.getFeatureCollection()
            geometry = featurecollection.features
        # 处理 import_FeatureCollection 类型
        elif isinstance(geometry, import_FeatureCollection):
            if not geometry.features:
                geometry.getFeatureCollection()
            geometry = geometry.features
        
        self.collection = self.collection.filterBounds(geometry)
        self.bounds_filtered = True
        return self

    def get_ids(self) -> list:
        '''
        获取筛选出的影像 ID 列表，并存储在自身属性中。
        为了防止请求 ID 数量过多导致服务端超时或客户端崩溃，必须先调用 filter_Bounds。
        '''
        if not self.bounds_filtered:
            raise RuntimeError("错误：在请求影像 ID 列表 (get_ids) 之前，必须先调用 filter_Bounds 进行空间范围筛选，以确保数据量在安全范围内。")
            
        # 使用 aggregate_array 获取 ID 列表
        self.ids = self.collection.aggregate_array('system:id').getInfo()
        print(f"成功获取 {len(self.ids)} 个影像 ID。")
        return self.ids

    def __getitem__(self, index) -> 'import_ImageCollection':
        '''
        支持像列表切片和根据索引取值一样选择影像 ID
        '''
        if not self.ids:
            print("提示：当前 ID 列表为空，请先调用 get_ids() 获取 ID。")
            return self
            
        if isinstance(index, slice):
            self.selected_ids = self.ids[index]
        else:
            self.selected_ids = [self.ids[index]]
        return self

    def addtoMap(self, map_obj: geemap.Map) -> geemap.Map:
        '''
        根据自身存储的 selected_ids，将其转化为 ee.Image 并全部加载到 map 上。
        返回传入的 map 对象。
        '''
        if not self.selected_ids:
            print("提示：没有选中的影像可供加载。请确保已依次调用 get_ids() 和索引/切片操作。")
            return map_obj
            
        for img_id in self.selected_ids:
            img = ee.Image(img_id)
            # 使用 ID 的末尾作为图层名称
            layer_name = img_id.split('/')[-1]
            map_obj.addLayer(img, {}, layer_name)
            
        print(f"已成功将 {len(self.selected_ids)} 个影像加载到地图上。")
        return map_obj
    
    def scaleAndOffset(self):
        '''
        应用scaleAndOffset()方法到影像集
        '''
        self.collection = self.collection.scaleAndOffset()
        return self
    
    def _repr_html_(self):
        '''
        返回HTML表示，使得Jupyter Notebook能够显示import_ImageCollection实例
        利用内部ee.ImageCollection对象自动生成的HTML表示
        '''
        return self.collection._repr_html_()

    def get_info(self):
        return self.collection.getInfo()
    
class import_Image:
    def __init__(self,cid):
        self.image = ee.Image(cid)
        self.visparams = {}
    def set_visparams(self,visparams) -> 'import_Image':
        self.visparams = visparams
        return self
        
    def get_map_url(self) -> str:
        if not self.visparams:
            raise ValueError("错误：请先设置可视化参数 (set_visparams) 后再获取地图 URL。")
        return self.image.getMapId(self.visparams)['tile_fetcher'].url_format

    def scaleAndOffset(self):
        self.image = self.image.scaleAndOffset()
        return self


def get_map_urls(img_ids: str | list ,vis_params: dict) -> str:
   if isinstance(img_ids, str):
       return ee.Image(img_ids)\
           .scaleAndOffset()\
           .getMapId(vis_params)['tile_fetcher'].url_format
   elif isinstance(img_ids, list):
       return [ee.Image(img_id)\
           .scaleAndOffset()\
           .getMapId(vis_params)['tile_fetcher'].url_format 
           for img_id in img_ids]

  
if __name__ == '__main__':
    pass