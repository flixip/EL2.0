<!-- Nodes/HTTPNode.vue -->
<script setup lang="ts">
import { Handle, Position, type NodeProps } from '@vue-flow/core'
import { ref, computed, onMounted } from 'vue'

// 继承NodeProps并扩展data类型，定义HTTP节点需要的字段
interface HTTPNodeData {
  imageUrl: string // 图片请求URL
  status: 'idle' | 'loading' | 'success' | 'error' // 请求状态
  errorMsg?: string // 错误信息
  imgWidth?: number // 图片宽度
  imgHeight?: number // 图片高度
}

// 定义Props，指定data的类型为HTTPNodeData
const props = defineProps<NodeProps<HTTPNodeData>>()

// 响应式状态：控制图片加载（基于props.data，保留响应式）
const imgLoading = ref(props.data.status === 'loading')
const imgError = ref(false)


// 核心方法：请求图片（处理加载/成功/失败状态）
const fetchImage = () => {
  if (!props.data.imageUrl) {
    props.data.status = 'error'
    props.data.errorMsg = '图片URL不能为空'
    return
  }

  // 更新状态为加载中
  props.data.status = 'loading'
  imgLoading.value = true
  imgError.value = false

  // 创建图片对象请求资源
  const img = new Image()
  img.onload = () => {
    // 成功：记录图片尺寸，更新状态
    props.data.status = 'success'
    props.data.imgWidth = img.width
    props.data.imgHeight = img.height
    imgLoading.value = false
  }
  img.onerror = (err) => {
    // 失败：记录错误信息
    props.data.status = 'error'
    props.data.errorMsg = '图片加载失败：URL无效或网络错误'
    imgLoading.value = false
    imgError.value = true
    console.error('图片加载失败：', err)
  }
  img.src = props.data.imageUrl
}

// 组件挂载时：如果已有URL且状态为idle，自动请求（可选）
onMounted(() => {
  if (props.data.imageUrl && props.data.status === 'idle') {
    fetchImage()
  }
})
</script>

<template>
  <div class="http-node">
    <!-- 节点头部：和加法节点结构一致 -->
    <div class="node-header">
      <span class="node-type">HTTP图片请求节点</span>
      <span class="node-id">{{ props.id }}</span>
    </div>

    <!-- 节点内容区：适配图片请求逻辑 -->
    <div class="node-content">
      <!-- URL展示+请求按钮区域（替代加法节点的运算区） -->
      <div class="request-area">
        <div class="url-display">
          <span class="url-label">图片URL：</span>
          <span class="url-value">{{ props.data.imageUrl || '未设置URL' }}</span>
        </div>
        <button 
          class="request-btn" 
          @click="fetchImage"
          :disabled="props.data.status === 'loading'"
        >
          {{ props.data.status === 'loading' ? '加载中...' : '请求图片' }}
        </button>
      </div>

      <!-- 状态提示区域 -->
      <div class="status-area" v-if="props.data.status !== 'idle'">
        <span 
          class="status-tag" 
          :class="{
            loading: props.data.status === 'loading',
            success: props.data.status === 'success',
            error: props.data.status === 'error'
          }"
        >
          {{ 
             props.data.status === 'loading' ? '加载中' : 
             props.data.status === 'success' ? '加载成功' : '加载失败' 
          }}
        </span>
        <span class="error-msg" v-if="props.data.status === 'error'">
          {{ props.data.errorMsg || '图片加载失败' }}
        </span>
      </div>

      <!-- 图片展示区域（核心） -->
      <div class="image-preview">
        <div v-if="props.data.status === 'loading'" class="loading-placeholder">
          <span class="loading-text">图片加载中...</span>
        </div>
        <div v-else-if="props.data.status === 'success'" class="image-container">
          <img 
            :src="props.data.imageUrl" 
            alt="请求的图片"
            class="preview-img"
            :style="{ maxWidth: '100%', maxHeight: '120px' }"
          >
          <div class="img-info">
            尺寸：{{ props.data.imgWidth }} × {{ props.data.imgHeight }}
          </div>
        </div>
        <div v-else-if="props.data.status === 'error'" class="error-placeholder">
          <span class="error-icon">⚠️</span>
          <span class="error-text">{{ props.data.errorMsg || '图片加载失败' }}</span>
        </div>
        <div v-else class="empty-placeholder">
          <span class="empty-text">点击「请求图片」加载URL</span>
        </div>
      </div>
    </div>

    <!-- 输入连接点（左侧）：和加法节点一致 -->
    <Handle 
      type="target" 
      :position="Position.Left" 
      class="node-handle node-handle-target"
    />
    
    <!-- 输出连接点（右侧）：和加法节点一致 -->
    <Handle 
      type="source" 
      :position="Position.Right" 
      class="node-handle node-handle-source"
    />
  </div>
</template>

<style scoped>
/* 基础样式：继承加法节点的布局/配色，仅修改内容区适配图片 */
.http-node {
  min-width: 220px; /* 略宽于加法节点，适配图片展示 */
  max-height: 440px;
  max-width: 300px;
  background: white;
  border: 2px solid #2196F3; /* 和加法节点同主色 */
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 3px 10px rgba(33, 150, 243, 0.1);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  user-select: none;
  position: relative;
}

/* 节点头部：完全复用加法节点样式 */
.node-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e0e0e0;
}

.node-type {
  background: #2196F3;
  color: white;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.node-id {
  font-size: 10px;
  color: #757575;
}

/* 内容区：调整布局适配图片请求逻辑 */
.node-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* 请求区域：替代加法节点的运算区，保持风格一致 */
.request-area {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px;
  background: #E3F2FD; /* 和加法节点运算区同背景色 */
  border-radius: 6px;
}

.url-display {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  font-size: 12px;
}

.url-label {
  color: #1976D2;
  font-weight: 500;
}

.url-value {
  color: #424242;
  flex: 1;
  word-break: break-all;
}

.request-btn {
  background: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.request-btn:disabled {
  background: #90CAF9;
  cursor: not-allowed;
}

/* 状态区域 */
.status-area {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 11px;
}

.status-tag {
  padding: 2px 6px;
  border-radius: 3px;
  display: inline-block;
}

.status-tag.loading {
  background: #FFF3E0;
  color: #FF9800;
}

.status-tag.success {
  background: #E8F5E9;
  color: #4CAF50;
}

.status-tag.error {
  background: #FFEBEE;
  color: #F44336;
}

.error-msg {
  color: #F44336;
  font-size: 10px;
}

/* 图片预览区域 */
.image-preview {
  padding: 8px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  min-height: 100px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.loading-placeholder, .error-placeholder, .empty-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: #757575;
  font-size: 12px;
}

.error-icon {
  font-size: 20px;
}

.img-info {
  margin-top: 6px;
  font-size: 10px;
  color: #757575;
}

/* 连接点样式：完全复用加法节点 */
.node-handle {
  width: 10px;
  height: 10px;
  background: white;
  border: 2px solid #2196F3;
}

.node-handle-target {
  left: -5px;
  top: 50%;
}

.node-handle-source {
  right: -5px;
  top: 50%;
}
</style>