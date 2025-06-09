<template>
  <div class="texture-generator">
    <h2>材质生成模型</h2>
    <AIModuleTemplate 
      module-type="texture"
      :training-options="textureTrainingOptions"
      @start-training="handleStartTraining"
      @start-inference="handleStartInference"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import AIModuleTemplate from "../components/AIModuleTemplate.vue";

const textureTrainingOptions = ref({
  epochs: 75,
  batchSize: 16,
  learningRate: 0.0001,
  imageSize: 256
});

const handleStartTraining = (config: any) => {
  console.log("Starting texture training with config:", config);
};

const handleStartInference = (config: any) => {
  console.log("Starting texture inference with config:", config);
};
</script>