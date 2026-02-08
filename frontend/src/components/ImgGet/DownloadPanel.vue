<template>
  <div class="download-panel">
    <div class="row">
      <!-- 左侧：影像和波段列表 -->
      <div class="col">
        <div class="mb-3">
          <h6>可下载影像</h6>
          <div class="list-group image-scroll">
            <div 
              v-for="(image, index) in availableImages" 
              :key="index"
              class="list-group-item"
            >
              <div class="form-check">
                <input 
                  class="form-check-input" 
                  type="checkbox" 
                  :id="`image-${index}`"
                  :value="image.id"
                  v-model="selectedImages"
                >
                <label class="form-check-label" :for="`image-${index}`">
                  {{ image.name }}
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="mb-3">
          <h6>可下载波段</h6>
          <div class="list-group band-scroll">
            <div 
              v-for="(band, index) in availableBands" 
              :key="index"
              class="list-group-item"
            >
              <div class="form-check">
                <input 
                  class="form-check-input" 
                  type="checkbox" 
                  :id="`band-${index}`"
                  :value="band.id"
                  v-model="selectedBands"
                >
                <label class="form-check-label" :for="`band-${index}`">
                  {{ band.name }}
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：高级设置 -->
      <div class="col">
        <div class="card">
          <div class="card-body">
            <h6>高级设置</h6>
            
            <div class="form-check mb-3">
              <input 
                class="form-check-input" 
                type="checkbox" 
                id="exportMask"
                v-model="useMask"
              >
              <label class="form-check-label" for="exportMask">
                区域掩膜
              </label>
              <div class="alert alert-warning alert-tip" v-if="useMask">
                勾选此项将按选择的区域进行影像裁剪，可能出现影像残缺的情况
              </div>
            </div>

            <div class="form-check mb-3">
              <input 
                class="form-check-input" 
                type="checkbox" 
                id="medianComposite"
                v-model="useComposite"
              >
              <label class="form-check-label" for="medianComposite">
                中值合成
              </label>
              <div class="alert alert-warning alert-tip" v-if="useComposite">
                勾选此项将把选中图像进行中值合成，最后只会下载一张融合图像
              </div>
            </div>

            <div class="mb-3">
              <label for="resolution" class="form-label">分辨率（米）</label>
              <el-input-number
                v-model="resolution"
                :min="10"
                :max="1000"
                :step="10"
                style="width: 100%"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="download-actions">
      <el-button @click="$emit('back')">
        <el-icon><ArrowLeft /></el-icon> 返回结果
      </el-button>
      <el-button type="primary" @click="startDownload">
        提交下载请求
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { ArrowLeft } from '@element-plus/icons-vue';

const emit = defineEmits(['back']);

// 下载设置
const selectedImages = ref([]);
const selectedBands = ref([]);
const useMask = ref(false);
const useComposite = ref(false);
const resolution = ref(30);

// 模拟数据
const availableImages = ref([
  { id: 1, name: 'Landsat-8_20230101_123456' },
  { id: 2, name: 'Landsat-8_20230201_234567' },
  { id: 3, name: 'Sentinel-2_20230115_345678' },
  { id: 4, name: 'Sentinel-2_20230215_456789' }
]);

const availableBands = ref([
  { id: 'B1', name: 'B1 (蓝)' },
  { id: 'B2', name: 'B2 (绿)' },
  { id: 'B3', name: 'B3 (红)' },
  { id: 'B4', name: 'B4 (近红外)' },
  { id: 'B5', name: 'B5 (短波红外1)' },
  { id: 'B6', name: 'B6 (短波红外2)' }
]);

// 开始下载
const startDownload = () => {
  const downloadData = {
    selectedImages: selectedImages.value,
    selectedBands: selectedBands.value,
    useMask: useMask.value,
    useComposite: useComposite.value,
    resolution: resolution.value
  };
  
  console.log('下载请求:', downloadData);
  alert(`区域掩膜: ${useMask.value}, 中值合成: ${useComposite.value}\n分辨率: ${resolution.value} 米\n选择了 ${selectedImages.value.length} 景影像和 ${selectedBands.value.length} 个波段`);
};
</script>

<style scoped>
.download-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex: 1;
}

.col {
  flex: 1;
}

.image-scroll,
.band-scroll {
  max-height: 250px;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

.list-group-item {
  padding: 8px 12px;
  border-bottom: 1px solid #e0e0e0;
}

.list-group-item:last-child {
  border-bottom: none;
}

.card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.card-body {
  padding: 15px;
}

.form-check {
  margin-bottom: 15px;
}

.alert-tip {
  margin-top: 5px;
  font-size: 12px;
  padding: 8px;
  border-radius: 4px;
}

.download-actions {
  display: flex;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

/* 自定义滚动条 */
.image-scroll::-webkit-scrollbar,
.band-scroll::-webkit-scrollbar {
  width: 6px;
}

.image-scroll::-webkit-scrollbar-track,
.band-scroll::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.image-scroll::-webkit-scrollbar-thumb,
.band-scroll::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.image-scroll::-webkit-scrollbar-thumb:hover,
.band-scroll::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .row {
    flex-direction: column;
  }
}
</style>