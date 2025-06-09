/// <reference types="../../node_modules/.vue-global-types/vue_3.5_0_0_0.d.ts" />
import { ref } from "vue";
import AIModuleTemplate from "../components/AIModuleTemplate.vue";
const textureTrainingOptions = ref({
    epochs: 75,
    batchSize: 16,
    learningRate: 0.0001,
    imageSize: 256
});
const handleStartTraining = (config) => {
    console.log("Starting texture training with config:", config);
};
const handleStartInference = (config) => {
    console.log("Starting texture inference with config:", config);
};
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(Object.assign({ class: "texture-generator" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
/** @type {[typeof AIModuleTemplate, ]} */ ;
// @ts-ignore
const __VLS_0 = __VLS_asFunctionalComponent(AIModuleTemplate, new AIModuleTemplate(Object.assign(Object.assign({ 'onStartTraining': {} }, { 'onStartInference': {} }), { moduleType: "texture", trainingOptions: (__VLS_ctx.textureTrainingOptions) })));
const __VLS_1 = __VLS_0(Object.assign(Object.assign({ 'onStartTraining': {} }, { 'onStartInference': {} }), { moduleType: "texture", trainingOptions: (__VLS_ctx.textureTrainingOptions) }), ...__VLS_functionalComponentArgsRest(__VLS_0));
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
/** @type {__VLS_StyleScopedClasses['texture-generator']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            AIModuleTemplate: AIModuleTemplate,
            textureTrainingOptions: textureTrainingOptions,
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
