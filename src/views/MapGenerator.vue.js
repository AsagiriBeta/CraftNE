/// <reference types="../../node_modules/.vue-global-types/vue_3.5_0_0_0.d.ts" />
import { ref } from "vue";
import AIModuleTemplate from "../components/AIModuleTemplate.vue";
const mapTrainingOptions = ref({
    epochs: 100,
    batchSize: 32,
    learningRate: 0.001,
    imageSize: 512
});
const handleStartTraining = (config) => {
    console.log("Starting map training with config:", config);
};
const handleStartInference = (config) => {
    console.log("Starting map inference with config:", config);
};
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(Object.assign({ class: "map-generator" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
/** @type {[typeof AIModuleTemplate, ]} */ ;
// @ts-ignore
const __VLS_0 = __VLS_asFunctionalComponent(AIModuleTemplate, new AIModuleTemplate(Object.assign(Object.assign({ 'onStartTraining': {} }, { 'onStartInference': {} }), { moduleType: "map", trainingOptions: (__VLS_ctx.mapTrainingOptions) })));
const __VLS_1 = __VLS_0(Object.assign(Object.assign({ 'onStartTraining': {} }, { 'onStartInference': {} }), { moduleType: "map", trainingOptions: (__VLS_ctx.mapTrainingOptions) }), ...__VLS_functionalComponentArgsRest(__VLS_0));
let __VLS_3;
let __VLS_4;
let __VLS_5;
const __VLS_6 = {
    onStartTraining: (__VLS_ctx.handleStartTraining)
};
const __VLS_7 = {
    onStartInference: (__VLS_ctx.handleStartInference)
};
var __VLS_2;
/** @type {__VLS_StyleScopedClasses['map-generator']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            AIModuleTemplate: AIModuleTemplate,
            mapTrainingOptions: mapTrainingOptions,
            handleStartTraining: handleStartTraining,
            handleStartInference: handleStartInference,
        };
    },
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
