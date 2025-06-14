#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod ai_engine;
mod models;
mod utils;

use ai_engine::{ModelManager, GenerationRequest, GenerationResult};
use models::{SkinGenerator, ItemTextureGenerator};
use tauri::Manager;

#[tauri::command]
async fn generate_skin(prompt: String, model_path: String) -> Result<GenerationResult, String> {
    let manager = ModelManager::new();
    let request = GenerationRequest {
        prompt,
        model_path,
        output_size: (64, 64),
        model_type: "skin".to_string(),
    };
    
    manager.generate(request).await.map_err(|e| e.to_string())
}

#[tauri::command]
async fn generate_item_texture(prompt: String, model_path: String) -> Result<GenerationResult, String> {
    let manager = ModelManager::new();
    let request = GenerationRequest {
        prompt,
        model_path,
        output_size: (32, 32),
        model_type: "item".to_string(),
    };
    
    manager.generate(request).await.map_err(|e| e.to_string())
}

#[tauri::command]
async fn load_model(model_path: String, model_type: String) -> Result<bool, String> {
    let manager = ModelManager::new();
    manager.load_model(&model_path, &model_type).await.map_err(|e| e.to_string())
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_dialog::init())
        .invoke_handler(tauri::generate_handler![
            generate_skin,
            generate_item_texture,
            load_model
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}