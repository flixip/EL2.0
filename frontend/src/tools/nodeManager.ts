import e_Start from '../components/Nodes/e_Start.vue'
import e_Add from '../components/Nodes/e_Add.vue'
import e_Output from '../components/Nodes/e_Output.vue'
import e_Sub from '../components/Nodes/e_Sub.vue'
import e_Predict from '../components/Nodes/e_Predict.vue'
import e_ViewImg from '../components/Nodes/e_ViewImg.vue'

import { markRaw,type Ref ,watch,type Reactive,reactive, ref,toRaw } from 'vue'
import type{ VueFlowStore ,Connection} from '@vue-flow/core'



interface NodeConfig{
  id:string,
  type:string,
  position:{x:number,y:number},
  style_data:any,
  func:(data:any)=>any,
  description:string,
}


/**
 * 随机位置生成器
 * 用于节点的随机位置生成
 */
export const random_pos = () => ({ x: Math.random() * 400, y: Math.random() * 400 })



/**
 * 节点管理器
 * 程序想要跟着流程图跑，那么就得设计一套跟着图跑的逻辑
 * vueflow没有提供数据流传递的逻辑，那么只写一个数据流管理器就够了吗？
 * 不够，因为和图表的关联性不够，不好操作，只能找到一个中间节点
 * 如果说流管理器靠图表配置，也就是写node对象，那么只能把node对象作为一个根逻辑，在此基础上进行添砖加瓦
 * 打个比方，核心逻辑写好，然后流管理器按逻辑来运行，节点管理器按逻辑来变化，两者完全可以独立，一个控制动作，一个控制逻辑
 * 所以想要写一套可以逻辑简单的生成输入，输出组件的节点管理器，其不走就应该是，先写好输入输出逻辑，流管理器负责依据这些逻辑运行，节点管理器根据要求渲染，控制样式的变化
 * 所以问题是怎么写一个用户创建组件，然后自动生成好这个node对象逻辑
 * 试想用户要写一个自定义节点，这也是工作流必须要有的一个节点类型
 * 这个节点的外观嗯，可以很简单，后续可以考虑外观也自定义
 * 这个节点至少得有确定关系的逻辑,貌似不需要节点考虑自己链接了多少个其他节点，因为节点的关系用边就可以唯一确定
 * 因为边只有一个target 和 source，所以节点的关系用边就可以唯一确定
 * 那么数据的传递其实是依赖边进行传递的，
 * 有没有必要设计一个节点有多个输入和输出的逻辑呢？有
 * 如果说把节点看成一个函数，那么节点的输入和输出就可以用函数的参数和返回值来表示，除了输入节点这边不建议带动态数据，默认数据看需求
 * 那么其实完全可以就把节点Id和他的动作函数做一个映射，根本不需要用到其他逻辑
 * 所以完全可以写一个创建某个节点时记录节点的动作函数，然后根据边的关联，依次执行就可以了
 * 那么会不会出现一些怪问题呢？比如需不需要考虑多线程，同时运行，一个核心节点需要接受参数，会不会不同时到达节点，那么节点的运行逻辑是什么？
 * 貌似当时工作流设计的时候就没有考虑多线程的问题吧，都是按顺序执行，那么其实完全可以就把程序从上到下执行一遍就可以了
 * 甚至写的时候可以没有顺序，因为考虑按边来顺序执行
 * 
 * 好的，那么现在的思路是把动作和样式独立出来，
 * 动作流写的形式就是写一个id:函数映射表
 * 输入节点带数据，默认不带函数，或者带一个占位函数，返回数据
 * 中间节点携带动作函数，只接受一个输入边，返回一个输出边，如果有循环控制就在侧面加边，一个句柄只连一条线
 * 输出节点接受数据，函数就是更新节点的样式，将数据渲染出来，或者有其他不需要改样式的输出方法，给出一些提示这样
 * 执行逻辑就是查到第一个节点，以这个节点为起点，查链接这个节点的边，然后找到下一个节点，然后执行下一个节点带的逻辑
 * 
 * 那么现在可以回答怎么写一个自定义节点了，首先需要自定义节点类型（输入/中间/输出），定义完毕出现相应样式的改变
 * 然后需要定义输入的类型，（字符/数字/对象/数组/布尔值）
 * 或者不需要查类型？直接让用户写函数，反正大不了报错或者undefined,让他自己取debug，那么需要可能做一些提示告诉他怎么写
 * 
 * 那么到底要不要所谓的节点管理器呢？
 * 貌似不需要了，因为useVueflow已经提供了一些方法，然后如果我要改样式，我可以把这个逻辑写到节点的动作函数中
 * 所以现在的其实就开发一个辅助创建节点的同时，把id函数映射表同时记录下来
 * 嗯，设想用户面对空空的表，肯定要加节点，那肯定不能让他编那个根json ,这很反人性
 * 所以其实应该提前把所有节点逻辑写好，然后只需点点点按钮就能加节点，然后是自定义节点
 * 
 * 来到开发问题上，那我们开发的时候应该怎么组织代码呢？
 * 首先是节点管理器面板，没有面板开发也不好测试，同时还需要给面板注入对应逻辑
 * 然后是调试面板，控制执行逻辑，需要能找到起点，找到下一个节点，然后执行函数，单步执行功能
 * 执行逻辑这一块，不如写一个状态管理器，比如addNode只是addNode到状态管理器，我想在addNode的同时就把起点确定
 * 然后addEdges时就把id函数表给生成出来
 * 执行的时候顺着id函数表走就行，适当在函数里面加一些样式改变函数，这样更直观
 * 
 * 怎么解决编辑图表的时候的运行问题？要求有个编辑状态，编辑完成才可以运行
*/
export class NodeManager {
    flow:VueFlowStore;
    id_func_map:Reactive<any> = reactive({})
    initial_data:any={};
    cur_data:any={};
    cur_id:Ref<string> = ref('start');
    is_running:boolean=false;

    constructor(flow:VueFlowStore){
      this.flow = flow
      this._watchStatus()
    }
    /**
     * 输入初始数据，存在this.initial_data中
     * 目的是数据和样式分离
     * @param data 
     *
     * 初始化数据时重置一次，避免运行时不在运行起点
     */
    addInput(data:any={}){
      this.initial_data = data
      this.reset()
    }

    /**
     * 添加节点
     * @param config 节点配置对象
     * 节点配置对象包含id,type,position,style_data,func,description
     * id:节点id
     * type:节点类型
     * position:节点位置
     * style_data:节点样式数据
     * func:节点动作函数
     * description:节点描述
     */
    addNode(config:NodeConfig){
      const id = config.id
      this.id_func_map[id] = {
        func:config.func,
        description:config.description}
      this.flow.addNodes([
        {
          id: id,
          type: config.type,
          position: config.position,
          data: config.style_data,
        },
      ])
    }

    /**
     * 添加边
     * @param connection 边对象
     * 边对象包含source,target,id
     * 边的作用是连接节点,记录下一个节点id
     * 这样写在前面创建节点的时候可以不考虑下一个节点，专注于节点本身的逻辑
     */
    addEdge(connection:Connection){
      const start_id = connection.source
      const end_id = connection.target
      this.id_func_map[start_id].next_id = end_id
      this.flow.addEdges([
        {
          id: `${start_id}_to_${end_id}`,
          source: start_id,
          target: end_id,
        },
      ])
    }

   
    _watchStatus(){
      // 监听idfunc映射表变化,如果映射关系改变,则重置起点
     watch(()=>this.id_func_map,()=>{
      console.log('🔄检测到idfunc图发生改变，正在重置起点...')
      // 如果函数映射关系改变，也就是说修改了映射关系，那就重置一下运行起点
      this.reset()
     },{deep:true})
     // 监听当前节点id变化,如果id不是start,则认为在运行过程中
     watch(()=>this.cur_id,()=>{
      // 如果节点id不是start，则认为在运行过程中
      if (this.cur_id.value === 'start'){
        this.is_running = false
      }
      else{
        this.is_running = true
      }
     },{deep:true})
     
    }

    /**
     * 重置执行器
     * 1.将id重置为start
     */
    reset(){
      this.is_running = false
      this.cur_id.value = 'start'
      this.cur_data = this.initial_data
      console.log('✅初始化完毕\n当前节点id:',this.cur_id.value,'\n当前节点数据:',this.cur_data)
      console.log('当前idfunc映射表：',toRaw(this.id_func_map))
    }

    /**
     * 执行一步
     * 1.获取当前节点id
     * 2.根据id获取下一个节点id
     * 3.根据下一个节点id获取函数
     * 4.执行函数
     * 5.将返回值赋值给当前节点数据
     * 6.将当前节点id赋值为下一个节点id
     */
    async step(is_debug:boolean=true){
      const cur_id = this.cur_id.value
      const next_id = this.id_func_map[cur_id].next_id
      const func = this.id_func_map[next_id].func
      if (is_debug){
        console.log('执行前节点id:',cur_id,'\n执行前数据:',this.cur_data)
      }
      this.cur_data = await func(this.cur_data)
      this.cur_id.value = next_id
      if (is_debug){
        console.log('执行后节点:',next_id,'\n执行后数据:',this.cur_data)
      }
    }

    /**
     * 运行到结束
     * 直接判断是不是结束节点会导致结束节点的函数不被执行
     * 所以判断下一个节点是否存在，如果没有就结束运行
     */
    async run(){
      while (this.id_func_map[this.cur_id.value].next_id !== ''){
        await this.step(false)
      }
      console.log('运行到结束节点:',this.cur_id.value,'\n当前数据:',this.cur_data)
    }
}



/**
 * 节点类型定义
 */
export const nodeTypes = {
    Add: markRaw(e_Add),
    Start: markRaw(e_Start),
    Output: markRaw(e_Output),
    Subtract: markRaw(e_Sub),
    Predict: markRaw(e_Predict),
    ViewImg: markRaw(e_ViewImg),
}




// /**
//  * 输入节点数据接口
//  */
// export interface InputNodeData {
//     value: string | number,
// }

// export const addInputNode = (
//   addNodes:AddNodes,
//   data:InputNodeData
// ) => (    
//   addNodes({
//     id: `input`,
//     type: 'Start',
   
//     position: random_pos(),
//     data: data,
//   })
// )

// /**
//  * 输出节点数据接口
//  */

// export const addOutputNode = (
//   addNodes:AddNodes,
//   updateNodeData:UpdateNodeData,
// ) => ( 
//   addNodes({
//     id: `output`,
//     type: 'Output',
//     position: random_pos(),
//     data: {
//       input_data:{   // 可以当作默认值，也可以当作检查数据类型的依据
//        value: '',
//       },
//       value:'正在等待数据...',
//       func:(data:any)=>{
//         updateNodeData('output',{value:data.value})
//         return data
//       }
//     },
//   })
// )