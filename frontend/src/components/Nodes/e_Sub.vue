<!-- Nodes/AddNode.vue -->
<script setup lang="ts">
import { Handle, Position,type NodeProps } from '@vue-flow/core'

const props = defineProps<NodeProps>()

</script>

<template>
  <div class="add-node">
    <div class="node-header">
      <span class="node-type">减法</span>
      <span class="node-id">{{ 'sub_'+id.slice(12, 16) }}</span>
    </div>
    
    <div class="node-content">
      <div class="operation">
        <div class="operation-symbol">-{{ props.data.value }}</div>
        <div class="operation-desc">输入值减{{ props.data.value }}</div>
      </div>
      
      <div class="node-info">
        <div class="info-item" v-if="data.input">
          <span class="info-label">输入:</span>
          <span class="info-value">{{ data.input }}</span>
        </div>
        <div class="info-item" v-if="data.output">
          <span class="info-label">输出:</span>
          <span class="info-value">{{ data.output }}</span>
        </div>
      </div>
    </div>
    
    <!-- 输入连接点（左侧） -->
    <Handle 
      type="target" 
      :position="Position.Left" 
      class="node-handle node-handle-target"
    />
    
    <!-- 输出连接点（右侧） -->
    <Handle 
      type="source" 
      :position="Position.Right" 
      class="node-handle node-handle-source"
    />
  </div>
</template>

<style scoped>
.add-node {
  min-width: 160px;
  background: white;
  border: 2px solid #2196F3;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 3px 10px rgba(33, 150, 243, 0.1);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  user-select: none;
  position: relative;
}

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

.node-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.operation {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: #E3F2FD;
  border-radius: 6px;
}

.operation-symbol {
  font-size: 20px;
  font-weight: bold;
  color: #1976D2;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 50%;
}

.operation-desc {
  font-size: 13px;
  color: #424242;
  flex: 1;
}

.node-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  padding: 4px 8px;
  background: #F5F5F5;
  border-radius: 4px;
}

.info-label {
  color: #616161;
  font-weight: 500;
}

.info-value {
  color: #424242;
  font-weight: 600;
}

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