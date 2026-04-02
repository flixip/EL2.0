import functools
from typing import Callable, Optional, Any, List, Union
from pydantic import BaseModel, Field
from langchain_core.tools import tool as create_tool

# ==================== Schema（拆分索引/切片，还原对应description） ====================
class GetOriginRawArgs(BaseModel):
    func_name: Optional[str] = Field(
        default=None,
        description="输入需要获取对应原始数据的函数名",
        examples=["add_func"]
    )

# 纯索引专用Schema（description仅针对索引）
class GetOriginByIndexArgs(BaseModel):
    func_name: str = Field(
        description="输入需要获取对应原始数据的函数名",
        examples=["list_func"]
    )
    indices: Union[int, List[int]] = Field(
        ...,
        description="按索引获取对应原始数据，单个int/多个int列表（如0、[1,3]）",
        examples=[0, [1,3]]
    )

# 纯切片专用Schema（新增，description仅针对切片）
class GetOriginBySliceArgs(BaseModel):
    func_name: str = Field(
        description="输入需要获取对应原始数据的函数名",
        examples=["list_func"]
    )
    start: Optional[int] = Field(default=None, description="切片起始索引（默认None=从开头取）", example=0)
    end: Optional[int] = Field(default=None, description="切片结束索引（默认None=取到末尾），取前10个传10", example=10)

class GetOriginByKeyArgs(BaseModel):
    func_name: str = Field(
        description="输入需要获取对应原始数据的函数名",
        examples=["dict_func"]
    )
    keys: Union[str, List[str]] = Field(
        ...,
        description="按字典键获取对应原始数据，单个str/多个str列表",
        examples=["name", ["name","age"]]
    )

# ==================== Summary（拆分索引/切片为独立方法） ====================
class Summary:
    def __init__(self):
        self.data = {}

    def summarize(self, func: callable, str_limit: int = 100, list_limit: int = 5) -> callable:
        original_str_limit, original_list_limit = str_limit, list_limit
        if not isinstance(original_str_limit, int) or original_str_limit <= 0:
            str_limit = 100
            print(f"【警告】str_limit={original_str_limit} 重置为100")
        if not isinstance(original_list_limit, int) or original_list_limit <= 0:
            list_limit = 5
            print(f"【警告】list_limit={original_list_limit} 重置为5")

        @functools.wraps(func)
        def inner(*args, **kwargs):
            original_data = func(*args, **kwargs)
            self.data[func.__name__] = original_data
            
            # 如果错误，直接返回错误信息而不进行摘要
            if "执行失败" in original_data or "error" in original_data or "错误" in original_data or "异常" in original_data:
                return original_data

            if isinstance(original_data, str) and len(original_data) > str_limit:
                return f"【{func.__name__}】返回字符串类型 <已摘要为前{str_limit}个字符>：{original_data[:str_limit]}...原数据长度：{len(original_data)}（通过get_origin_* 等方法获取完整信息）"
            elif isinstance(original_data, list):
                # 列表类型把列表元素也摘要一下，不然元素太长token也爆炸
                summary_data = []
                for item in original_data[:list_limit]:
                    summary_data.append(str(item)[:str_limit] + "...")
                return f"【{func.__name__}】返回列表类型 <已摘要为前{list_limit}个元素>：{summary_data}...原数据长度：{len(original_data)}（通过get_origin_* 等方法获取完整信息）"
            elif isinstance(original_data, dict):
                summary_dict = {}
                has_truncated = False
                for k, v in original_data.items():
                    str_v = str(v)
                    if len(str_v) > str_limit:
                        summary_dict[k] = str_v[:str_limit] + "..."
                        has_truncated = True
                    else:
                        summary_dict[k] = v
                if has_truncated:
                    return f"【{func.__name__}】返回字典类型 <已摘要>：{summary_dict}...（通过get_origin_* 等方法获取完整信息）"
            return original_data

        return inner

    def get_origin_raw(self, func_name: str = None) -> any:
        if func_name is None:
            return self.data if self.data else "暂无原始数据"
        return self.data.get(func_name, f"未找到【{func_name}】的原始数据")

    # 纯索引方法：仅处理单个/多个索引（不碰切片）
    def get_origin_by_index(self, func_name: str, *indices: int) -> any:
        origin = self.get_origin_raw(func_name)
        if not isinstance(origin, (list, str)):
            return f"【类型错误】{func_name} 非列表/字符串类型"
        try:
            return origin[indices[0]] if len(indices) == 1 else [origin[i] for i in indices]
        except IndexError:
            return f"【索引错误】超出范围，长度：{len(origin)}"

    # 纯切片方法：仅处理切片（独立方法，逻辑简单）
    def get_origin_by_slice(self, func_name: str, start: Optional[int] = None, end: Optional[int] = None) -> any:
        origin = self.get_origin_raw(func_name)
        if not isinstance(origin, (list, str)):
            return f"【类型错误】{func_name} 非列表/字符串类型"
        try:
            return origin[start:end]
        except IndexError:
            return f"【切片错误】超出范围，长度：{len(origin)}"

    def get_origin_by_key(self, func_name: str, *keys: str) -> any:
        origin = self.get_origin_raw(func_name)
        # or 是如果前者false，就后者，如果前者true,就前者,如果不是字典就检查是不是list 
        if not isinstance(origin, dict) or isinstance(origin, list) and isinstance(origin[0], dict):
            return f"【类型错误】{func_name} 非字典或list<dict>类型"
        
        try:
            if isinstance(origin, list):
                for item in origin:
                    result = item[keys[0]] if len(keys) == 1 else {k: item[k] for k in keys}
                return result
            return origin[keys[0]] if len(keys) == 1 else {k: origin[k] for k in keys}
        except KeyError as e:
            return f"【键错误】{e}，字典键：{list(origin.keys())}"

class Protector:
    def __init__(self):
        self.retry_count = {}

    def protect(self, func, error_guide: str = "", max_count: int = 3) -> callable:
        @functools.wraps(func)
        def inner(*args, **kwargs):
            func_name = func.__name__
            self.retry_count.setdefault(func_name, 0)
            if self.retry_count[func_name] >= max_count:
                raise Exception(f"【{func_name}】重试{max_count}次失败")
            self.retry_count[func_name] += 1
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return f"【{func_name}】执行失败（第{self.retry_count[func_name]}次）：{e}\n{error_guide}"
        return inner

# ==================== Supervisor（拆分索引/切片，还原对应description） ====================
class Supervisor:
    def __init__(self):
        self.protector = Protector()
        self.summarizer = Summary()
        
        # 核心映射：拆分索引/切片的description（各自独立，不混淆）
        self._tool_meta = {
            "get_origin_raw": {
                "args_schema": GetOriginRawArgs,
                "description": "【get_origin_raw 工具提示】获取被摘要的函数的完整原始返回值，当需要获取被摘要数据的完整原始信息时调用"
            },
            "get_origin_by_index": {
                "args_schema": GetOriginByIndexArgs,
                "description": "【get_origin_by_index 工具提示】按索引获取被摘要的函数的原始数据，支持列表/字符串类型返回值（支持单个/多个索引），当需要按取单个（多个）索引（元素）时调用此工具。"
            },
            "get_origin_by_slice": {  # 新增切片映射，专属description
                "args_schema": GetOriginBySliceArgs,
                "description": "【get_origin_by_slice 工具提示】按切片获取被摘要的函数的原始数据，支持列表/字符串类型返回值，当只需要取原始数据中指定范围的元素或指定元素时调用此工具。"
            },
            "get_origin_by_key": {
                "args_schema": GetOriginByKeyArgs,
                "description": "【get_origin_by_key 工具提示】按字典键（支持单个/多个键）获取被摘要的函数的原始数据，支持字典或list<dict>类型返回值，当需要按取指定键值对时调用此工具。"
            }
        }

    def supervise(self, func: Optional[Callable] = None, **kwargs) -> Callable:
        '''
        二合一装饰器：保护+摘要  
        :param func: 要保护的函数  
        :param kwargs: 保护参数（error_guide, max_count）和摘要参数（str_limit, list_limit）  
        :return: 保护后的函数   
        '''
        def decorator(_func: Callable) -> Callable:
            protect_kwargs = {k: kwargs[k] for k in ["error_guide", "max_count"] if k in kwargs}
            summary_kwargs = {k: kwargs[k] for k in ["str_limit", "list_limit"] if k in kwargs}
            protected_func = self.protector.protect(_func,** protect_kwargs)
            supervised_func = self.summarizer.summarize(protected_func, **summary_kwargs)
            return supervised_func
        return decorator(func) if func else decorator

    # ==================== 拆分索引/切片的透传方法 ====================
    def get_origin_raw(self, func_name: Optional[str] = None) -> any:
        """透传Summary的get_origin_raw方法"""
        return self.summarizer.get_origin_raw(func_name)

    def get_origin_by_index(self, func_name: str, *indices: int) -> any:
        """透传Summary的get_origin_by_index方法（纯索引）"""
        return self.summarizer.get_origin_by_index(func_name, *indices)

    def get_origin_by_slice(self, func_name: str, start: Optional[int] = None, end: Optional[int] = None) -> any:
        """透传Summary的get_origin_by_slice方法（纯切片）"""
        return self.summarizer.get_origin_by_slice(func_name, start, end)

    def get_origin_by_key(self, func_name: str, *keys: str) -> any:
        """透传Summary的get_origin_by_key方法"""
        return self.summarizer.get_origin_by_key(func_name, *keys)

    def reset_retry_count(self, func_name: Optional[str] = None) -> str:
        """重置重试次数（功能与原lambda一致）"""
        if func_name is None:
            self.protector.retry_count.clear()
            return "已重置所有函数的重试次数"
        else:
            self.protector.retry_count.update({func_name: 0})
            return f"重置【{func_name}】重试次数"

    # ==================== get_tool方法（适配切片方法） ====================
    def get_tool(self, func: str | Callable) -> Callable:
        """
        一键生成Tool（def函数名天然正确，无<lambda>问题）
        :param func: 函数名（str）或函数对象（Callable）
        :return: 新版BaseTool对象
        """
        # 1. 解析函数名和函数对象
        if isinstance(func, Callable):
            target_func = func
            func_name = target_func.__name__  # def函数__name__天然正确
        elif isinstance(func, str):
            func_name = func
            target_func = getattr(self, func_name)
        else:
            raise TypeError(f"func必须是str或Callable，当前类型：{type(func)}")
        
        # 2. 校验函数是否支持
        if func_name not in self._tool_meta:
            raise ValueError(f"不支持的函数：{func_name}，支持：{list(self._tool_meta.keys())}")
        
        # 3. 获取预设meta
        meta = self._tool_meta[func_name]

        # 4. 适配入参逻辑（拆分索引/切片，各自独立）
        def wrapper(**kwargs):
            if func_name == "get_origin_by_index":
                # 纯索引逻辑
                indices = kwargs.pop("indices")
                return target_func(kwargs["func_name"], *(indices if isinstance(indices, list) else [indices]))
            elif func_name == "get_origin_by_slice":
                # 纯切片逻辑（直接传start/end）
                return target_func(kwargs["func_name"], kwargs.get("start"), kwargs.get("end"))
            elif func_name == "get_origin_by_key":
                # 纯键逻辑
                keys = kwargs.pop("keys")
                return target_func(kwargs["func_name"], *(keys if isinstance(keys, list) else [keys]))
            else:
                # 原始数据逻辑
                return target_func(** kwargs)
        
        wrapper.__name__ = func_name
        # 5. 调用新版create_tool（无name参数）
        return create_tool(
            wrapper,  # 唯一位置参数：函数（__name__=func_name）
            description=meta["description"],  # 还原各自的专属description
            args_schema=meta["args_schema"],
        )


class TodoList:
    def __init__(self):
        self.list = []
        
    def add_task(self, task_name: str, task_desc: str):
        self.list.append({"name": task_name, "desc": task_desc})
        print(f"添加任务：{task_name}，描述：{task_desc}")
    
    def query_task(self, task_name: str| None=None):
        if task_name is None:
            return self.list
        else:
            return [task for task in self.list if task["name"] == task_name]
    
    def check_task(self, task_name: str):
        return task_name in [task["name"] for task in self.list]
    
        
if __name__ == '__main__':
    supervisor = Supervisor()
    # 测试索引工具（纯索引description）
    tool_index = supervisor.get_tool(supervisor.get_origin_by_index)
    print("索引工具描述：", tool_index.description)
    # 测试切片工具（纯切片description）
    tool_slice = supervisor.get_tool(supervisor.get_origin_by_slice)
    print("切片工具描述：", tool_slice.description)
    # 测试原始数据工具
    tool_raw = supervisor.get_tool(supervisor.get_origin_raw)
    print("原始数据工具描述：", tool_raw.description)