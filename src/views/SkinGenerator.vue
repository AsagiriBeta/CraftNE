<template>
  <div class="skin-generator">
    <h2>皮肤生成模型</h2>
    <AIModuleTemplate 
      module-type="skin"
      :training-options="skinTrainingOptions"
      @start-training="handleStartTraining"
      @start-inference="handleStartInference"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import AIModuleTemplate from "../components/AIModuleTemplate.vue";

const skinTrainingOptions = ref({
  epochs: 50,
  batchSize: 64,
  learningRate: 0.0002,
  imageSize: 64
});

const handleStartTraining = (config: any) => {
  console.log("Starting skin training with config:", config);
};

const handleStartInference = (config: any) => {
  console.log("Starting skin inference with config:", config);
};
</script>