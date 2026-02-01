<template>
  <div class="w-full">
   
    <hr class="mb-4 border border-gray-300">
    <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px">
      <el-form-item 
      label="研究区"
      label-position="left"
      required>
        <div class="flex gap-4">
          <el-radio-group v-model="areaType" @change="handleAreaTypeChange" style="margin-right: 20px">
            <el-radio value="region">行政区划</el-radio>
            <el-radio value="custom">自定义研究区</el-radio>
          </el-radio-group>
        </div>
        
        <div v-if="areaType === 'region'" style="margin-top: 12px;width: 100%">
          <el-cascader
            v-model="regionData"
            :options="regionOptions"
            :props="cascaderProps"
            placeholder="请选择省/市"
            style="width: 100%"
            :loading="loading"
          />
        </div>
        <div v-else-if="areaType === 'custom'" style="margin-top: 12px;width: 100%">
          <el-input
            v-model="formData.province"
            placeholder="自定义研究区"
            style="width: 100%"
            readonly
            value="roi"
          />
        </div>
      </el-form-item>
       
        <el-form-item
      label="日期范围"
       label-position="left"
       required>
        <el-date-picker
          v-model="formData.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          style="width: 100%"
          required
        />
      </el-form-item>

      <el-form-item 
      label="最大云量(%)"
      label-position="left">
        <el-input-number
          v-model="formData.cloud"
          :min="0"
          :max="100"
          :step="5"
          :default-value="20"
          style="width: 100%"
        />
      </el-form-item>

      

    </el-form>
     <el-button class="float-right" type="primary" @click="handleNext" style="width: 30%">
          <el-icon><ArrowRight /></el-icon> 下一步
     </el-button>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue';
import { Download , ArrowRight } from '@element-plus/icons-vue';
import geoDataService from '@/services/GeoDataService';
import MapManager from '@/tools/mapManager';

const emit = defineEmits(['next-step']);
const formRef = ref(null);

// 表单数据
const formData = reactive({
  dateRange: null,
  cloud: 20,
  province: ''
});

// 区域选择类型
const areaType = ref('region');

// 级联选择器数据
const regionData = ref([]);
const regionOptions = ref([]);
const loading = ref(false);

// 级联选择器配置
const cascaderProps = {
  value: 'value',
  label: 'label',
  children: 'children',
  checkStrictly: true
};

// 验证规则
const rules = {
  dateRange: [
    {
      required: true,
      message: '请选择日期范围',
      trigger: 'change'
    }
  ],
  province: [
    {
      required: true,
      message: '请选择研究区',
      trigger: 'change'
    }
  ]
};

// 处理区域类型切换
const handleAreaTypeChange = () => {
  if (areaType.value === 'custom') {
    formData.province = 'roi';
    regionData.value = [];
  } else {
    formData.province = '';
  }
};

// 加载地理数据
const loadGeoData = async () => {
  try {
    loading.value = true;
    
    // 初始化地理数据服务
    await geoDataService.initialize();
    
    // 获取省份数据
    const provinces = geoDataService.getProvinces();
    
    // 构建级联选择器选项
    const options = provinces.map(province => {
      // 获取该省份的城市
      const cities = geoDataService.getCitiesByProvince(province.name);
      
      return {
        value: province.name,
        label: province.name,
        children: cities.map(city => ({
          value: city.name,
          label: city.name
        }))
      };
    });
    
    regionOptions.value = options;
  } catch (error) {
    console.error('Failed to load geo data:', error);
  } finally {
    loading.value = false;
  }
};

// 监听区域数据变化
const updateProvinceData = () => {
  if (regionData.value && regionData.value.length > 0) {
    // 如果选择了城市，使用城市名称；否则使用省份名称
    formData.province = regionData.value[regionData.value.length - 1];
  } else {
    formData.province = '';
  }
};

// 监听区域数据变化
watch(regionData, () => {
  updateProvinceData();
}, { deep: true });

// 处理下一步
const handleNext = async () => {
  if (formRef.value) {
    formRef.value.validate((valid) => {
      if (valid) {
        // 保存表单数据到全局状态或本地存储
        localStorage.setItem('imgGetStep1', JSON.stringify(formData));
        console.log(localStorage.getItem('imgGetStep1'));
        
        // 准备区域选择数据
        let regionSelectionData = null;
        if (areaType.value === 'region' && regionData.value.length > 0) {
          regionSelectionData = {
            type: 'region',
            data: regionData.value,
            province: formData.province
          };
        } else if (areaType.value === 'custom') {
          regionSelectionData = {
            type: 'custom',
            data: null,
            province: formData.province
          };
        }
        
        // 直接使用MapManager单例处理区域选择
        try {
          const mapManager = MapManager.getInstance();
          if (mapManager && regionSelectionData) {
            // 直接调用MapManager的handleRegionSelected方法
            mapManager.handleRegionSelected(regionSelectionData);
            console.log('直接通过MapManager处理区域选择');
          }
        } catch (error) {
          console.error('Error accessing map manager:', error);
        }
        
        emit('next-step');
      } else {
        console.log('表单验证失败');
      }
    });
  }
};

// 生命周期钩子
onMounted(async () => {
  await loadGeoData();
});
</script>
