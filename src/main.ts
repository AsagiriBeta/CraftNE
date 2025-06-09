import { createApp } from "vue";
import { createRouter, createWebHistory } from "vue-router";
import { createPinia } from "pinia";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import * as ElementPlusIconsVue from "@element-plus/icons-vue";

import App from "./App.vue";
import Home from "./views/Home.vue";
import MapGenerator from "./views/MapGenerator.vue";
import SkinGenerator from "./views/SkinGenerator.vue";
import TextureGenerator from "./views/TextureGenerator.vue";

const routes = [
  { path: "/", component: Home },
  { path: "/map", component: MapGenerator },
  { path: "/skin", component: SkinGenerator },
  { path: "/texture", component: TextureGenerator },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

const app = createApp(App);
const pinia = createPinia();

// Register ElementPlus icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component);
}

app.use(router);
app.use(pinia);
app.use(ElementPlus);
app.mount("#app");