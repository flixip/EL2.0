from ..rpc import exec_code,eval_code
from pydantic import BaseModel,Field,ValidationError
from typing import List,Dict,Any,Optional,Union

class ParamsFilterImgId(BaseModel):
    """筛选图像id参数（保留，仅适配新装饰器）"""
    cid: str = Field(description="目标图像数据集id", example="LANDSAT/LT05/C02/T1_L2")
    bounds: List[str] = Field(description="[省份名,城市名(可选)]", example=["湖北省", "武汉市"])
    start_date: str = Field(description="开始日期yyyy-MM-dd", example="2008-01-01")
    end_date: str = Field(description="结束日期yyyy-MM-dd", example="2009-12-31")


def fliter_img_id(cid:str,bounds:list[str,],start_date:str,end_date:str,**kwargs)->list[str]:
    exec_code(f'from geeservice.geeFunc.baseTool import import_FeatureCollection as FC,import_ImageCollection as IC')        
    resp = eval_code(f'IC.get_instance("{cid}").filter_Bounds(FC({str(bounds)})).filter_Date("{start_date}","{end_date}").get_ids()')
    if resp['code'] == 200:
        return resp['result']
    else:
        raise Exception(f'筛选图像id失败：{resp["msg"]}')

def get_filtered_info(cid,info_type:list[str,str] = ['getinfo','gethtml']):
    # 需要优先筛选，为filter_img_id后的方法
    exec_code(f'from geeservice.geeFunc.baseTool import import_FeatureCollection as FC,import_ImageCollection as IC')        
    if 'getinfo' in info_type and 'gethtml' not in info_type:
        resp = eval_code(f'IC.get_instance("{cid}").get_info()')
    elif 'gethtml' in info_type and 'getinfo' not in info_type:
        resp = eval_code(f'IC.get_instance("{cid}")._repr_html_()')
    elif 'getinfo' in info_type and 'gethtml' in info_type:
        resp = eval_code(f'IC.get_instance("{cid}").get_info(),IC.get_instance("{cid}")._repr_html_()')

    if resp['code'] == 200:
        return resp['result']
    else:
        raise Exception(f'获取筛选结果信息失败：{resp["msg"]}')


class VisParams(BaseModel):
    """GEE影像可视化参数模型（符合Google官方规范）"""
    # 核心必填字段
    bands: List[str] = Field(
        description="要显示的波段列表，如RGB真彩色填['B4','B3','B2']（基于影像数据集的波段名称填写）",
        examples=[["B4", "B3", "B2"]]
    )
    # 必填字段（控制影像拉伸显示）
    min: Optional[Union[float, List[float]]] = Field(
        default=None,
        description="拉伸最小值，单值所有波段共用，列表则对应每个波段",
        examples=[0.0, [0.0, 0.0, 0.0]]
    )
    max: Optional[Union[float, List[float]]] = Field(
        default=None,
        description="拉伸最大值，单值所有波段共用，列表则对应每个波段",
        examples=[0.3, [0.3, 0.3, 0.3]]
    )
    # 扩展可选字段
    palette: Optional[List[str]] = Field(
        default=None,
        description="单波段影像的颜色调色板（十六进制颜色值列表）",
        examples=[["000000", "FF0000", "FFFF00"]]
    )
    opacity: Optional[float] = Field(
        default=None,
        ge=0.0,  # 限制最小值0
        le=1.0,  # 限制最大值1
        description="影像透明度，取值范围0-1（1为不透明）",
        examples=[1.0]
    )
    gamma: Optional[Union[float, List[float]]] = Field(
        default=1.0,
        description="伽马校正值，调整影像亮度，用户如果需要提高影像亮度，可以尝试降低伽马值，反之增加",
        examples=[1.0]
    )

    class Config:
        # 允许传入GEE的其他小众参数（兼容扩展性）
        extra = "allow"


class ParamsGetMapUrl(VisParams):
    img_ids: List[str] | str = Field(description="单个影像id或影像ID列表")

def get_map_urls(
    img_ids: str | list,
    vis_params: dict | VisParams | None = None,
    **kwargs
) -> str | list[str]:
    """
    生成GEE影像的地图URL
    :param img_ids: 单个影像ID或ID列表
    :param vis_params: 可视化参数（dict/VisParams实例）
    :param kwargs: 可视化零散参数（补充/覆盖vis_params）
    :return: 地图URL字符串
    """
    try:
        # 步骤1：统一处理vis_params，合并kwargs（kwargs优先级更高）
        if isinstance(vis_params, VisParams):
            # VisParams实例 → 转dict后合并kwargs
            vis_dict = vis_params.model_dump(exclude_none=True)
            vis_dict.update(kwargs)  # kwargs覆盖vis_params中的同名参数
        elif isinstance(vis_params, dict):
            # dict → 合并kwargs后校验
            vis_dict = {**vis_params, **kwargs}
        elif vis_params is None:
            # 仅传kwargs → 直接用kwargs校验
            vis_dict = kwargs
        else:
            # 非法类型 → 抛错
            raise TypeError(f"vis_params仅支持dict/VisParams/None，当前类型：{type(vis_params)}")

        # 步骤2：用VisParams校验最终的参数字典（核心！保证格式合规）
        vis_params_obj = VisParams(** vis_dict)
        vis = vis_params_obj.model_dump(exclude_none=True)

        # 步骤3：执行原有逻辑（修复列表字符串拼接问题）
        exec_code(f'from geeservice.geeFunc.baseTool import get_map_urls')
        if isinstance(img_ids, str):
            resp = eval_code(f'get_map_urls("{img_ids}", {vis})')
            if resp['code'] == 200:
                return resp['result']
            else:
                # 工具函数直接抛出异常，被保护时就会被打上错误标记
                raise Exception(resp["msg"])
        elif isinstance(img_ids, list):
            # 转换为双引号列表，避免eval解析报错
            img_ids_str = str(img_ids).replace("'", '"')
            resp = eval_code(f'get_map_urls({img_ids_str}, {vis})')
            if resp['code'] == 200:
                return resp['result']
            else:
                raise Exception(resp["msg"])
        else:
            raise TypeError(f"img_ids仅支持str/list，当前类型：{type(img_ids)}")

    except ValidationError as e:
        raise ValueError(f"可视化参数格式错误：{e}") from e
    except TypeError as e:
        raise ValueError(f"参数类型错误：{e}") from e
    except Exception as e:
        raise RuntimeError(f"生成地图URL失败：{e}") from e