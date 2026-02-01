## 解耦数据与地图：引入 TableManager 并增强 CSV 管理功能

### 1. 创建 `TableManager.ts` (数据管理类)
- **核心职责**:
    - **CSV 数据管理**: 存储 `importedCSVList`（包含原始文本、解析后的 JSON 对象）。
    - **关联逻辑**: 维护 `dataState` (Map<区域名, 数值数组>)，负责将 CSV 数据映射到地理区域。
    - **操作接口**: 提供 `addCSV`、`removeCSV`、`updateCSV`（编辑文本后重新解析）方法。
    - **模板数据**: 负责生成符合 CSV 格式的示例数据并初始化。

### 2. 重构 `MapManager.ts` (地图操作类)
- **核心职责**: 仅负责 Leaflet 地图初始化、图层添加、样式刷新（`updateLayerStyles`）及选中操作。
- **解耦**: 移除内部的 `dataState` 和 `timeConfig`（或改为通过 `TableManager` 获取），`updateLayerStyles` 将通过 `TableManager.getDataForRegion(name)` 获取数值。

### 3. 增强 `SearchSection.vue` 交互
- **Loading 状态**: 在搜索输入框集成 `:loading="loading"`，并在列表下方显示“正在检索...”提示。

### 4. 侧边栏功能升级 (`DataSidebar.vue`)
- **CSV 已添加列表**: 
    - 在“导入数据”标签页下方增加一个类似于城市列表的 CSV 管理区域。
    - 每个条目包含：文件名、查看按钮 (View)、删除按钮 (Delete)。
- **全屏文本查看/编辑器 (Dialog)**:
    - 弹出居中 Dialog，以标准文本格式显示 CSV 内容。
    - **可编辑**: 用户可直接修改文本，保存时触发 `TableManager.updateCSV` 重新解析数据，并自动触发地图样式更新。

### 5. 样式与空状态
- 统一侧边栏视觉风格。
- 当 `TableManager` 中无数据时，保持图表与表格的“暂无数据”空状态。

---

## **实施步骤**
1. **第一步**: 新建 `TableManager.ts`，实现数据解析与列表维护逻辑。
2. **第二步**: 修改 `MapManager.ts`，将其数据依赖转向 `TableManager`。
3. **第三步**: 更新 `SearchSection.vue`，添加搜索 Loading 反馈。
4. **第四步**: 在 `DataSidebar.vue` 中实现 CSV 列表展示及全屏编辑 Dialog 逻辑。
