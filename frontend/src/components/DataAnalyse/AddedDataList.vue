<template>
  <div class="flex-1 overflow-hidden">
    <h3 class="text-lg font-semibold mb-3 px-3">已添加区划</h3>
    <el-scrollbar>
      <div v-if="selectedRegionList.length > 0">
        <div
          v-for="data in selectedRegionList"
          :key="data.id"
          class="flex justify-between items-center p-3 border-b border-gray-50 transition-all hover:bg-gray-50;"
        >
          <div class="flex flex-col">
            <span class="text-sm font-medium text-gray-800">{{ data.name }}</span>
            <span class="text-xs text-gray-400 mt-0.5">{{ data.type === 'province' ? '省份' : '城市' }}</span>
          </div>
          <el-button type="danger" size="small" @click="handleRemoveGeoData(data.id)">
            删除
          </el-button>
        </div>
      </div>
      <!-- 无添加数据提示 -->
      <div v-else class="py-12 px-6 text-center">
        <el-empty description="暂无添加的数据" />
      </div>
    </el-scrollbar>
  </div>
</template>

<script setup lang="ts">
import MapManager from '@/tools/mapManager';

const mapManager = MapManager.getInstance();
// 直接使用 MapManager 暴露的响应式计算属性
const selectedRegionList = mapManager.selectedRegionList;

/**
 * 处理删除地理数据
 * @param {string | number} id - 区域 ID
 */
const handleRemoveGeoData = (id: string | number) => {
  try {
    mapManager.removeRegion(id);
    console.log('删除数据成功');
  } catch (error) {
    console.error('Error removing geo data:', error);
  }
};
</script>

