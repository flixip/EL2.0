<!-- 父组件 -->
<template>
  <div class="relative h-screen">
    <!-- Vue Flow 画布 -->
    <VueFlow
      v-model:nodes="nodes"
      v-model:edges="edges"
      id="my-flow"
      @connect="nodeManager.addEdge($event)"
      :node-types="nodeTypes"
    >
      <Background :gap="15" />
    </VueFlow>
    <!-- 节点面板 -->
    <NodePanel 
    @toggleDebugPanel="isDebugPanelOpen = !isDebugPanelOpen"
    />
  
  </div>
</template>

<script setup lang="ts">
import { provide, ref } from 'vue'
import { VueFlow, useVueFlow, type Node, type Edge } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import NodePanel from './NodePanel.vue'
import { nodeTypes,NodeManager } from '../tools/nodeManager'

const isDebugPanelOpen = ref(false)

// Vue Flow 实例
const flow = useVueFlow('my-flow')
const nodes = ref<Node[]>([])
const edges = ref<Edge[]>([])


const nodeManager = new NodeManager(flow)

provide('node_manager', nodeManager)

</script>


