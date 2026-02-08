<template>
  <div class="px-5 pb-5 overflow-y-auto hide-scrollbar max-h-screen">
    <div class="flex justify-between items-center ">
    <h1 
    class="text-2xl mb-2 font-bold select-none">🌏影像数据采集与可视化</h1>
    </div>
    <hr class="border-gray-300">
    <div class="form-container">
      <!-- 步骤指示器 -->
      <div class="flex justify-center items-center text-sm m-[20px_0]">
          <div 
            class="step-indicator" 
            :class="{ active: currentStep === 1 }"
            @click="goToStep(1)"
          >
            <span class="step-number">Step1</span>
            <span class="step-text">基础筛选</span>
          </div>
          <div class="step-separator">→</div>
          <div 
            class="step-indicator" 
            :class="{ active: currentStep === 2 }"
            @click="goToStep(2)"
          >
            <span class="step-number">Step2</span>
            <span class="step-text">卫星选择</span>
          </div>
          <div class="step-separator">→</div>
          <div 
            class="step-indicator" 
            :class="{ active: currentStep === 3 }"
            @click="goToStep(3)"
          >
            <span class="step-number">Step3</span>
            <span class="step-text">可视化</span>
          </div>
        </div>

      <!-- 步骤内容 -->
      <div class="step-content">
        <!-- 步骤1：基本筛选 -->
        <div v-if="currentStep === 1" class="step-panel">
          <Step1 
            @next-step="()=>{
              goToStep(2);
            }"
          />
        </div>

        <!-- 步骤2：卫星选择 -->
        <div v-if="currentStep === 2" class="step-panel">
          <Step2 @prev-step="goToStep(1)" @next-step="()=>{
            goToStep(3);}" />
        </div>

        <!-- 步骤3：可视化配置 -->
        <div v-if="currentStep === 3" class="step-panel">
          <VisualParams @prev-step="goToStep(2)" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import Step1 from '@/components/ImgGet/Step1.vue';
import Step2 from '@/components/ImgGet/Step2.vue';
import VisualParams from '@/components/ImgGet/VisualParams.vue';

const preventDefault = (e) => {
  e.preventDefault();
}

const currentStep = ref(1);

const goToStep = (step) => {
  currentStep.value = step;
};

</script>

<style scoped>

.form-container {
  width: 100%;
  max-height: 100%;
}

.step-indicator {
  padding: 8px 16px;
  border-radius: 20px;
  background-color: #e9ecef;
  cursor: pointer;
  transition: all 0.5s ease;
  margin: 0 5px;
  display: flex;
  align-items: center;
  gap: 0;
  overflow: hidden;
  min-width: 60px;
  justify-content: center;
  
}

.step-indicator:hover {
  background-color: #dee2e6;
  gap: 8px;
  min-width: auto;
}

.step-indicator.active {
  background-color: #409eff;
  color: white;
  gap: 8px;
  min-width: auto;
}

.step-number {
  white-space: nowrap;
}

.step-text {
  white-space: nowrap;
  opacity: 0;
  width: 0;
  transition: all 0.5s ease;
  overflow: hidden;
}

.step-indicator:hover .step-text,
.step-indicator.active .step-text {
  opacity: 1;
  width: auto;
}

.step-indicator:hover .step-number {
  margin-right: 0;
}

.step-indicator.active .step-number {
  margin-right: 0;
}

.step-separator {
  align-self: center;
  margin: 0 5px;
}

.step-content {
  width: 100%;
}

.step-panel {
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .step-indicator-container {
    flex-direction: column;
    align-items: center;
  }
  
  .step-separator {
    transform: rotate(90deg);
    margin: 10px 0;
  }
}
</style>