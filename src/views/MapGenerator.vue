<template>
  <div class="map-generator">
    <h2>地图生成模型</h2>
    <AIModuleTemplate 
      module-type="map"
      :training-options="mapTrainingOptions"
      @start-training="handleStartTraining"
      @start-inference="handleStartInference"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import AIModuleTemplate from "../components/AIModuleTemplate.vue";

const mapTrainingOptions = ref({
  epochs: 100,
  batchSize: 32,
  learningRate: 0.001,
  imageSize: 512
});

const handleStartTraining = (config: any) => {
  console.log("Starting map training with config:", config);
};

const handleStartInference = (config: any) => {
  console.log("Starting map inference with config:", config);
};
</script>