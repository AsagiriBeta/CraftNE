/// <reference types="../../node_modules/.vue-global-types/vue_3.5_0_0_0.d.ts" />
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { ref } from "vue";
import { invoke } from "@tauri-apps/api/core";
import { ElMessage } from "element-plus";
const props = defineProps();
const emit = defineEmits(["start-training", "start-inference"]);
const activeTab = ref("dataset");
const processing = ref(false);
const training = ref(false);
const inferencing = ref(false);
const trainingProgress = ref(0);
const currentEpoch = ref(0);
const currentLoss = ref("0.000");
const inferenceResults = ref([]);
// 表单数据
const datasetForm = ref({
    path: "",
    format: "png",
    preprocessing: ["resize", "normalize"]
});
const trainingForm = ref({
    architecture: "gan",
    epochs: props.trainingOptions.epochs || 100,
    batchSize: props.trainingOptions.batchSize || 32,
    learningRate: props.trainingOptions.learningRate || 0.001
});
const inferenceForm = ref({
    modelPath: "",
    prompt: "",
    count: 1
});
// 方法
const selectDatasetPath = () => __awaiter(void 0, void 0, void 0, function* () {
    // TODO: 使用Tauri的文件对话框
    ElMessage.info("请手动输入数据集路径");
});
const selectModelPath = () => __awaiter(void 0, void 0, void 0, function* () {
    // TODO: 使用Tauri的文件对话框
    ElMessage.info("请手动输入模型文件路径");
});
const processDataset = () => __awaiter(void 0, void 0, void 0, function* () {
    processing.value = true;
    try {
        yield invoke("process_dataset", {
            datasetPath: datasetForm.value.path,
            modelType: props.moduleType
        });
        ElMessage.success("数据集处理完成!");
    }
    catch (error) {
        ElMessage.error(`数据集处理失败: ${error}`);
    }
    finally {
        processing.value = false;
    }
});
const startTraining = () => __awaiter(void 0, void 0, void 0, function* () {
    training.value = true;
    try {
        const taskId = yield invoke("create_training_task", {
            modelType: props.moduleType,
            config: trainingForm.value
        });
        ElMessage.success("训练任务已开始!");
        emit("start-training", trainingForm.value);
        // 模拟训练进度
        simulateTrainingProgress();
    }
    catch (error) {
        ElMessage.error(`训练启动失败: ${error}`);
        training.value = false;
    }
});
const stopTraining = () => {
    training.value = false;
    trainingProgress.value = 0;
    currentEpoch.value = 0;
    ElMessage.info("训练已停止");
};
const simulateTrainingProgress = () => {
    const interval = setInterval(() => {
        if (!training.value) {
            clearInterval(interval);
            return;
        }
        trainingProgress.value += 1;
        currentEpoch.value = Math.floor((trainingProgress.value / 100) * trainingForm.value.epochs);
        currentLoss.value = (Math.random() * 0.1 + 0.05).toFixed(3);
        if (trainingProgress.value >= 100) {
            training.value = false;
            ElMessage.success("训练完成!");
            clearInterval(interval);
        }
    }, 500);
};
const startInference = () => __awaiter(void 0, void 0, void 0, function* () {
    inferencing.value = true;
    try {
        const result = yield invoke("generate_content", {
            modelType: props.moduleType,
            prompt: inferenceForm.value.prompt,
            modelPath: inferenceForm.value.modelPath
        });
        // 模拟生成结果
        inferenceResults.value = Array.from({ length: inferenceForm.value.count }, (_, i) => `data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==`);
        ElMessage.success("生成完成!");
        emit("start-inference", inferenceForm.value);
    }
    catch (error) {
        ElMessage.error(`生成失败: ${error}`);
    }
    finally {
        inferencing.value = false;
    }
});
const downloadResult = (result, index) => {
    // TODO: 实现文件下载
    ElMessage.success(`结果 ${index + 1} 已保存`);
};
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
/** @type {__VLS_StyleScopedClasses['result-item']} */ ;
// CSS variable injection 
// CSS variable injection end 
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(Object.assign({ class: "ai-module" }));
const __VLS_0 = {}.ElTabs;
/** @type {[typeof __VLS_components.ElTabs, typeof __VLS_components.elTabs, typeof __VLS_components.ElTabs, typeof __VLS_components.elTabs, ]} */ ;
// @ts-ignore
const __VLS_1 = __VLS_asFunctionalComponent(__VLS_0, new __VLS_0({
    modelValue: (__VLS_ctx.activeTab),
    type: "card",
}));
const __VLS_2 = __VLS_1({
    modelValue: (__VLS_ctx.activeTab),
    type: "card",
}, ...__VLS_functionalComponentArgsRest(__VLS_1));
__VLS_3.slots.default;
const __VLS_4 = {}.ElTabPane;
/** @type {[typeof __VLS_components.ElTabPane, typeof __VLS_components.elTabPane, typeof __VLS_components.ElTabPane, typeof __VLS_components.elTabPane, ]} */ ;
// @ts-ignore
const __VLS_5 = __VLS_asFunctionalComponent(__VLS_4, new __VLS_4({
    label: "训练集处理",
    name: "dataset",
}));
const __VLS_6 = __VLS_5({
    label: "训练集处理",
    name: "dataset",
}, ...__VLS_functionalComponentArgsRest(__VLS_5));
__VLS_7.slots.default;
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(Object.assign({ class: "tab-content" }));
const __VLS_8 = {}.ElForm;
/** @type {[typeof __VLS_components.ElForm, typeof __VLS_components.elForm, typeof __VLS_components.ElForm, typeof __VLS_components.elForm, ]} */ ;
// @ts-ignore
const __VLS_9 = __VLS_asFunctionalComponent(__VLS_8, new __VLS_8({
    model: (__VLS_ctx.datasetForm),
    labelWidth: "120px",
}));
const __VLS_10 = __VLS_9({
    model: (__VLS_ctx.datasetForm),
    labelWidth: "120px",
}, ...__VLS_functionalComponentArgsRest(__VLS_9));
__VLS_11.slots.default;
const __VLS_12 = {}.ElFormItem;
/** @type {[typeof __VLS_components.ElFormItem, typeof __VLS_components.elFormItem, typeof __VLS_components.ElFormItem, typeof __VLS_components.elFormItem, ]} */ ;
// @ts-ignore
const __VLS_13 = __VLS_asFunctionalComponent(__VLS_12, new __VLS_12({
    label: "数据集路径",
}));
const __VLS_14 = __VLS_13({
    label: "数据集路径",
}, ...__VLS_functionalComponentArgsRest(__VLS_13));
__VLS_15.slots.default;
const __VLS_16 = {}.ElInput;
/** @type {[typeof __VLS_components.ElInput, typeof __VLS_components.elInput, typeof __VLS_components.ElInput, typeof __VLS_components.elInput, ]} */ ;
// @ts-ignore
const __VLS_17 = __VLS_asFunctionalComponent(__VLS_16, new __VLS_16({
    modelValue: (__VLS_ctx.datasetForm.path),
    placeholder: "选择数据集文件夹",
}));
const __VLS_18 = __VLS_17({
    modelValue: (__VLS_ctx.datasetForm.path),
    placeholder: "选择数据集文件夹",
}, ...__VLS_functionalComponentArgsRest(__VLS_17));
__VLS_19.slots.default;
{
    const { append: __VLS_thisSlot } = __VLS_19.slots;
    const __VLS_20 = {}.ElButton;
    /** @type {[typeof __VLS_components.ElButton, typeof __VLS_components.elButton, typeof __VLS_components.ElButton, typeof __VLS_components.elButton, ]} */ ;
    // @ts-ignore
    const __VLS_21 = __VLS_asFunctionalComponent(__VLS_20, new __VLS_20(Object.assign({ 'onClick': {} })));
    const __VLS_22 = __VLS_21(Object.assign({ 'onClick': {} }), ...__VLS_functionalComponentArgsRest(__VLS_21));
    let __VLS_24;
    let __VLS_25;
    let __VLS_26;
    const __VLS_27 = {
        onClick: (__VLS_ctx.selectDatasetPath)
    };
    __VLS_23.slots.default;
    var __VLS_23;
}
var __VLS_19;
var __VLS_15;
const __VLS_28 = {}.ElFormItem;
/** @type {[typeof __VLS_components.ElFormItem, typeof __VLS_components.elFormItem, typeof __VLS_components.ElFormItem, typeof __VLS_components.elFormItem, ]} */ ;
// @ts-ignore
const __VLS_29 = __VLS_asFunctionalComponent(__VLS_28, new __VLS_28({
    label: "数据格式",
}));
const __VLS_30 = __VLS_29({
    label: "数据格式",
}, ...__VLS_functionalComponentArgsRest(__VLS_29));
__VLS_31.slots.default;
const __VLS_32 = {}.ElSelect;
/** @type {[typeof __VLS_components.ElSelect, typeof __VLS_components.elSelect, typeof __VLS_components.ElSelect, typeof __VLS_components.elSelect, ]} */ ;
// @ts-ignore
const __VLS_33 = __VLS_asFunctionalComponent(__VLS_32, new __VLS_32({
    modelValue: (__VLS_ctx.datasetForm.format),
}));
const __VLS_34 = __VLS_33({
    modelValue: (__VLS_ctx.datasetForm.format),
}, ...__VLS_functionalComponentArgsRest(__VLS_33));
__VLS_35.slots.default;
const __VLS_36 = {}.ElOption;
/** @type {[typeof __VLS_components.ElOption, typeof __VLS_components.elOption, ]} */ ;
// @ts-ignore
const __VLS_37 = __VLS_asFunctionalComponent(__VLS_36, new __VLS_36({
    label: "PNG Images",
    value: "png",
}));
const __VLS_38 = __VLS_37({
    label: "PNG Images",
    value: "png",
}, ...__VLS_functionalComponentArgsRest(__VLS_37));
const __VLS_40 = {}.ElOption;
/** @type {[typeof __VLS_components.ElOption, typeof __VLS_components.elOption, ]} */ ;
// @ts-ignore
const __VLS_41 = __VLS_asFunctionalComponent(__VLS_40, new __VLS_40({
    label: "NBT Files",
    value: "nbt",
}));
const __VLS_42 = __VLS_41({
    label: "NBT Files",
    value: "nbt",
}, ...__VLS_functionalComponentArgsRest(__VLS_41));
const __VLS_44 = {}.ElOption;
/** @type {[typeof __VLS_components.ElOption, typeof __VLS_components.elOption, ]} */ ;
// @ts-ignore
const __VLS_45 = __VLS_asFunctionalComponent(__VLS_44, new __VLS_44({
    label: "Schematic",
    value: "schematic",
}));
const __VLS_46 = __VLS_45({
    label: "Schematic",
    value: "schematic",
}, ...__VLS_functionalComponentArgsRest(__VLS_45));
var __VLS_35;
var __VLS_31;
const __VLS_48 = {}.ElFormItem;
/** @type {[typeof __VLS_components.ElFormItem, typeof __VLS_components.elFormItem, typeof __VLS_components.ElFormItem, typeof __VLS_components.elFormItem, ]} */ ;
// @ts-ignore
const __VLS_49 = __VLS_asFunctionalComponent(__VLS_48, new __VLS_48({
    label: "预处理选项",
}));
const __VLS_50 = __VLS_49({
    label: "预处理选项",
}, ...__VLS_functionalComponentArgsRest(__VLS_49));
__VLS_51.slots.default;
const __VLS_52 = {}.ElCheckboxGroup;
/** @type {[typeof __VLS_components.ElCheckboxGroup, typeof __VLS_components.elCheckboxGroup, typeof __VLS_components.ElCheckboxGroup, typeof __VLS_components.elCheckboxGroup, ]} */ ;
// @ts-ignore
const __VLS_53 = __VLS_asFunctionalComponent(__VLS_52, new __VLS_52({
    modelValue: (__VLS_ctx.datasetForm.preprocessing),
}));
const __VLS_54 = __VLS_53({
    modelValue: (__VLS_ctx.datasetForm.preprocessing),
}, ...__VLS_functionalComponentArgsRest(__VLS_53));
__VLS_55.slots.default;
const __VLS_56 = {}.ElCheckbox;
/** @type {[typeof __VLS_components.ElCheckbox, typeof __VLS_components.elCheckbox, typeof __VLS_components.ElCheckbox, typeof __VLS_components.elCheckbox, ]} */ ;
// @ts-ignore
const __VLS_57 = __VLS_asFunctionalComponent(__VLS_56, new __VLS_56({
    value: "resize",
}));
const __VLS_58 = __VLS_57({
    value: "resize",
}, ...__VLS_functionalComponentArgsRest(__VLS_57));
__VLS_59.slots.default;
var __VLS_59;
const __VLS_60 = {}.ElCheckbox;
/** @type {[typeof __VLS_components.ElCheckbox, typeof __VLS_components.elCheckbox, typeof __VLS_components.ElCheckbox, typeof __VLS_components.elCheckbox, ]} */ ;
// @ts-ignore
const __VLS_61 = __VLS_asFunctionalComponent(__VLS_60, new __VLS_60({
    value: "augment",
}));
const __VLS_62 = __VLS_61({
    value: "augment",
}, ...__VLS_functionalComponentArgsRest(__VLS_61));
__VLS_63.slots.default;
var __VLS_63;
const __VLS_64 = {}.ElCheckbox;
/** @type {[typeof __VLS_components.ElCheckbox, typeof __VLS_components.elCheckbox, typeof __VLS_components.ElCheckbox, typeof __VLS_components.elCheckbox, ]} */ ;
// @ts-ignore
const __VLS_65 = __VLS_asFunctionalComponent(__VLS_64, new __VLS_64({
    value: "normalize",
}));
const __VLS_66 = __VLS_65({
    value: "normalize",
}, ...__VLS_functionalComponentArgsRest(__VLS_65));
__VLS_67.slots.default;
var __VLS_67;
var __VLS_55;
var __VLS_51;
const __VLS_68 = {}.ElFormItem;
/** @type {[typeof __VLS_components.ElFormItem, typeof __VLS_components.elFormItem, typeof __VLS_components.ElFormItem, typeof __VLS_components.elFormItem, ]} */ ;
// @ts-ignore
const __VLS_69 = __VLS_asFunctionalComponent(__VLS_68, new __VLS_68({}));
const __VLS_70 = __VLS_69({}, ...__VLS_functionalComponentArgsRest(__VLS_69));
__VLS_71.slots.default;
const __VLS_72 = {}.ElButton;
/** @type {[typeof __VLS_components.ElButton, typeof __VLS_components.elButton, typeof __VLS_components.ElButton, typeof __VLS_components.elButton, ]} */ ;
// @ts-ignore
const __VLS_73 = __VLS_asFunctionalComponent(__VLS_72, new __VLS_72(Object.assign({ 'onClick': {} }, { type: "primary", loading: (__VLS_ctx.processing) })));
const __VLS_74 = __VLS_73(Object.assign({ 'onClick': {} }, { type: "primary", loading: (__VLS_ctx.processing) }), ...__VLS_functionalComponentArgsRest(__VLS_73));
let __VLS_76;
let __VLS_77;
let __VLS_78;
const __VLS_79 = {
    onClick: (__VLS_ctx.processDataset)
};
__VLS_75.slots.default;
var __VLS_75;
var __VLS_71;
var __VLS_11;
var __VLS_7;
const __VLS_80 = {}.ElTabPane;
/** @type {[typeof __VLS_components.ElTabPane, typeof __VLS_components.elTabPane, typeof __VLS_components.ElTabPane, typeof __VLS_components.elTabPane, ]} */ ;
// @ts-ignore
const __VLS_81 = __VLS_asFunctionalComponent(__VLS_80, new __VLS_80({
    label: "训练",
    name: "training",
}));
const __VLS_82 = __VLS_81({
    label: "训练",
    name: "training",
}, ...__VLS_functionalComponentArgsRest(__VLS_81));
__VLS_83.slots.default;
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(Object.assign({ class: "tab-content" }));
const __VLS_84 = {}.ElForm;
/** @type {[typeof __VLS_components.ElForm, typeof __VLS_components.elForm, typeof __VLS_components.ElForm, typeof __VLS_components.elForm, ]} */ ;
// @ts-ignore
const __VLS_85 = __VLS_asFunctionalComponent(__VLS_84, new __VLS_84({
    model: (__VLS_ctx.trainingForm),
    labelWidth: "120px",
}));
const __VLS_86 = __VLS_85({
    model: (__VLS_ctx.trainingForm),
    labelWidth: "120px",
}, ...__VLS_functionalComponentArgsRest(__VLS_85));
__VLS_87.slots.default;
const __VLS_88 = {}.ElFormItem;
/** @type {[typeof __VLS_components.ElFormItem, typeof __VLS_components.elFormItem, typeof __VLS_components.ElFormItem, typeof __VLS_components.elFormItem, ]} */ ;
// @ts-ignore
const __VLS_89 = __VLS_asFunctionalComponent(__VLS_88, new __VLS_88({
    label: "模型架构",
}));
const __VLS_90 = __VLS_89({
    label: "模型架构",
}, ...__VLS_functionalComponentArgsRest(__VLS_89));
__VLS_91.slots.default;
const __VLS_92 = {}.ElSelect;
/** @type {[typeof __VLS_components.ElSelect, typeof __VLS_components.elSelect, typeof __VLS_components.ElSelect, typeof __VLS_components.elSelect, ]} */ ;
// @ts-ignore
const __VLS_93 = __VLS_asFunctionalComponent(__VLS_92, new __VLS_92({
    modelValue: (__VLS_ctx.trainingForm.architecture),
}));
const __VLS_94 = __VLS_93({
    modelValue: (__VLS_ctx.trainingForm.architecture),
}, ...__VLS_functionalComponentArgsRest(__VLS_93));
__VLS_95.slots.default;
const __VLS_96 = {}.ElOption;
/** @type {[typeof __VLS_components.ElOption, typeof __VLS_components.elOption, ]} */ ;
// @ts-ignore
const __VLS_97 = __VLS_asFunctionalComponent(__VLS_96, new __VLS_96({
    label: "GAN",
    value: "gan",
}));
const __VLS_98 = __VLS_97({
    label: "GAN",
    value: "gan",
}, ...__VLS_functionalComponentArgsRest(__VLS_97));
const __VLS_100 = {}.ElOption;
/** @type {[typeof __VLS_components.ElOption, typeof __VLS_components.elOption, ]} */ ;
// @ts-ignore
const __VLS_101 = __VLS_asFunctionalComponent(__VLS_100, new __VLS_100({
    label: "VAE",
    value: "vae",
}));
const __VLS_102 = __VLS_101({
    label: "VAE",
    value: "vae",
}, ...__VLS_functionalComponentArgsRest(__VLS_101));
const __VLS_104 = {}.ElOption;
/** @type {[typeof __VLS_components.ElOption, typeof __VLS_components.elOption, ]} */ ;
// @ts-ignore
const __VLS_105 = __VLS_asFunctionalComponent(__VLS_104, new __VLS_104({
    label: "Diffusion",
    value: "diffusion",
}));
const __VLS_106 = __VLS_105({
    label: "Diffusion",
    value: "diffusion",
}, ...__VLS_functionalComponentArgsRest(__VLS_105));
var __VLS_95;
var __VLS_91;
const __VLS_108 = {}.ElFormItem;
/** @type {[typeof __VLS_components.ElFormItem, typeof __VLS_components.elFormItem, typeof __VLS_components.ElFormItem, typeof __VLS_components.elFormItem, ]} */ ;
// @ts-ignore
const __VLS_109 = __VLS_asFunctionalComponent(__VLS_108, new __VLS_108({
    label: "训练轮数",
}));
const __VLS_110 = __VLS_109({
    label: "训练轮数",
}, ...__VLS_functionalComponentArgsRest(__VLS_109));
__VLS_111.slots.default;
const __VLS_112 = {}.ElInputNumber;
/** @type {[typeof __VLS_components.ElInputNumber, typeof __VLS_components.elInputNumber, ]} */ ;
// @ts-ignore
const __VLS_113 = __VLS_asFunctionalComponent(__VLS_112, new __VLS_112({
    modelValue: (__VLS_ctx.trainingForm.epochs),
    min: (1),
    max: (1000),
}));
const __VLS_114 = __VLS_113({
    modelValue: (__VLS_ctx.trainingForm.epochs),
    min: (1),
    max: (1000),
}, ...__VLS_functionalComponentArgsRest(__VLS_113));
var __VLS_111;
const __VLS_116 = {}.ElFormItem;
/** @type {[typeof __VLS_components.ElFormItem, typeof __VLS_components.elFormItem, typeof __VLS_components.ElFormItem, typeof __VLS_components.elFormItem, ]} */ ;
// @ts-ignore
const __VLS_117 = __VLS_asFunctionalComponent(__VLS_116, new __VLS_116({
    label: "批次大小",
}));
const __VLS_118 = __VLS_117({
    label: "批次大小",
}, ...__VLS_functionalComponentArgsRest(__VLS_117));
__VLS_119.slots.default;
const __VLS_120 = {}.ElInputNumber;
/** @type {[typeof __VLS_components.ElInputNumber, typeof __VLS_components.elInputNumber, ]} */ ;
// @ts-ignore
const __VLS_121 = __VLS_asFunctionalComponent(__VLS_120, new __VLS_120({
    modelValue: (__VLS_ctx.trainingForm.batchSize),
    min: (1),
    max: (128),
}));
const __VLS_122 = __VLS_121({
    modelValue: (__VLS_ctx.trainingForm.batchSize),
    min: (1),
    max: (128),
}, ...__VLS_functionalComponentArgsRest(__VLS_121));
var __VLS_119;
const __VLS_124 = {}.ElFormItem;
/** @type {[typeof __VLS_components.ElFormItem, typeof __VLS_components.elFormItem, typeof __VLS_components.ElFormItem, typeof __VLS_components.elFormItem, ]} */ ;
// @ts-ignore
const __VLS_125 = __VLS_asFunctionalComponent(__VLS_124, new __VLS_124({
    label: "学习率",
}));
const __VLS_126 = __VLS_125({
    label: "学习率",
}, ...__VLS_functionalComponentArgsRest(__VLS_125));
__VLS_127.slots.default;
const __VLS_128 = {}.ElInputNumber;
/** @type {[typeof __VLS_components.ElInputNumber, typeof __VLS_components.elInputNumber, ]} */ ;
// @ts-ignore
const __VLS_129 = __VLS_asFunctionalComponent(__VLS_128, new __VLS_128({
    modelValue: (__VLS_ctx.trainingForm.learningRate),
    min: (0.0001),
    max: (0.1),
    step: (0.0001),
    precision: (4),
}));
const __VLS_130 = __VLS_129({
    modelValue: (__VLS_ctx.trainingForm.learningRate),
    min: (0.0001),
    max: (0.1),
    step: (0.0001),
    precision: (4),
}, ...__VLS_functionalComponentArgsRest(__VLS_129));
var __VLS_127;
const __VLS_132 = {}.ElFormItem;
/** @type {[typeof __VLS_components.ElFormItem, typeof __VLS_components.elFormItem, typeof __VLS_components.ElFormItem, typeof __VLS_components.elFormItem, ]} */ ;
// @ts-ignore
const __VLS_133 = __VLS_asFunctionalComponent(__VLS_132, new __VLS_132({}));
const __VLS_134 = __VLS_133({}, ...__VLS_functionalComponentArgsRest(__VLS_133));
__VLS_135.slots.default;
const __VLS_136 = {}.ElButton;
/** @type {[typeof __VLS_components.ElButton, typeof __VLS_components.elButton, typeof __VLS_components.ElButton, typeof __VLS_components.elButton, ]} */ ;
// @ts-ignore
const __VLS_137 = __VLS_asFunctionalComponent(__VLS_136, new __VLS_136(Object.assign({ 'onClick': {} }, { type: "primary", loading: (__VLS_ctx.training) })));
const __VLS_138 = __VLS_137(Object.assign({ 'onClick': {} }, { type: "primary", loading: (__VLS_ctx.training) }), ...__VLS_functionalComponentArgsRest(__VLS_137));
let __VLS_140;
let __VLS_141;
let __VLS_142;
const __VLS_143 = {
    onClick: (__VLS_ctx.startTraining)
};
__VLS_139.slots.default;
var __VLS_139;
const __VLS_144 = {}.ElButton;
/** @type {[typeof __VLS_components.ElButton, typeof __VLS_components.elButton, typeof __VLS_components.ElButton, typeof __VLS_components.elButton, ]} */ ;
// @ts-ignore
const __VLS_145 = __VLS_asFunctionalComponent(__VLS_144, new __VLS_144(Object.assign({ 'onClick': {} }, { disabled: (!__VLS_ctx.training) })));
const __VLS_146 = __VLS_145(Object.assign({ 'onClick': {} }, { disabled: (!__VLS_ctx.training) }), ...__VLS_functionalComponentArgsRest(__VLS_145));
let __VLS_148;
let __VLS_149;
let __VLS_150;
const __VLS_151 = {
    onClick: (__VLS_ctx.stopTraining)
};
__VLS_147.slots.default;
var __VLS_147;
var __VLS_135;
var __VLS_87;
if (__VLS_ctx.training) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(Object.assign({ class: "training-progress" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h4, __VLS_intrinsicElements.h4)({});
    const __VLS_152 = {}.ElProgress;
    /** @type {[typeof __VLS_components.ElProgress, typeof __VLS_components.elProgress, ]} */ ;
    // @ts-ignore
    const __VLS_153 = __VLS_asFunctionalComponent(__VLS_152, new __VLS_152({
        percentage: (__VLS_ctx.trainingProgress),
    }));
    const __VLS_154 = __VLS_153({
        percentage: (__VLS_ctx.trainingProgress),
    }, ...__VLS_functionalComponentArgsRest(__VLS_153));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(Object.assign({ class: "progress-info" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    (__VLS_ctx.currentEpoch);
    (__VLS_ctx.trainingForm.epochs);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    (__VLS_ctx.currentLoss);
}
var __VLS_83;
const __VLS_156 = {}.ElTabPane;
/** @type {[typeof __VLS_components.ElTabPane, typeof __VLS_components.elTabPane, typeof __VLS_components.ElTabPane, typeof __VLS_components.elTabPane, ]} */ ;
// @ts-ignore
const __VLS_157 = __VLS_asFunctionalComponent(__VLS_156, new __VLS_156({
    label: "推理",
    name: "inference",
}));
const __VLS_158 = __VLS_157({
    label: "推理",
    name: "inference",
}, ...__VLS_functionalComponentArgsRest(__VLS_157));
__VLS_159.slots.default;
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(Object.assign({ class: "tab-content" }));
const __VLS_160 = {}.ElForm;
/** @type {[typeof __VLS_components.ElForm, typeof __VLS_components.elForm, typeof __VLS_components.ElForm, typeof __VLS_components.elForm, ]} */ ;
// @ts-ignore
const __VLS_161 = __VLS_asFunctionalComponent(__VLS_160, new __VLS_160({
    model: (__VLS_ctx.inferenceForm),
    labelWidth: "120px",
}));
const __VLS_162 = __VLS_161({
    model: (__VLS_ctx.inferenceForm),
    labelWidth: "120px",
}, ...__VLS_functionalComponentArgsRest(__VLS_161));
__VLS_163.slots.default;
const __VLS_164 = {}.ElFormItem;
/** @type {[typeof __VLS_components.ElFormItem, typeof __VLS_components.elFormItem, typeof __VLS_components.ElFormItem, typeof __VLS_components.elFormItem, ]} */ ;
// @ts-ignore
const __VLS_165 = __VLS_asFunctionalComponent(__VLS_164, new __VLS_164({
    label: "模型文件",
}));
const __VLS_166 = __VLS_165({
    label: "模型文件",
}, ...__VLS_functionalComponentArgsRest(__VLS_165));
__VLS_167.slots.default;
const __VLS_168 = {}.ElInput;
/** @type {[typeof __VLS_components.ElInput, typeof __VLS_components.elInput, typeof __VLS_components.ElInput, typeof __VLS_components.elInput, ]} */ ;
// @ts-ignore
const __VLS_169 = __VLS_asFunctionalComponent(__VLS_168, new __VLS_168({
    modelValue: (__VLS_ctx.inferenceForm.modelPath),
    placeholder: "选择训练好的模型",
}));
const __VLS_170 = __VLS_169({
    modelValue: (__VLS_ctx.inferenceForm.modelPath),
    placeholder: "选择训练好的模型",
}, ...__VLS_functionalComponentArgsRest(__VLS_169));
__VLS_171.slots.default;
{
    const { append: __VLS_thisSlot } = __VLS_171.slots;
    const __VLS_172 = {}.ElButton;
    /** @type {[typeof __VLS_components.ElButton, typeof __VLS_components.elButton, typeof __VLS_components.ElButton, typeof __VLS_components.elButton, ]} */ ;
    // @ts-ignore
    const __VLS_173 = __VLS_asFunctionalComponent(__VLS_172, new __VLS_172(Object.assign({ 'onClick': {} })));
    const __VLS_174 = __VLS_173(Object.assign({ 'onClick': {} }), ...__VLS_functionalComponentArgsRest(__VLS_173));
    let __VLS_176;
    let __VLS_177;
    let __VLS_178;
    const __VLS_179 = {
        onClick: (__VLS_ctx.selectModelPath)
    };
    __VLS_175.slots.default;
    var __VLS_175;
}
var __VLS_171;
var __VLS_167;
const __VLS_180 = {}.ElFormItem;
/** @type {[typeof __VLS_components.ElFormItem, typeof __VLS_components.elFormItem, typeof __VLS_components.ElFormItem, typeof __VLS_components.elFormItem, ]} */ ;
// @ts-ignore
const __VLS_181 = __VLS_asFunctionalComponent(__VLS_180, new __VLS_180({
    label: "生成提示",
}));
const __VLS_182 = __VLS_181({
    label: "生成提示",
}, ...__VLS_functionalComponentArgsRest(__VLS_181));
__VLS_183.slots.default;
const __VLS_184 = {}.ElInput;
/** @type {[typeof __VLS_components.ElInput, typeof __VLS_components.elInput, ]} */ ;
// @ts-ignore
const __VLS_185 = __VLS_asFunctionalComponent(__VLS_184, new __VLS_184({
    modelValue: (__VLS_ctx.inferenceForm.prompt),
    type: "textarea",
    rows: (3),
    placeholder: "描述你想要生成的内容...",
}));
const __VLS_186 = __VLS_185({
    modelValue: (__VLS_ctx.inferenceForm.prompt),
    type: "textarea",
    rows: (3),
    placeholder: "描述你想要生成的内容...",
}, ...__VLS_functionalComponentArgsRest(__VLS_185));
var __VLS_183;
const __VLS_188 = {}.ElFormItem;
/** @type {[typeof __VLS_components.ElFormItem, typeof __VLS_components.elFormItem, typeof __VLS_components.ElFormItem, typeof __VLS_components.elFormItem, ]} */ ;
// @ts-ignore
const __VLS_189 = __VLS_asFunctionalComponent(__VLS_188, new __VLS_188({
    label: "生成数量",
}));
const __VLS_190 = __VLS_189({
    label: "生成数量",
}, ...__VLS_functionalComponentArgsRest(__VLS_189));
__VLS_191.slots.default;
const __VLS_192 = {}.ElInputNumber;
/** @type {[typeof __VLS_components.ElInputNumber, typeof __VLS_components.elInputNumber, ]} */ ;
// @ts-ignore
const __VLS_193 = __VLS_asFunctionalComponent(__VLS_192, new __VLS_192({
    modelValue: (__VLS_ctx.inferenceForm.count),
    min: (1),
    max: (10),
}));
const __VLS_194 = __VLS_193({
    modelValue: (__VLS_ctx.inferenceForm.count),
    min: (1),
    max: (10),
}, ...__VLS_functionalComponentArgsRest(__VLS_193));
var __VLS_191;
const __VLS_196 = {}.ElFormItem;
/** @type {[typeof __VLS_components.ElFormItem, typeof __VLS_components.elFormItem, typeof __VLS_components.ElFormItem, typeof __VLS_components.elFormItem, ]} */ ;
// @ts-ignore
const __VLS_197 = __VLS_asFunctionalComponent(__VLS_196, new __VLS_196({}));
const __VLS_198 = __VLS_197({}, ...__VLS_functionalComponentArgsRest(__VLS_197));
__VLS_199.slots.default;
const __VLS_200 = {}.ElButton;
/** @type {[typeof __VLS_components.ElButton, typeof __VLS_components.elButton, typeof __VLS_components.ElButton, typeof __VLS_components.elButton, ]} */ ;
// @ts-ignore
const __VLS_201 = __VLS_asFunctionalComponent(__VLS_200, new __VLS_200(Object.assign({ 'onClick': {} }, { type: "primary", loading: (__VLS_ctx.inferencing) })));
const __VLS_202 = __VLS_201(Object.assign({ 'onClick': {} }, { type: "primary", loading: (__VLS_ctx.inferencing) }), ...__VLS_functionalComponentArgsRest(__VLS_201));
let __VLS_204;
let __VLS_205;
let __VLS_206;
const __VLS_207 = {
    onClick: (__VLS_ctx.startInference)
};
__VLS_203.slots.default;
var __VLS_203;
var __VLS_199;
var __VLS_163;
if (__VLS_ctx.inferenceResults.length > 0) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(Object.assign({ class: "inference-results" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h4, __VLS_intrinsicElements.h4)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(Object.assign({ class: "results-grid" }));
    for (const [result, index] of __VLS_getVForSourceType((__VLS_ctx.inferenceResults))) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(Object.assign({ key: (index) }, { class: "result-item" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.img)({
            src: (result),
            alt: (`Result ${index + 1}`),
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(Object.assign({ class: "result-actions" }));
        const __VLS_208 = {}.ElButton;
        /** @type {[typeof __VLS_components.ElButton, typeof __VLS_components.elButton, typeof __VLS_components.ElButton, typeof __VLS_components.elButton, ]} */ ;
        // @ts-ignore
        const __VLS_209 = __VLS_asFunctionalComponent(__VLS_208, new __VLS_208(Object.assign({ 'onClick': {} }, { size: "small" })));
        const __VLS_210 = __VLS_209(Object.assign({ 'onClick': {} }, { size: "small" }), ...__VLS_functionalComponentArgsRest(__VLS_209));
        let __VLS_212;
        let __VLS_213;
        let __VLS_214;
        const __VLS_215 = {
            onClick: (...[$event]) => {
                if (!(__VLS_ctx.inferenceResults.length > 0))
                    return;
                __VLS_ctx.downloadResult(result, index);
            }
        };
        __VLS_211.slots.default;
        var __VLS_211;
    }
}
var __VLS_159;
var __VLS_3;
/** @type {__VLS_StyleScopedClasses['ai-module']} */ ;
/** @type {__VLS_StyleScopedClasses['tab-content']} */ ;
/** @type {__VLS_StyleScopedClasses['tab-content']} */ ;
/** @type {__VLS_StyleScopedClasses['training-progress']} */ ;
/** @type {__VLS_StyleScopedClasses['progress-info']} */ ;
/** @type {__VLS_StyleScopedClasses['tab-content']} */ ;
/** @type {__VLS_StyleScopedClasses['inference-results']} */ ;
/** @type {__VLS_StyleScopedClasses['results-grid']} */ ;
/** @type {__VLS_StyleScopedClasses['result-item']} */ ;
/** @type {__VLS_StyleScopedClasses['result-actions']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            activeTab: activeTab,
            processing: processing,
            training: training,
            inferencing: inferencing,
            trainingProgress: trainingProgress,
            currentEpoch: currentEpoch,
            currentLoss: currentLoss,
            inferenceResults: inferenceResults,
            datasetForm: datasetForm,
            trainingForm: trainingForm,
            inferenceForm: inferenceForm,
            selectDatasetPath: selectDatasetPath,
            selectModelPath: selectModelPath,
            processDataset: processDataset,
            startTraining: startTraining,
            stopTraining: stopTraining,
            startInference: startInference,
            downloadResult: downloadResult,
        };
    },
    emits: {},
    __typeProps: {},
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
    emits: {},
    __typeProps: {},
});
; /* PartiallyEnd: #4569/main.vue */
