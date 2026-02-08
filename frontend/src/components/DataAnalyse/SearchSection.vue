<template>
  <div class="search-section">
    <el-input
      v-model="localSearchQuery"
      placeholder="搜索地点以添加区划矢量图层"
      prefix-icon="Search"
      @input="handleSearchInput"
    >
      <template #suffix>
        <el-icon v-if="loading" class="is-loading"><Loading /></el-icon>
      </template>
    </el-input>
    
    <!-- 搜索检索状态提示 -->
    <div v-if="loading" class="mt-2 text-center text-[10px] text-emerald-500 flex items-center justify-center gap-1">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>正在检索地理数据...</span>
    </div>
    
    <!-- 搜索结果 -->
    <div v-if="searchResults.length > 0" class="search-results">
      <el-scrollbar>
        <div
          v-for="result in searchResults"
          :key="result.id"
          class="search-result-item"
          @click="handleAddGeoData(result)"
        >
          <div class="result-info">
            <span class="result-name">{{ result.name }}</span>
            <span class="result-type">{{ result.type === 'province' ? '省份' : '城市' }}</span>
          </div>
          <el-button type="primary" size="small">添加</el-button>
        </div>
      </el-scrollbar>
    </div>
    
    <!-- 搜索无结果提示 -->
    <div v-else-if="localSearchQuery.length > 0" class="empty-result">
      <el-empty description="未找到匹配的地点" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { Search, Loading } from '@element-plus/icons-vue';

import geoDataService from '@/services/GeoDataService';
import MapManager from '@/tools/mapManager';

const mapManager = MapManager.getInstance();
const selectedRegionList = mapManager.selectedRegionList;

// 本地状态
const localSearchQuery = ref('');
const searchResults = ref([]);
const loading = ref(false);

// 搜索输入防抖
let searchTimeout = null;

// 搜索输入处理
const handleSearchInput = async () => {
  if (localSearchQuery.value.length < 1) {
    searchResults.value = [];
    return;
  }

  if (searchTimeout) clearTimeout(searchTimeout);

  searchTimeout = setTimeout(async () => {
    try {
      loading.value = true;
      await geoDataService.initialize();
      const results = geoDataService.search(localSearchQuery.value);
      searchResults.value = results;
    } catch (error) {
      console.error('Search error:', error);
     
    } finally {
      loading.value = false;
    }
  }, 300);
};

// 处理添加地理数据
const handleAddGeoData = async (data) => {
  try {
    loading.value = true;
    
    // 检查是否已添加
    if (selectedRegionList.value.some(item => item.name === data.name)) {
      throw new Error('该数据已添加');
    }
    
    await geoDataService.initialize();
    
    // 使用 MapManager 处理区域选择
    await mapManager.handleRegionSelected(data, true, {
      color: '#3388ff',
      weight: 2,
      opacity: 0.8,
      fillColor: '#3388ff',
      fillOpacity: 0.3
    });
    
    // 清空搜索
    localSearchQuery.value = '';
    searchResults.value = [];
 
  } catch (error) {
    console.error('Add geo data error:', error);
   
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
@reference 'tailwindcss';

.search-section {
  @apply mb-6; /* Layout */
}

.search-results {
  @apply mt-2 max-h-50; /* Layout */
  @apply border border-gray-200 rounded overflow-hidden; /* Aesthetics */
}

.search-result-item {
  @apply flex justify-between items-center p-3; /* Layout */
  @apply cursor-pointer border-b border-gray-50 transition-all hover:bg-gray-50 hover:translate-x-1; /* Aesthetics */
}

.result-info {
  @apply flex flex-col; /* Layout */
}

.result-name {
  @apply text-sm font-medium text-gray-800; /* Aesthetics */
}

.result-type {
  @apply mt-0.5; /* Layout */
  @apply text-xs text-gray-400; /* Aesthetics */
}

.empty-result {
  @apply p-6; /* Layout */
  @apply text-center; /* Aesthetics */
}
</style>
