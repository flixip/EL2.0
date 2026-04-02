from pydantic import BaseModel, Field
from langchain_core.tools import tool as create_tool  # 新版LangChain推荐导入
from dataloader.utils.geeinfo import \
    filter_dataset, get_dataset_fields, get_detail, \
    DatasetFilterParams
from Aichat.utils import Supervisor  # 【核心替换1】引入新的Supervisor类
from typing import Optional

# ==================== 第一步：初始化全局Supervisor（替代单独的Summary/protect） ====================
supervisor = Supervisor()

super_tools = [
    supervisor.get_tool(supervisor.get_origin_raw),
    supervisor.get_tool(supervisor.get_origin_by_index),
    supervisor.get_tool(supervisor.get_origin_by_key),
    supervisor.get_tool(supervisor.get_origin_by_slice)
]


# ==================== 第二步：外部业务函数的参数Schema（保留，仅适配新装饰器） ====================
class ParamsGetDetail(BaseModel):
    """获取数据集详情参数（精简省token）"""
    cids: list[str] | str = Field(description="数据集ID，单个str或str列表")
    field: list[str] = Field(
        description="要获取详情的字段列表,可以通过调用get_dataset_fields工具获取所有可用字段",
        examples=[['name','producer','pixel_size_num'],['revisit_interval','tags']]
    )


# 【外部业务函数用langchain的tool，但简化】
geedataset_tools = [
    create_tool(
        supervisor.supervise(get_dataset_fields,list_limit=100),
        description="获取GEE数据集信息的所有可用表单字段"
    ),
    create_tool(
        supervisor.supervise(filter_dataset),
        args_schema=DatasetFilterParams,
        description="根据筛选条件搜索GEE数据集,该工具返回符合条件的数据集ID列表"
    ),
    create_tool(
        supervisor.supervise(get_detail),
        args_schema=ParamsGetDetail,
        description="""
        根据数据集ID和字段查询详情
        注意查询字段如果包含不存在的字段，会自动移除，请注意返回信息中的error_fields元素！
        """
    ),
]

# ==================== 第四步：GEE影像工具（外部业务函数+预设工具一键生成） ====================
# 【核心替换2】用supervisor.supervise二合一装饰器
from geeservice.utils import fliter_img_id,ParamsFilterImgId\
    ,get_map_urls,ParamsGetMapUrl

# 【核心替换3】预设工具全部用supervisor.get_tool一键生成，自动用省token的description
geefunc_tools = [
    # 外部业务函数简化处理
    create_tool(
        supervisor.supervise(fliter_img_id,
            error_guide="如果触发计算机积极拒绝的问题，可能是后端服务未开启，道歉无法获取准确数据，然后根据自己已知的信息回答"
            ),
        args_schema=ParamsFilterImgId,
        description="根据数据集ID、边界、日期筛选影像ID列表"
    ),
    create_tool(
        supervisor.supervise(get_map_urls,
            error_guide="如果触发波段存在性错误，参考错误提示的存在的波段按需调整"
                             ),
        args_schema=ParamsGetMapUrl,
        description="根据影像ID列表和可视化参数获取可用于在地图上显示的影像url列表"
    ),
    
]


if __name__ == '__main__':
    supervisor = Supervisor()
    get_detail = supervisor.supervise(get_detail)
    result = get_detail(cids=['LANDSAT/LT05/C02/T1_L2'],field=['name','producer','pixel_size_num','description'])
    print(result)