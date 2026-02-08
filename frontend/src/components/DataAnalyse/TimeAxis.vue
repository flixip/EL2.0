<template>
  <transition name="fade-slide">
    <div 
      v-if="visible"
      class="fixed bottom-8 left-1/2 z-1000 w-[60%] -translate-x-1/2 rounded-2xl border border-white/10 bg-gray-900/80 p-4 shadow-2xl backdrop-blur-xl"
    >
      <div class="flex items-center gap-4">
        <!-- 播放控制 -->
        <button 
          @click="togglePlay"
          class="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-500 text-white shadow-lg hover:bg-emerald-600 transition-colors"
        >
          <el-icon :size="20">
            <VideoPause v-if="timeConfig.isPlaying" />
            <VideoPlay v-else />
          </el-icon>
        </button>

        <!-- 时间轴轨道 -->
        <div class="relative flex-1 px-4">
          <div 
            class="relative h-2 rounded-full bg-white/10 cursor-pointer"
            @mousedown="handleTrackMouseDown"
            ref="trackRef"
          >
            <!-- 进度条 -->
            <div 
              class="absolute h-full rounded-full bg-emerald-500"
              :class="{ 'transition-all duration-300': !isDragging }"
              :style="{ width: isDragging ? `${tempProgress * 100}%` : `${progress}%` }"
            ></div>
            
            <!-- 滑块 -->
            <div 
              @mousedown.stop="startDrag"
              class="absolute top-1/2 -translate-y-1/2 translate-x-[-50%] h-4 w-4 rounded-full border-2 border-emerald-500 bg-white shadow-md cursor-pointer hover:scale-125 z-10"
              :class="{ 'transition-all duration-300': !isDragging, 'transition-transform': true }"
              :style="{ left: isDragging ? `${tempProgress * 100}%` : `${progress}%` }"
            ></div>

            <!-- 刻度点 -->
            <div 
              v-for="index in timeConfig.yearRange" 
              :key="index"
              class="absolute top-0 h-2 w-0.5 bg-white/20 "
              :style="{ left: `${((index - 1) / (timeConfig.yearRange - 1)) * 100}%` }"
            >
              <div 
              class="absolute top-4 -translate-x-1/2 text-[10px] text-white/40 whitespace-nowrap pointer-events-none select-none">
                {{ timeConfig.startYear + index - 1 }}
              </div>
            </div>
          </div>
        </div>

        <!-- 当前显示 -->
        <div class="flex flex-col items-end min-w-20">
          <span class="text-xl font-bold text-emerald-400">{{ currentYear }}</span>
          <span class="text-[10px] text-white/40">年份索引: {{ timeConfig.yearIndex }}</span>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted, watch } from 'vue';
import { VideoPlay, VideoPause } from '@element-plus/icons-vue';
import MapManager from '@/tools/mapManager';

const props = defineProps<{
  visible: boolean;
}>();

const mapManager = MapManager.getInstance();
const timeConfig = mapManager.timeConfig;

const progress = computed(() => {
  if (timeConfig.value.yearRange <= 1) return 0;
  return (timeConfig.value.yearIndex / (timeConfig.value.yearRange - 1)) * 100;
});

const currentYear = computed(() => timeConfig.value.startYear + timeConfig.value.yearIndex);

// 自动播放逻辑
let playInterval: any = null;

const togglePlay = () => {
  timeConfig.value.isPlaying = !timeConfig.value.isPlaying;
  
  if (timeConfig.value.isPlaying) {
    playInterval = setInterval(() => {
      if (timeConfig.value.yearIndex < timeConfig.value.yearRange - 1) {
        timeConfig.value.yearIndex++;
      } else {
        timeConfig.value.yearIndex = 0;
      }
    }, 1500);
  } else {
    clearInterval(playInterval);
  }
};

// 拖拽逻辑
const isDragging = ref(false);
const tempProgress = ref(0);
const trackRef = ref<HTMLElement | null>(null);

const handleTrackMouseDown = (e: MouseEvent) => {
  if (!trackRef.value) return;
  const rect = trackRef.value.getBoundingClientRect();
  let pos = (e.clientX - rect.left) / rect.width;
  pos = Math.max(0, Math.min(1, pos));
  
  const maxIdx = timeConfig.value.yearRange - 1;
  const targetIndex = Math.round(pos * maxIdx);
  timeConfig.value.yearIndex = targetIndex;
  
  // 点击轨道也立即开启拖拽模式，让滑块跟随
  startDrag(e);
};

const startDrag = (e: MouseEvent) => {
  e.preventDefault();
  isDragging.value = true;
  
  if (timeConfig.value.isPlaying) {
    timeConfig.value.isPlaying = false;
    if (playInterval) clearInterval(playInterval);
  }
  
  const track = trackRef.value;
  if (!track) return;
  const trackRect = track.getBoundingClientRect();

  const updateProgress = (clientX: number) => {
    let pos = (clientX - trackRect.left) / trackRect.width;
    pos = Math.max(0, Math.min(1, pos));
    tempProgress.value = pos;
  };

  // 初始设置
  updateProgress(e.clientX);

  const moveHandler = (moveEvent: MouseEvent) => {
    if (!isDragging.value) return;
    updateProgress(moveEvent.clientX);
  };
  
  const upHandler = () => {
    if (isDragging.value) {
      const maxIdx = timeConfig.value.yearRange - 1;
      const finalIndex = Math.round(tempProgress.value * maxIdx);
      timeConfig.value.yearIndex = Math.max(0, Math.min(finalIndex, maxIdx));
      isDragging.value = false;
    }
    window.removeEventListener('mousemove', moveHandler);
    window.removeEventListener('mouseup', upHandler);
  };
  
  window.addEventListener('mousemove', moveHandler);
  window.addEventListener('mouseup', upHandler);
};

// 监听年份变化，同步更新地图样式
watch(() => timeConfig.value.yearIndex, () => {
  mapManager.updateLayerStyles();
});

onUnmounted(() => {
  if (playInterval) clearInterval(playInterval);
});
</script>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translate(-50%, 20px);
}
</style>
