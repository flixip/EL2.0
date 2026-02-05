<template>
  <div :class="[
    'h-full bg-white border-r border-gray-200 shadow-sm transition-all duration-300 flex flex-col overflow-hidden z-10',
    isExpanded ? 'w-80' : 'w-16'
  ]">
    <!-- 侧边栏头部 -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-linear-to-r from-emerald-50 to-teal-50">
      <div :class="[
        'flex items-center gap-2 transition-all duration-300 transform origin-left',
        isExpanded ? 'opacity-100 scale-100 w-auto' : 'opacity-0 scale-95 w-0 pointer-events-none'
      ]">
        <el-icon class="text-emerald-600"><DataAnalysis /></el-icon>
        <span class="font-bold text-gray-800 text-sm whitespace-nowrap">数据管理与分析</span>
      </div>

      <el-button 
        @click="isExpanded = !isExpanded"
        circle
        size="small"
        class="transition-all duration-300 shrink-0"
      >
        <el-icon :class="['transition-transform duration-300', isExpanded ? '' : 'rotate-180']">
          <ArrowLeft />
        </el-icon>
      </el-button>
    </div>

    <!-- 侧边栏内容 -->
    <div class="flex-1 relative overflow-hidden">
      <!-- 展开状态 -->
      <div :class="[
        'absolute inset-0 p-4 overflow-y-auto transition-all duration-300 delay-75 hide-scrollbar',
        isExpanded ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-8 pointer-events-none'
      ]">
        <el-collapse v-model="activeNames" accordion class="custom-collapse">
          <!-- 1. 数据管理 (整合导入与添加) -->
          <el-collapse-item name="data">
            <template #title>
              <div class="flex items-center gap-2 font-medium">
                <el-icon><Box /></el-icon>
                <span>数据管理</span>
              </div>
            </template>
            <div class="py-2">
              <el-tabs v-model="dataTab" class="custom-tabs">
                <el-tab-pane label="导入数据" name="import">
                  <div class="flex flex-col gap-4 pt-2">
                    <!-- 已导入 CSV 列表 (置顶) -->
                    <div v-if="tableManager.importedCSVList.value.length > 0" class="flex flex-col gap-2">
                      <div class="text-[10px] font-bold text-gray-400 px-1 uppercase tracking-wider">已导入数据</div>
                      <div 
                        v-for="item in tableManager.importedCSVList.value" 
                        :key="item.id"
                        class="group flex items-center justify-between p-2 rounded-lg border border-gray-100 bg-gray-50/50 hover:bg-emerald-50 hover:border-emerald-100 transition-all"
                      >
                        <div class="flex items-center gap-2 min-w-0 flex-1">
                          <el-icon class="text-emerald-500 shrink-0"><Document /></el-icon>
                          <span class="text-xs text-gray-700 truncate font-medium">{{ item.name }}</span>
                        </div>
                        <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <el-tooltip content="查看/编辑" placement="top">
                            <el-button circle size="small" @click="handleViewCSV(item)" class="!p-1">
                              <el-icon :size="12"><View /></el-icon>
                            </el-button>
                          </el-tooltip>
                          <el-tooltip content="删除" placement="top">
                            <el-button circle size="small" type="danger" plain @click="handleRemoveCSV(item.id)" class="!p-1">
                              <el-icon :size="12"><Delete /></el-icon>
                            </el-button>
                          </el-tooltip>
                        </div>
                      </div>
                    </div>

                    <!-- 添加数据按钮 -->
                    <div class="px-1">
                      <el-button 
                        type="primary" 
                        class="w-full bg-emerald-500 border-emerald-500 hover:bg-emerald-600"
                        @click="openAddDialog"
                      >
                        <el-icon class="mr-2"><Plus /></el-icon>
                        添加数据
                      </el-button>
                      
                      <!-- 暂无数据时的引导 -->
                      <div v-if="tableManager.importedCSVList.value.length === 0" class="mt-3 p-3 rounded-lg bg-emerald-50/30 border border-dashed border-emerald-200 text-center">
                        <div class="text-[10px] text-emerald-600/60 mb-2">暂无数据，建议先从加载示例开始</div>
                        <el-button type="success" size="small" plain @click="handleLoadTemplate" class="w-full">
                          加载示例模板
                        </el-button>
                      </div>
                    </div>
                  </div>
                </el-tab-pane>
                <el-tab-pane label="搜索添加" name="add">
                  <div class="flex flex-col gap-4 pt-2">
                    <SearchSection />
                    <AddedDataList />
                  </div>
                </el-tab-pane>
              </el-tabs>
            </div>
          </el-collapse-item>

          <!-- 2. 数据可视化 -->
          <el-collapse-item name="viz">
            <template #title>
              <div class="flex items-center gap-2 font-medium">
                <el-icon><Histogram /></el-icon>
                <span>数据可视化</span>
              </div>
            </template>
            
            <div v-if="tableManager.dataState.value.size === 0" class="py-10 text-center">
              <el-empty description="暂无数据" :image-size="60" />
              <el-button type="primary" size="small" plain @click="dataTab = 'import'">
                前往导入数据
              </el-button>
            </div>

            <div v-else class="flex flex-col gap-4 py-2">
              <div v-if="mapManager.selectedDistrict.value" class="flex items-center justify-between rounded bg-emerald-50 p-2 text-xs text-emerald-700 border border-emerald-100">
                <span class="truncate">当前选中: <b>{{ mapManager.selectedDistrict.value }}</b></span>
                <el-icon class="cursor-pointer hover:text-emerald-900" @click="mapManager.selectedDistrict.value = null"><Close /></el-icon>
              </div>

              <el-radio-group v-model="chartType" size="small" class="w-full justify-center">
                <el-radio-button label="line">趋势</el-radio-button>
                <el-radio-button label="bar">对比</el-radio-button>
                <el-radio-button label="table">表格</el-radio-button>
              </el-radio-group>

              <div v-show="chartType !== 'table'" class="h-48 w-full rounded bg-gray-50 p-2 border border-gray-100">
                <canvas ref="chartCanvas"></canvas>
              </div>

              <div v-show="chartType === 'table'" class="max-h-48 overflow-y-auto rounded border border-gray-100 text-[10px]">
                <table class="w-full border-collapse">
                  <thead class="sticky top-0 bg-gray-50 z-1">
                    <tr class="border-b border-gray-200">
                      <th class="p-1 text-left text-gray-500">区域</th>
                      <th class="p-1 text-right text-gray-500">数值</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="[name, values] in Array.from(tableManager.dataState.value)" :key="name" class="border-b border-gray-100 hover:bg-gray-50">
                      <td class="p-1 text-gray-700">{{ name }}</td>
                      <td class="p-1 text-right font-medium text-emerald-600">{{ (values as number[])[mapManager.timeConfig.value.yearIndex]?.toFixed(4) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div class="grid grid-cols-2 gap-2 text-xs">
                <div class="rounded bg-emerald-50 p-2 border border-emerald-100">
                  <div class="text-emerald-600/70">最大值</div>
                  <div class="text-lg font-bold text-emerald-600">{{ stats.max.value.toFixed(4) }}</div>
                  <div class="truncate text-[10px] text-gray-400">{{ stats.max.name }}</div>
                </div>
                <div class="rounded bg-rose-50 p-2 border border-rose-100">
                  <div class="text-rose-600/70">最小值</div>
                  <div class="text-lg font-bold text-rose-600">{{ stats.min.value.toFixed(4) }}</div>
                  <div class="truncate text-[10px] text-gray-400">{{ stats.min.name }}</div>
                </div>
              </div>
            </div>
          </el-collapse-item>

          <!-- 3. 图层配置 -->
          <el-collapse-item name="style">
            <template #title>
              <div class="flex items-center gap-2 font-medium">
                <el-icon><Setting /></el-icon>
                <span>图层配置</span>
              </div>
            </template>
            <div class="flex flex-col gap-4 py-2 text-xs text-gray-600">
              <div v-if="tableManager.dataState.value.size === 0" class="mb-2 p-2 rounded bg-amber-50 text-amber-700 border border-amber-100 text-[10px]">
                提示：当前无关联数据，配置将作为全局默认样式。
              </div>
              <div class="flex flex-col gap-2">
                <div class="flex items-center justify-between">
                  <span>低值颜色</span>
                  <el-color-picker v-model="startColorHex" size="small" />
                </div>
                <div class="flex items-center justify-between">
                  <span>高值颜色</span>
                  <el-color-picker v-model="endColorHex" size="small" />
                </div>
              </div>
              <div class="h-4 rounded border border-gray-100" :style="gradientStyle"></div>
              <div class="flex flex-col gap-3">
                <div>
                  <div class="mb-1 flex justify-between">
                    <span>不透明度</span>
                    <span class="text-emerald-600 font-medium">{{ (mapManager.mapConfig.value.opacity * 100).toFixed(0) }}%</span>
                  </div>
                  <el-slider v-model="mapManager.mapConfig.value.opacity" :min="0" :max="1" :step="0.01" />
                </div>
                <div>
                  <div class="mb-1 flex justify-between">
                    <span>Gamma 校正</span>
                    <span class="text-emerald-600 font-medium">{{ mapManager.mapConfig.value.gamma.toFixed(1) }}</span>
                  </div>
                  <el-slider v-model="mapManager.mapConfig.value.gamma" :min="0.1" :max="3" :step="0.1" />
                </div>
                <div class="grid grid-cols-2 gap-2">
                  <div>
                    <div class="mb-1">最小值</div>
                    <el-input-number v-model="mapManager.mapConfig.value.minValue" :step="0.01" size="small" class="w-full!" />
                  </div>
                  <div>
                    <div class="mb-1">最大值</div>
                    <el-input-number v-model="mapManager.mapConfig.value.maxValue" :step="0.01" size="small" class="w-full!" />
                  </div>
                </div>
              </div>
              <div class="flex items-center justify-between border-t border-gray-100 pt-2">
                <span>显示数值标注</span>
                <el-switch v-model="mapManager.mapConfig.value.showLabel" size="small" />
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>

        <!-- 时间轴开关 -->
        <div class="mt-4 flex items-center justify-between border-t border-gray-100 pt-4 text-xs text-gray-600 px-2">
          <div class="flex items-center gap-2">
            <el-icon class="text-emerald-500"><Timer /></el-icon>
            <span>启用时间轴</span>
          </div>
          <el-switch v-model="isTimeAxisEnabled" size="small" :disabled="tableManager.dataState.value.size === 0" />
        </div>
      </div>

      <!-- 收缩状态 -->
      <div :class="[
        'absolute inset-0 flex flex-col items-center py-6 gap-6 transition-all duration-300',
        !isExpanded ? 'opacity-100 scale-100' : 'opacity-0 scale-75 pointer-events-none'
      ]">
        <el-tooltip content="数据管理" placement="right">
          <el-button circle size="default" @click="expandAndOpen('data')">
            <el-icon><Box /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="数据可视化" placement="right">
          <el-button class="ml-0!" circle size="default" @click="expandAndOpen('viz')">
            <el-icon><Histogram /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="图层配置" placement="right">
          <el-button class="ml-0!" circle size="default" @click="expandAndOpen('style')">
            <el-icon><Setting /></el-icon>
          </el-button>
        </el-tooltip>
        <div class="mt-auto pb-4 text-center">
          <el-tooltip :content="isTimeAxisEnabled ? '关闭时间轴' : '开启时间轴'" placement="right">
            <el-switch v-model="isTimeAxisEnabled" size="small" :disabled="tableManager.dataState.value.size === 0" />
          </el-tooltip>
        </div>
      </div>
    </div>
  </div>

  <!-- 添加数据 Dialog -->
  <el-dialog
    v-model="showAddDialog"
    title="添加分析数据"
    width="60%"
    center
    destroy-on-close
    class="add-data-dialog"
  >
    <div class="flex flex-col gap-6">
      <!-- 快速操作 -->
      <div class="flex items-center gap-4">
        <el-button type="success" plain @click="loadTemplateToDialog">
          <el-icon class="mr-1"><Document /></el-icon>
          加载模板数据
        </el-button>
        <el-upload
          action="#"
          :auto-upload="false"
          :on-change="handleUploadToDialog"
          :show-file-list="false"
          accept=".csv"
        >
          <el-button type="primary" plain>
            <el-icon class="mr-1"><Upload /></el-icon>
            上传 CSV 文件
          </el-button>
        </el-upload>
      </div>

      <!-- 文本编辑区 -->
      <div class="flex flex-col gap-2">
        <div class="flex items-center justify-between">
          <span class="text-sm font-bold text-gray-700">数据内容预览与编辑</span>
          <el-input v-model="addDataForm.name" placeholder="文件名称" size="small" class="!w-64" />
        </div>
        <el-input
          v-model="addDataForm.rawText"
          type="textarea"
          :rows="12"
          placeholder="此处显示 CSV 文本内容，可手动输入或修改..."
          class="font-mono text-sm"
          @input="parseFormText"
        />
      </div>

      <!-- 字段映射区 -->
      <div v-if="addDataForm.headers.length > 0" class="rounded-lg bg-gray-50 p-4 border border-gray-100 flex flex-col gap-4">
        <div class="text-sm font-bold text-emerald-600">字段关联设置</div>
        <div class="grid grid-cols-2 gap-6">
          <div class="flex flex-col gap-2">
            <span class="text-xs text-gray-500">行政区划字段 (匹配地图):</span>
            <el-select v-model="addDataForm.mapping.name" placeholder="选择名称字段">
              <el-option v-for="h in addDataForm.headers" :key="h" :label="h" :value="h" />
            </el-select>
          </div>
          <div class="flex flex-col gap-2">
            <span class="text-xs text-gray-500">数值字段 (支持多选年份):</span>
            <el-select v-model="addDataForm.mapping.values" multiple collapse-tags placeholder="选择数值字段">
              <el-option v-for="h in addDataForm.headers" :key="h" :label="h" :value="h" />
            </el-select>
          </div>
        </div>
      </div>
    </div>
    <template #footer>
      <div class="flex justify-end gap-3">
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="confirmAddData" 
          :disabled="!addDataForm.name || !addDataForm.rawText"
          class="bg-emerald-500 border-emerald-500 hover:bg-emerald-600"
        >
          确认并添加
        </el-button>
      </div>
    </template>
  </el-dialog>

  <!-- CSV 文本编辑器 Dialog (用于查看/修改已有的) -->
  <el-dialog
    v-model="showEditor"
    :title="`编辑数据: ${editingCSV?.name}`"
    width="70%"
    center
    destroy-on-close
    class="csv-editor-dialog"
  >
    <div class="flex flex-col gap-4">
      <div class="text-xs text-gray-500 bg-amber-50 p-2 rounded border border-amber-100">
        提示：您可以直接在此处编辑 CSV 文本。保存后，系统将重新解析数据并更新地图样式。请确保格式正确（首行为表头，逗号分隔）。
      </div>
      <el-input
        v-model="editingCSV!.text"
        type="textarea"
        :rows="20"
        placeholder="请输入 CSV 格式文本..."
        class="font-mono text-sm"
      />
    </div>
    <template #footer>
      <div class="flex justify-end gap-3">
        <el-button @click="showEditor = false">取消</el-button>
        <el-button type="primary" @click="saveCSVEdit" class="bg-emerald-500 border-emerald-500 hover:bg-emerald-600">
          保存并更新
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { 
  DataAnalysis, ArrowLeft, Histogram, Setting, Upload, 
  UploadFilled, Timer, Close, CirclePlus, Box, View, Delete, Loading, Document, Plus
} from '@element-plus/icons-vue';
import type { UploadFile } from 'element-plus';
import MapManager from '@/tools/mapManager';
import TableManager, { type CSVDataItem } from '@/tools/tableManager';
import geoDataService from '@/services/GeoDataService';
import { Chart, registerables, type ChartTypeRegistry } from 'chart.js';
import SearchSection from './SearchSection.vue';
import AddedDataList from './AddedDataList.vue';

Chart.register(...registerables);

const mapManager = MapManager.getInstance();
const tableManager = TableManager.getInstance();
const isExpanded = ref(true);
const activeNames = ref(['data']); // 默认展开数据管理
const dataTab = ref('import'); // 默认显示导入标签
const chartType = ref<'line' | 'bar' | 'table'>('line');
const chartCanvas = ref<HTMLCanvasElement | null>(null);
let chartInstance: Chart | null = null;

const isTimeAxisEnabled = ref(false);

// 添加数据弹窗相关
const showAddDialog = ref(false);
const addDataForm = ref({
  name: '',
  rawText: '',
  headers: [] as string[],
  mapping: { name: '', values: [] as string[] }
});

const openAddDialog = () => {
  addDataForm.value = {
    name: '',
    rawText: '',
    headers: [],
    mapping: { name: '', values: [] }
  };
  showAddDialog.value = true;
};

/**
 * 解析表单中的 CSV 文本并更新字段选项
 */
const parseFormText = () => {
  const { headers } = tableManager.parseCSV(addDataForm.value.rawText);
  addDataForm.value.headers = headers;
  
  // 简单启发式映射：如果发现 District 字段，自动选上
  const nameField = headers.find(h => h.toLowerCase() === 'district' || h === '区域' || h === '名称');
  if (nameField) {
    addDataForm.value.mapping.name = nameField;
    // 自动选上所有看起来像年份或数值的字段
    addDataForm.value.mapping.values = headers.filter(h => 
      h !== nameField && (!isNaN(Number(h)) || h.toLowerCase().includes('value'))
    );
  }
};

/**
 * 加载模板数据到添加对话框
 */
const loadTemplateToDialog = () => {
  const text = tableManager.getTemplateCSVText();
  addDataForm.value.rawText = text;
  addDataForm.value.name = '示例 NDVI 数据.csv';
  parseFormText();
};

/**
 * 处理文件上传到对话框
 * @param {UploadFile} file - 上传的文件对象
 */
const handleUploadToDialog = (file: UploadFile) => {
  const reader = new FileReader();
  reader.onload = (e) => {
    const text = e.target?.result as string;
    addDataForm.value.rawText = text;
    addDataForm.value.name = file.name;
    parseFormText();
  };
  if (file.raw) {
    reader.readAsText(file.raw);
  }
  return false; // 阻止默认上传
};

/**
 * 加载示例模板并自动关联开封市图层
 */
const handleLoadTemplate = async () => {
  // 1. 确保地理服务已初始化 (先初始化，防止后续查找失败)
  if (!geoDataService.isInitialized()) {
    await geoDataService.initialize();
  }

  // 2. 加载数据
  tableManager.loadTemplateData();
  
  // 3. 自动加载开封市图层
  const kaifeng = geoDataService.getGeoDataItemByName('开封市');
  if (kaifeng) {
    await mapManager.handleRegionSelected(kaifeng, true);
  }

  // 4. 时间轴引导逻辑
  if (tableManager.yearRange.value > 1) {
    isTimeAxisEnabled.value = true;
    mapManager.timeConfig.value.yearIndex = 0;
  }

  mapManager.updateLayerStyles();
};

/**
 * 确认添加数据
 */
const confirmAddData = async () => {
  if (!addDataForm.value.name || !addDataForm.value.rawText) return;
  
  // 1. 将数据添加到 TableManager
  const id = tableManager.addCSV(addDataForm.value.name, addDataForm.value.rawText);
  if (addDataForm.value.mapping.name && addDataForm.value.mapping.values.length > 0) {
    tableManager.applyMapping(id, addDataForm.value.mapping.name, addDataForm.value.mapping.values);
  }

  // 2. 时间轴逻辑
  if (tableManager.yearRange.value > 1) {
    isTimeAxisEnabled.value = true;
    mapManager.timeConfig.value.yearIndex = 0;
  }

  showAddDialog.value = false;
  
  // 3. 尝试检索现有图层并更新样式（即“添加完毕后尝试检索图层”）
  mapManager.updateLayerStyles();
};

// 查看/编辑相关
const showEditor = ref(false);
const editingCSV = ref<{ id: string; name: string; text: string } | null>(null);

/**
 * 处理查看/编辑 CSV
 * @param {CSVDataItem} item - CSV 数据项
 */
const handleViewCSV = (item: CSVDataItem) => {
  editingCSV.value = {
    id: item.id,
    name: item.name,
    text: item.rawText
  };
  showEditor.value = true;
};

/**
 * 保存 CSV 编辑
 */
const saveCSVEdit = () => {
  if (editingCSV.value) {
    tableManager.updateCSV(editingCSV.value.id, editingCSV.value.text);
    mapManager.updateLayerStyles();
    showEditor.value = false;
    editingCSV.value = null;
  }
};

/**
 * 处理删除 CSV
 * @param {string} id - 数据 ID
 */
const handleRemoveCSV = (id: string) => {
  tableManager.removeCSV(id);
  mapManager.updateLayerStyles();
};

// 颜色转换逻辑
const rgbToHex = (r: number, g: number, b: number) => {
  return '#' + [r, g, b].map(x => x.toString(16).padStart(2, '0')).join('');
};

const hexToRgb = (hex: string) => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  if (!result) return { r: 0, g: 0, b: 0 };
  return {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  };
};

const startColorHex = computed({
  get: () => rgbToHex(mapManager.mapConfig.value.startRGB.r, mapManager.mapConfig.value.startRGB.g, mapManager.mapConfig.value.startRGB.b),
  set: (val) => { mapManager.mapConfig.value.startRGB = hexToRgb(val); }
});

const endColorHex = computed({
  get: () => rgbToHex(mapManager.mapConfig.value.endRGB.r, mapManager.mapConfig.value.endRGB.g, mapManager.mapConfig.value.endRGB.b),
  set: (val) => { mapManager.mapConfig.value.endRGB = hexToRgb(val); }
});

const gradientStyle = computed(() => ({
  background: `linear-gradient(to right, ${startColorHex.value}, ${endColorHex.value})`
}));

const stats = computed(() => {
  let max = { name: '无', value: 0 };
  let min = { name: '无', value: Infinity };
  
  tableManager.dataState.value.forEach((values, name) => {
    const val = values[mapManager.timeConfig.value.yearIndex] || 0;
    if (val > max.value) max = { name, value: val };
    if (val < min.value) min = { name, value: val };
  });

  if (min.value === Infinity) min.value = 0;
  return { max, min };
});

const updateChart = () => {
  if (!chartCanvas.value || chartType.value === 'table') return;
  if (chartInstance) chartInstance.destroy();

  let labels: string[] = [];
  let data: number[] = [];
  let label = '';
  const selectedName = mapManager.selectedDistrict.value;

  if (selectedName && tableManager.dataState.value.has(selectedName)) {
    const values = tableManager.dataState.value.get(selectedName)!;
    labels = values.map((_, i) => (mapManager.timeConfig.value.startYear + i).toString());
    data = values;
    label = `${selectedName} 趋势`;
  } else {
    labels = Array.from(tableManager.dataState.value.keys());
    data = labels.map(name => tableManager.dataState.value.get(name)?.[mapManager.timeConfig.value.yearIndex] || 0);
    label = `${mapManager.timeConfig.value.startYear + mapManager.timeConfig.value.yearIndex} 年数据`;
  }

  // 使用类型断言 as any 是因为 chart.js 的类型定义在 Vue 组件中可能存在兼容性问题
  // 或者是 chartType.value 的类型与 Chart.js 的 ChartTypeRegistry 键不完全匹配（尽管我们已经限制了 keys）
  chartInstance = new Chart(chartCanvas.value, {
    type: chartType.value as keyof ChartTypeRegistry,
    data: {
      labels,
      datasets: [{
        label,
        data,
        backgroundColor: chartType.value === 'line' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(16, 185, 129, 0.5)',
        borderColor: 'rgb(16, 185, 129)',
        borderWidth: 2,
        fill: chartType.value === 'line',
        tension: 0.4,
        pointRadius: selectedName ? 4 : 0,
        pointBackgroundColor: 'rgb(16, 185, 129)'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { 
        legend: { display: true, labels: { color: '#666', font: { size: 10 } } },
        tooltip: {
          mode: 'index',
          intersect: false,
          backgroundColor: 'rgba(255,255,255,0.9)',
          titleColor: '#333',
          bodyColor: '#666',
          borderColor: '#eee',
          borderWidth: 1,
          padding: 8
        }
      },
      scales: {
        y: { 
          beginAtZero: true, 
          grid: { color: '#f0f0f0' }, 
          ticks: { color: '#999', font: { size: 10 } } 
        },
        x: { 
          grid: { display: false }, 
          ticks: { color: '#999', font: { size: 10 }, maxRotation: 45 } 
        }
      }
    }
  });
};

watch([chartType, () => mapManager.timeConfig.value.yearIndex, () => tableManager.dataState.value, () => mapManager.selectedDistrict.value, isExpanded], () => {
  if (isExpanded.value && activeNames.value.includes('viz')) {
    setTimeout(updateChart, 350);
  }
}, { deep: true });

watch(() => mapManager.mapConfig.value, () => {
  mapManager.updateLayerStyles();
}, { deep: true });

const expandAndOpen = (name: string) => {
  isExpanded.value = true;
  activeNames.value = [name];
};

onMounted(() => {
  setTimeout(updateChart, 500);
});

onUnmounted(() => {
  if (chartInstance) chartInstance.destroy();
});

defineExpose({ isTimeAxisEnabled });
</script>

<style scoped>
@reference 'tailwindcss';

.custom-collapse {
  @apply border-none bg-transparent;
}

:deep(.el-collapse-item__header) {
  @apply border-b border-gray-100 h-11 px-2 transition-colors hover:bg-emerald-50/30;
}

:deep(.el-collapse-item__wrap) {
  @apply border-none bg-transparent;
}

:deep(.el-collapse-item__content) {
  @apply pb-4 pt-2;
}

:deep(.el-slider) {
  --el-slider-main-bg-color: #10b981;
}

:deep(.el-radio-button__inner) {
  @apply bg-gray-50 border-gray-200 text-gray-500;
}

:deep(.el-radio-button.is-active .el-radio-button__inner) {
  @apply bg-emerald-500 border-emerald-500 text-white shadow-none;
}

:deep(.el-upload-dragger) {
  @apply bg-gray-50/50 border-dashed border-gray-200 p-4 transition-colors;
}

:deep(.el-upload-dragger:hover) {
  @apply border-emerald-500 bg-emerald-50/20;
}

.custom-tabs :deep(.el-tabs__header) {
  @apply mb-2;
}

.custom-tabs :deep(.el-tabs__nav-wrap::after) {
  @apply bg-gray-100;
}

.custom-tabs :deep(.el-tabs__item) {
  @apply text-xs h-8 leading-8;
}

.custom-tabs :deep(.el-tabs__item.is-active) {
  @apply text-emerald-600 font-bold;
}

.custom-tabs :deep(.el-tabs__active-bar) {
  @apply bg-emerald-500;
}

.hide-scrollbar::-webkit-scrollbar {
  display: none;
}
.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
