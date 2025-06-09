// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::process::{Command, Stdio};
use tauri::State;
use tokio::sync::Mutex;
use uuid::Uuid;

#[derive(Debug, Serialize, Deserialize, Clone)]
struct TrainingTask {
    id: String,
    model_type: String,
    status: String,
    progress: f32,
    created_at: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct ModelConfig {
    name: String,
    model_type: String,
    parameters: HashMap<String, serde_json::Value>,
}

type TasksState = Mutex<HashMap<String, TrainingTask>>;

#[tauri::command]
async fn get_tasks(tasks: State<'_, TasksState>) -> Result<Vec<TrainingTask>, String> {
    let tasks_guard = tasks.lock().await;
    Ok(tasks_guard.values().cloned().collect())
}

#[tauri::command]
async fn create_training_task(
    model_type: String,
    _config: ModelConfig,
    tasks: State<'_, TasksState>,
) -> Result<String, String> {
    let task_id = Uuid::new_v4().to_string();
    let task = TrainingTask {
        id: task_id.clone(),
        model_type,
        status: "pending".to_string(),
        progress: 0.0,
        created_at: chrono::Utc::now().to_rfc3339(),
    };

    let mut tasks_guard = tasks.lock().await;
    tasks_guard.insert(task_id.clone(), task);

    Ok(task_id)
}

#[tauri::command]
async fn start_python_script(
    script_name: String,
    args: Vec<String>,
) -> Result<String, String> {
    let cmd = Command::new("python")
        .arg(format!("python/{}.py", script_name))
        .args(args)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to start Python script: {}", e))?;

    let output = cmd.wait_with_output()
        .map_err(|e| format!("Failed to execute Python script: {}", e))?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}

#[tauri::command]
async fn process_dataset(
    dataset_path: String,
    model_type: String,
) -> Result<String, String> {
    start_python_script(
        "dataset_processor".to_string(),
        vec![dataset_path, model_type],
    ).await
}

#[tauri::command]
async fn generate_content(
    model_type: String,
    prompt: String,
    model_path: String,
) -> Result<String, String> {
    start_python_script(
        "inference".to_string(),
        vec![model_type, prompt, model_path],
    ).await
}

fn main() {
    let tasks_state = Mutex::new(HashMap::<String, TrainingTask>::new());

    tauri::Builder::default()
        .manage(tasks_state)
        .invoke_handler(tauri::generate_handler![
            get_tasks,
            create_training_task,
            start_python_script,
            process_dataset,
            generate_content
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}