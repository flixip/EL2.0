import sys
sys.path.append('E:/github/EL2.0')

from dotenv import load_dotenv
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage,ToolMessage
from langchain.tools import tool
from pydantic import BaseModel, Field
from Aichat.tools import geedataset_tools,super_tools,geefunc_tools
from Aichat.utils import Supervisor


load_dotenv()


MODEL_NAME = "qwen-plus-2025-09-11"

llm = ChatTongyi(
      model_name=MODEL_NAME,
      streaming=False,
      model_kwargs={
            "temperature": 0.7,  # 核心参数：控制随机性，0-1之间，推荐0.5-0.8
            "top_p": 0.9,        # 配合temperature使用，一般设0.9即可
            "seed": None         # 如果想偶尔换答案，可设随机seed（如123/456），None则每次随机
                 })

class QueryAgent(BaseModel):
      question: str = Field(description="查询语句")

# agent 是从本地数据中获取有关数据集的专业agent 可以当做搜索引擎 数据基础是从gee官网获取三大影像数据集信息
class Agent:
      def __init__(self,name:str,system_prompt:str,need_super_tools:bool=True,**kwargs):
            self.name = name
            self.agent = create_agent(
                  model=kwargs.get("model",llm),
                  tools = super_tools + kwargs.get("tools",[]) if need_super_tools else kwargs.get("tools",[]),
                  system_prompt=system_prompt,
            )
            self.supervisor = Supervisor() if need_super_tools else None
            # 执行记录可追溯
            self.record = []
            
      def query(self, question:str):
            # 每次query都重置重试次数
            self.supervisor.reset_retry_count()
            # 重置记录结果，避免重复记录
            self.clear_record()
            resp = self.agent.invoke({"messages": [HumanMessage(content=question)]})
            self.record.append(resp)
            # 直接返回最后一条信息而不是完整响应
            self.count_tokens()
            return resp['messages'][-1].content
      
      def get_record(self):
            return self.record
      
      def clear_record(self):
            self.record = []

      def count_tokens(self):
            token_count = 0
            for answer in self.record:
                  msgs = answer['messages']
                  for msg in msgs:
                        if isinstance(msg,AIMessage) or isinstance(msg,ToolMessage):
                              token_count += int(msg.response_metadata['token_usage']['total_tokens'])
            print(f'{self.name} 总token消耗: {token_count}')
            return token_count
      
      def as_tool(self,description:str,**kwargs):
            def wrapper(question:str):
                  return self.query(question)
            
            if self.supervisor:
                  wrapper = self.supervisor.supervise(wrapper,**kwargs)
            
            wrapper.__name__ = f"query_agent_{self.name}"
            return tool(
                  wrapper,
                  args_schema=QueryAgent,
                  description=description,
                  )
      
agent001 = Agent(
      name = "agent001",
      system_prompt="""
      你是一个专业的数据集搜索助手，根据问题进行相应检索操作。
      严格遵守以下规则：
      禁止并行调用工具，禁止硬编码数据集ID，严禁编造数据集ID。
      如果要查询多个数据集的数据集id 比如查询Sentinel-2和landsat数据集的id，先查询Sentinel-2数据集的id并记录，再查询landsat数据集的id。
      工具使用：
      一般要先用filter_dataset工具根据筛选条件搜索GEE数据集,该工具返回符合条件的数据集ID列表。
      然后根据筛选来的数据集ID列表，用get_detail工具根据数据集ID和需要查询的字段查询需要了解的详情.
      get_origin_* 工具是获取摘要后的工具函数返回值的原始值，记住一开始调用工具后返回的返回值类型信息，然后根据工具提示的使用场景合理选择调用的工具函数
      """,
      tools = geedataset_tools
      )

agent001_tool = agent001.as_tool(
      description="""agent001是专业数据集搜索助手，可以组织专业检索信息来让agent001检索数据集信息，
      例如：请检索并推荐两个覆盖2008-2009年的Landsat系列卫星影像推荐，并说明推荐原因"""
      )

agent002 = Agent(
      name = "agent002",
      system_prompt="""你是一个专业的影像操作助手，可以根据手中工具执行相应操作
      目前支持的操作有：
      1. 根据影像数据集ID、边界、日期筛选影像ID列表
      2. 根据影像ID列表和可视化参数获取可用于在地图上显示的影像url列表
      严格遵守以下规则：「用给定的、已验证有效的数据集ID，查询影像ID、生成地图URL」
      **绝对禁止自己生成、硬编码任何数据集ID**，所有数据集ID必须来自上游传入的已验证结果；
      """,
      tools = geefunc_tools
      )

agent002_tool = agent002.as_tool(
      description="""agent002是专业的影像操作助手,支持的操作有：
      1. 根据影像数据集ID、边界、日期筛选影像ID列表
      2. 根据影像ID列表和可视化参数获取可用于在地图上显示的影像url列表
      
      提示词使用案例：
      1.请根据影像集id:LANDSAT/LT05/C02/T1_L2查询湖北省武汉市的2008-2009间的图像有几个，列举10个真实可用的id -> 列举10个真实可用的id
      2.请根据影像集id:LANDSAT/LT05/C02/T1_L2查询湖北省武汉市的2008-2009间的图像有几个，列举10个真实可用的id，并拿到其中的五个mapurl -> 列举10个真实可用的id，并拿到其中的五个mapurl
      3.请根据影像id:LANDSAT/LT05/C02/T1_L2/LT05_122038_20080320,...,获取影像url列表 -> 列举影像url列表
      
"""
      )




agent003 = Agent(
      name = "agent003",
      system_prompt="""你是一个专业的问答助手兼agent操作总管，可以通过工具调用的方式给agent工具提示词，来获取相关信息进行回答
      每次回答前，请先用你自己的知识回答，不确定再调用agent工具获取相关信息
      ### 绝对禁止行为
      1. 禁止并行调用query_agent_agent001和query_agent_agent002；
      2. 禁止在query_agent_agent001执行完成前，调用query_agent_agent002；
      3. 禁止query_agent_agent002使用任何非query_agent_agent001返回的数据集ID；
      4. 禁止对确定性错误进行重试；
      5. 禁止跳步执行、跳过结果校验；
      6. 禁止硬编码任何数据集ID、波段名称、区域、时间范围。
      
      ### 关于地图URL的处理规则
      1. 当你需要展示影像地图时，请确保获取到的地图URL（mapurl）保持原样，不要修改或截断；
      2. 地图URL通常格式为：https://earthengine.googleapis.com/v1/projects/.../tiles/{z}/{x}/{y}
      3. 请将所有地图URL完整地包含在回复中，这样前端才能正确识别并添加到地图上；
      4. 你可以在地图URL前后添加一些说明文字，但不要改变URL本身的格式。
      """,
      tools = [agent001_tool,
               agent002_tool]
      )

      
