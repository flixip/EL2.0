from typing import Any

import ee
import geemap
import json
import time
from datetime import datetime
import pandas
from . import GEEFUNC_DIR


PROJECT_ID = "my-project-70786-459711"
BASIC_INFO_PATH = GEEFUNC_DIR / 'basic_info.json'

def admin():
    ee.Authenticate()
    ee.Initialize(project=PROJECT_ID)
    print("Administered successfully.")

class import_FeatureCollection:
    def __init__(self, json_file:str):
        self.geojson = self.getGeojson(json_file)
        self.name = self.geojson.get('name',str(json_file).split('\\')[-1].split('.')[0])
        self.features = None
        
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
    def __init__(self, dataset_id: str):
        self.dataset_id = dataset_id
        self.collection = ee.ImageCollection(dataset_id)
        self.ids = []
        self.selected_ids = []
        self.bounds_filtered = False

    def filter_Date(self, t0: str, t1: str) -> 'import_ImageCollection':
        '''
        专门用于 GEE 影像集的时间筛选方法
        '''
        self.collection = self.collection.filterDate(t0, t1)
        return self

    def filter_Bounds(self, geometry) -> 'import_ImageCollection':
        '''
        支持输入 ee.FeatureCollection 或 import_FeatureCollection 类对影像集进行筛选
        '''
        if isinstance(geometry, import_FeatureCollection):
            if not geometry.features:
                geometry.getFeatureCollection()
            geometry = geometry.features
        
        self.collection = self.collection.filterBounds(geometry)
        self.bounds_filtered = True
        return self

    def get_ids(self) -> 'import_ImageCollection':
        '''
        获取筛选出的影像 ID 列表，并存储在自身属性中。
        为了防止请求 ID 数量过多导致服务端超时或客户端崩溃，必须先调用 filter_Bounds。
        '''
        if not self.bounds_filtered:
            raise RuntimeError("错误：在请求影像 ID 列表 (get_ids) 之前，必须先调用 filter_Bounds 进行空间范围筛选，以确保数据量在安全范围内。")
            
        # 使用 aggregate_array 获取 ID 列表
        self.ids = self.collection.aggregate_array('system:id').getInfo()
        print(f"成功获取 {len(self.ids)} 个影像 ID。")
        return self

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

class Dataset:
    def __init__(self,dataset_info:str=BASIC_INFO_PATH):
        self.dataset_info = self._loadinfo(dataset_info)
        self.collection = None
        self.start_dt = None
        self.end_dt = None
        
    def _loadinfo(self, info_path: str) -> pandas.DataFrame:
        '''
        读取初始信息用于数据集类的初始化
        '''
        initial_info = pandas.read_json(info_path)
        # 把时间转化为可比较的时间格式
        time_format = r'%Y-%m-%d'
        
        def parse_start(x):
            try:
                return datetime.strptime(x.split('–')[0].split('T')[0], time_format)
            except:
                return datetime.min

        def parse_end(x):
            try:
                return datetime.strptime(x.split('–')[1].split('T')[0], time_format)
            except:
                return datetime.max

        initial_info['数据集开始时间'] = initial_info['数据集可用时间'].apply(parse_start)
        initial_info['数据集结束时间'] = initial_info['数据集可用时间'].apply(parse_end)
        
        # 初始化状态列，默认全为 'able'
        initial_info['status'] = 'able'
        return initial_info
    
    def filter_by_time(self, t0: str, t1: str = '-') -> 'Dataset':
        '''
        筛选出在时间范围内的数据集。用户输入格式为 YYYY-MM-DD
        修改自身 status 列而返回 self，支持链式调用
        '''
        time_format = r'%Y-%m-%d'
        self.start_dt = datetime.strptime(t0, time_format)
        if t1 == '-':
            self.end_dt = datetime.now()
        else:
            self.end_dt = datetime.strptime(t1, time_format)
            
        # 仅对当前为 'able' 的行进行筛选
        mask = (self.dataset_info['status'] == 'able') & \
               ~((self.dataset_info['数据集开始时间'] <= self.start_dt) & 
                 (self.dataset_info['数据集结束时间'] >= self.end_dt))
        
        self.dataset_info.loc[mask, 'status'] = 'disable'
        return self

    def filter_by_name(self, keyword: str) -> 'Dataset':
        '''
        实现按数据集名称筛选的功能，输入名称如 landsat, sentinel 等
        修改自身 status 列而返回 self，支持链式调用
        '''
        # 仅对当前为 'able' 的行进行筛选
        mask = (self.dataset_info['status'] == 'able') & \
               ~(self.dataset_info['name'].str.contains(keyword, case=False, na=False))
        
        self.dataset_info.loc[mask, 'status'] = 'disable'
        return self

    def filter_by_frequency(self, keyword: str) -> 'Dataset':
        '''
        实现按频率筛选的功能。如果没有值或不包含关键字，则设为 disable
        返回 self 支持链式调用
        '''
        # 1. 处理空值情况：如果“频率”列为空，直接设为 disable
        self.dataset_info.loc[
            (self.dataset_info['status'] == 'able') & 
            (self.dataset_info['频率'].isna() | (self.dataset_info['频率'] == '')), 
            'status'
        ] = 'disable'

        # 2. 模糊匹配关键字
        mask = (self.dataset_info['status'] == 'able') & \
               ~(self.dataset_info['频率'].str.contains(keyword, case=False, na=False))
        
        self.dataset_info.loc[mask, 'status'] = 'disable'
        return self

    def import_ImageCollection(self, dataset_id: str, auto_filter_time=True) -> 'import_ImageCollection':
        '''
        在 Dataset 类中处理时间校验逻辑，并实例化 import_ImageCollection
        '''
        # 1. 自动校验时间范围并警告
        if self.start_dt and self.end_dt:
            match = self.dataset_info[self.dataset_info['id'] == dataset_id]
            if not match.empty:
                row = match.iloc[0]
                if not (row['数据集开始时间'] <= self.start_dt and row['数据集结束时间'] >= self.end_dt):
                    print(f"警告：数据集 ID '{dataset_id}' 的可用时间 ({row['数据集可用时间']}) 无法完全覆盖您筛选的时间范围 ({self.start_dt.date()} 至 {self.end_dt.date()})，结果可能为空。")
            else:
                print(f"警告：未在元数据中找到 ID 为 '{dataset_id}' 的数据集，请确认 ID 是否正确。")
        
        # 2. 实例化独立的 import_ImageCollection 类
        img_coll_instance = import_ImageCollection(dataset_id)
        
        # 3. 如果开启了自动过滤且有时间信息，则调用实例的方法进行筛选
        if auto_filter_time and self.start_dt and self.end_dt:
            img_coll_instance.filter_Date(
                self.start_dt.strftime('%Y-%m-%d'), 
                self.end_dt.strftime('%Y-%m-%d')
            )
            
        return img_coll_instance

    def getID(self, index: int) -> str:
        '''
        获取当前筛选出的数据集 ID
        '''
        able_data = self.dataset_info[self.dataset_info['status'] == 'able']
        if 0 <= index < len(able_data):
            return str(able_data.iloc[index]['id'])
        else:
            raise IndexError(f"Index {index} out of range for current able datasets (total: {len(able_data)})")

    def showinfo(self):
        able_data = self.dataset_info[self.dataset_info['status'] == 'able']
        print(f"当前筛选出的有效数据集数量: {len(able_data)} / 总数: {len(self.dataset_info)}")
        if not able_data.empty:
            print("有效数据集详情:")
            print(able_data[['id', 'name', '频率', '数据集可用时间']])
        else:
            print("未找到匹配的数据集。")
        return self
        
 
if __name__ == '__main__':
    # 示例链式调用与状态管理验证
    dataset = Dataset()
    
    # 1. 链式筛选：Sentinel 数据，且频率为 5 天
    print("--- 筛选 Sentinel + 5天频率 ---")
    dataset.filter_by_name('sentinel')\
           .filter_by_frequency('5 天')\
           .showinfo()
    
    # 2. 导入影像集并链式处理
    print("\n--- 导入影像集并链式处理 ---")
    # 筛选时间
    dataset.filter_by_time('2020-01-01', '2020-02-01')
    
    # 导入影像集（触发自动时间筛选）
    img_coll = dataset.import_ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    
    # 模拟 roi (仅用于演示 filter_Bounds 逻辑)
    # roi = ee.Geometry.Point([114.3, 34.8]) 
    
    try:
        # 演示报错：未调用 filter_Bounds 直接尝试获取 ID
        print("尝试在未筛选 Bounds 时获取 ID 列表...")
        # img_coll.get_ids() # 这里会触发 RuntimeError
        
        # 正确流程示例：
        # 1. 必须先 filter_Bounds (核心前置条件)
        # 2. 然后 get_ids() 获取服务端数据
        # 3. 然后 [0:2] 选择特定影像
        # 4. 然后 addtoMap(Map) 加载到地图
        # Map = img_coll.filter_Bounds(roi).get_ids()[0:2].addtoMap(Map)
        print("语法示例：img_coll.filter_Bounds(roi).get_ids()[0:2].addtoMap(Map)")
    except Exception as e:
        print(f"捕获到预期错误: {e}")
