<template>
  <div class="h-full flex ">
    <!-- 标签页 -->
    <el-tabs v-model="activeTab"
    type="border-card"
    tab-position="right"
    style="width: 100%;"
    >
      <el-tab-pane
      class="" 
      name="form" >
        <template #label>
          <el-icon><Management /></el-icon>
      </template>
      <el-icon class="cursor-pointer float-right" @click="isCollapse = !isCollapse" v-if="isCollapse"><Expand /></el-icon>
          <el-icon class="cursor-pointer float-right" @click="isCollapse = !isCollapse" v-else><Fold /></el-icon>
              <FormComponent v-show="!isCollapse" />
      </el-tab-pane>
      
      <el-tab-pane  name="results">
        <template #label>
          <el-icon><Download /></el-icon>
      </template>
        <div class="h-full flex">
          <!-- 结果列表 -->
          <ResultsList v-if="!showDownloadPanel" @show-download="showDownloadPanel = true" />
          
          <!-- 下载设置面板 -->
          <DownloadPanel v-else @back="showDownloadPanel = false" />
        </div>
      </el-tab-pane>

    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { Download, Management, Expand, Fold } from '@element-plus/icons-vue';
import FormComponent from './FormComponent.vue';
import ResultsList from './ResultsList.vue';
import DownloadPanel from './DownloadPanel.vue';

// 标签页状态
const activeTab = ref('form');
const showDownloadPanel = ref(false);

const isCollapse = ref(true);

</script>

