from .geedataparser import DataParser
from pydantic import BaseModel, Field


# 引入数据集实例，后续不引入，而是引入方法
parser = DataParser()

# 抽象筛选结果为数据集id列表，即任何筛选结果第一返回信息为最简索引

class DatasetFilterParams(BaseModel):
    """数据集筛选参数
    name: 数据集名称列表或者单个名称，支持模糊匹配  
    start_date: 开始日期，格式YYYY-MM-DD  
    end_date: 结束日期，格式YYYY-MM-DD  
    producer: 数据生产者列表  
    pixel_size_comparison: 像素大小比较运算符，默认小于等于  
    pixel_size_num: 像素大小  
    tags: 标签列表，支持模糊匹配  
    
    """
    name: list[str] | str | None = Field(default=None,description="数据集名称列表或者单个名称，支持模糊匹配，建议分词搜索比如['landsat8']建议拆成['landsat','8']避免搜不到")
    start_date: str | None = Field(default=None,description="开始日期，格式YYYY-MM-DD")
    end_date: str | None = Field(default=None,description="结束日期，格式YYYY-MM-DD")
    producer: list[str] | str | None = Field(default=None,description="数据生产者列表")
    pixel_size_comparison: str | None = Field(default='lt',description="像素大小比较运算符，默认小于等于，默认lt")
    pixel_size_num: float | None = Field(default=None,description="像素大小")
    tags: list[str] | str | None = Field(default=None,description="标签列表，支持模糊匹配")

def get_dataset_fields() -> list[str]:
    """获取数据集的所有字段"""
    return parser.main_df.columns.tolist()

def filter_dataset(params:DatasetFilterParams | dict | None = None,**kwargs) -> list[str]:
    """筛选符合条件的影像数据集，返回ID列表"""
    # 每次筛选前先重置筛选表，避免筛选累计
    parser.reset_filter()
    if isinstance(params, dict):
        params = DatasetFilterParams(**params)
        parser.filter(**params.model_dump())
    elif isinstance(params, DatasetFilterParams):
        parser.filter(**params.model_dump())
    elif params is None:
        parser.filter(**kwargs)
    return parser.get_filtered_ids()

def get_detail(cids:str | list[str],field:list[str] | None = None,orient:str = 'records') -> list[dict]:
    """依据数据集ID列表获取数据集的详细信息
    :param cids: 单个cid或cid列表（支持字符串或列表）  
    :param field: 要返回的字段列表（默认返回所有字段）  
    :return: 包含查询结果的列表，每个元素为一个字典（包含查询字段）  
    
    tips：
    - get_result中已经包含field列表的空值检查，无需再进行
    """
    # 错误字段容差
    result_df = parser.get_by_cid(cids).get_result(field)
    valid_field = result_df.columns.tolist() + ['start_date','end_date','pixel_size']
    error_fields = [f for f in field if f not in valid_field]
    result_dict = result_df.to_dict(orient=orient)
    if isinstance(result_dict, list):
        result_dict.append({'error_fields': error_fields})
    if isinstance(result_dict, dict):
        result_dict['error_fields'] = error_fields
    return result_dict

def get_band_info(cid:str) -> list[str]:
    return parser.get_bands_by_cid(cid)['Name'].tolist()

if __name__ == '__main__':
   print(get_band_info('COPERNICUS/S2_SR_HARMONIZED'))
