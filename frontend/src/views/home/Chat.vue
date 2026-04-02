<template>
  <div class="chat-container">
    <!-- 聊天头部 -->
    <div class="chat-header">
      <h2 class="text-xl font-bold text-slate-700">AI 聊天助手</h2>
      <div class="chat-header-actions">
        <el-button size="small" type="primary" plain @click="clearChat">清空对话</el-button>
      </div>
    </div>
    
    <!-- 聊天内容区域 -->
    <div class="chat-messages" ref="messagesContainer">
      <!-- 系统消息 -->
      <div class="system-message">
        <p>您好！我是AI助手，有什么可以帮您的吗？</p>
      </div>
      
      <!-- 对话消息 -->
      <div 
        v-for="(message, index) in messages" 
        :key="index"
        :class="['message-item', message.isUser ? 'user-message' : 'ai-message']"
      >
        <div class="message-avatar">
          <span v-if="message.isUser">👤</span>
          <span v-else>🤖</span>
        </div>
        <div class="message-bubble">
          <p v-if="message.isUser">{{ message.content }}</p>
          <div v-else class="markdown-content" v-html="marked(message.content)">
          </div>
          <div class="message-time">{{ message.timestamp }}</div>
        </div>
      </div>
      
      <!-- 加载状态 -->
      
      <div v-if="isLoading" class="loading-message">
        <div class="loading-spinner"></div>
        <p>AI正在思考...</p>
      </div>
      
    <div v-show="imglayers.length" class="message-bubble py-20 w-[80%]">
      <div id="map-container" class="w-full h-80 rounded-xl shadow-md"></div>
    </div>
    </div>
    
    <!-- 聊天输入区域 -->
    <div class="chat-input-area">
      <el-input
        v-model="inputMessage"
        type="textarea"
        :rows="2"
        placeholder="请输入您的问题..."
        @keyup.enter.exact="sendMessage"
        resize="none"
      />
      <el-button 
        type="primary" 
        circle 
        :disabled="!inputMessage.trim() || isLoading"
        @click="sendMessage"
      >
        <el-icon><Promotion /></el-icon>
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { Promotion } from '@element-plus/icons-vue'
import { aiChat } from '@/apiService/aichatApi'
import { marked } from 'marked'
import MapManager from "@/tools/mapManager"

// 消息类型定义
interface Message {
  content: string
  isUser: boolean
  timestamp: string
}

// 响应式状态
const inputMessage = ref('')
const messages = ref<Message[]>([])
const isLoading = ref(false)
const messagesContainer = ref<HTMLElement>()
const imglayers = ref<string[]>([])

const addUserMessage = (content: string) => {
  const userMessage: Message = {
    content: content,
    isUser: true,
    timestamp: getCurrentTime()
  }
  messages.value.push(userMessage)
}

const addAiMessage = (content: string) => {
  const aiMessage: Message = {
    content: content,
    isUser: false,
    timestamp: getCurrentTime()
  }
  messages.value.push(aiMessage)
}

const extractMapUrls = (content: string): string[] => {
  const mapUrlPattern = /https?:\/\/[^\s<>"{}]+\/tiles\/\{z\}\/\{x\}\/\{y\}/g
  const matches = content.match(mapUrlPattern)
  return matches || []
}

const addLayer = (mapurl: string | Array<string>,pos:[string,string | undefined] | undefined)=> {
  
  if (Array.isArray(mapurl)) {
    mapurl.forEach(url => {
      MapManager.getInstance().addImageLayer(url)
      imglayers.value.push(url)
    })
  } else if (typeof mapurl === 'string') {
    MapManager.getInstance().addImageLayer(mapurl)
    imglayers.value.push(mapurl)
  }
  if (pos) {
    MapManager.getInstance()
  }
}

const clearLayers = () => {
  imglayers.value.forEach(url => {
    MapManager.getInstance().clearImageLayers()
  })
  imglayers.value = []
}


const query = (question:string) => {
  


}
// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return
  
  // 添加用户消息
  const userMessage: Message = {
    content: inputMessage.value.trim(),
    isUser: true,
    timestamp: getCurrentTime()
  }
  messages.value.push(userMessage)
  
  // 清空输入框
  inputMessage.value = ''
  
  // 滚动到底部
  scrollToBottom()
  
  // 调用aiChat服务获取AI回复
  isLoading.value = true
  
  // 添加一个空的AI消息
  const aiMessageIndex = messages.value.length
  messages.value.push({
    content: '',
    isUser: false,
    timestamp: getCurrentTime()
  })
  
  try {
    const response = await aiChat({ query: userMessage.content })
    
    // 更新AI消息内容
    const aiMessage = messages.value[aiMessageIndex]
    if (aiMessage) {
      aiMessage.content = response.answer
      aiMessage.timestamp = getCurrentTime()
      
      // 检测并提取mapurl
      const mapUrls = extractMapUrls(response.answer)
      if (mapUrls.length > 0) {
        addLayer(mapUrls, undefined)
      }
    }
  } catch (error) {
    // 更新错误消息
    const aiMessage = messages.value[aiMessageIndex]
    if (aiMessage) {
      aiMessage.content = '抱歉，我暂时无法回答您的问题。请稍后再试。'
    }
    console.error('AI chat error:', error)
  } finally {
    // 关闭加载状态
    isLoading.value = false
    
    // 滚动到底部
    scrollToBottom()
  }
}

// 清空对话
const clearChat = () => {
  messages.value = []
}

// 获取当前时间
const getCurrentTime = () => {
  const now = new Date()
  return now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 监听消息变化，自动滚动到底部
watch(messages, () => {
  scrollToBottom()
}, { deep: true })



onMounted(() => {
  MapManager.getInstance().initMap('map-container')
  MapManager.getInstance().addSreenFullCtl()

}) 

onUnmounted(() => {
  MapManager.getInstance().destroy()
})




</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f7fa;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background-color: #fff;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.chat-messages {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.system-message {
  align-self: center;
  background-color: #f0f9ff;
  padding: 8px 16px;
  border-radius: 16px;
  font-size: 14px;
  color: #333;
  max-width: 80%;
  text-align: center;
}

.message-item {
  display: flex;
  gap: 12px;
  max-width: 80%;
}

.user-message {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.ai-message {
  align-self: flex-start;
}

.message-avatar {
  font-size: 24px;
  flex-shrink: 0;
}

.message-bubble {
  background-color: #fff;
  padding: 12px 16px;
  border-radius: 16px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  position: relative;
}

.user-message .message-bubble {
  background-color: #e6f7ff;
}

.message-time {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  text-align: right;
}

.loading-message {
  align-self: flex-start;
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: #fff;
  padding: 12px 16px;
  border-radius: 16px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #409eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.chat-input-area {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  background-color: #fff;
  border-top: 1px solid #e4e7ed;
  box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.05);
}

.chat-input-area :deep(.el-textarea) {
  flex: 1;
  border-radius: 8px;
}

.chat-input-area :deep(.el-textarea__inner) {
  border-radius: 8px;
  resize: none;
}

.chat-input-area .el-button {
  flex-shrink: 0;
  align-self: flex-end;
  margin-bottom: 4px;
}

/* Markdown样式 */
:deep(.markdown-content) {
  line-height: 1.6;
}

:deep(.markdown-content h1),
:deep(.markdown-content h2),
:deep(.markdown-content h3),
:deep(.markdown-content h4),
:deep(.markdown-content h5),
:deep(.markdown-content h6) {
  margin: 16px 0 8px 0;
  font-weight: 600;
}

:deep(.markdown-content h1) {
  font-size: 1.5em;
}

:deep(.markdown-content h2) {
  font-size: 1.3em;
}

:deep(.markdown-content h3) {
  font-size: 1.1em;
}

:deep(.markdown-content p) {
  margin: 8px 0;
}

:deep(.markdown-content ul),
:deep(.markdown-content ol) {
  margin: 8px 0;
  padding-left: 24px;
}

:deep(.markdown-content li) {
  margin: 4px 0;
}

:deep(.markdown-content code) {
  background-color: #f0f0f0;
  padding: 2px 4px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.9em;
}

:deep(.markdown-content pre) {
  background-color: #f0f0f0;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 8px 0;
}

:deep(.markdown-content pre code) {
  background-color: transparent;
  padding: 0;
}

:deep(.markdown-content a) {
  color: #409eff;
  text-decoration: none;
}

:deep(.markdown-content a:hover) {
  text-decoration: underline;
}

:deep(.markdown-content blockquote) {
  border-left: 4px solid #409eff;
  padding-left: 12px;
  margin: 8px 0;
  color: #666;
}
</style>