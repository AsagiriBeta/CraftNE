use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::Mutex;
use anyhow::Result;
use candle_core::{Device, Tensor};
use super::{GenerationRequest, GenerationResult};

pub struct ModelManager {
    loaded_models: Arc<Mutex<HashMap<String, Box<dyn ModelInference + Send + Sync>>>>,
    device: Device,
}

pub trait ModelInference {
    fn generate(&self, prompt: &str, size: (u32, u32)) -> Result<Vec<u8>>;
}

impl ModelManager {
    pub fn new() -> Self {
        let device = Device::cuda_if_available(0).unwrap_or(Device::Cpu);
        
        Self {
            loaded_models: Arc::new(Mutex::new(HashMap::new())),
            device,
        }
    }

    pub async fn load_model(&self, model_path: &str, model_type: &str) -> Result<bool> {
        let mut models = self.loaded_models.lock().await;
        
        match model_type {
            "skin" => {
                let model = crate::models::SkinGenerator::load(model_path, &self.device)?;
                models.insert(format!("skin_{}", model_path), Box::new(model));
            },
            "item" => {
                let model = crate::models::ItemTextureGenerator::load(model_path, &self.device)?;
                models.insert(format!("item_{}", model_path), Box::new(model));
            },
            _ => return Err(anyhow::anyhow!("Unknown model type: {}", model_type)),
        }
        
        Ok(true)
    }

    pub async fn generate(&self, request: GenerationRequest) -> Result<GenerationResult> {
        let start_time = std::time::Instant::now();
        let models = self.loaded_models.lock().await;
        
        let model_key = format!("{}_{}", request.model_type, request.model_path);
        
        match models.get(&model_key) {
            Some(model) => {
                match model.generate(&request.prompt, request.output_size) {
                    Ok(image_data) => {
                        let generation_time = start_time.elapsed().as_secs_f64();
                        Ok(GenerationResult {
                            success: true,
                            image_data: Some(image_data),
                            error_message: None,
                            generation_time,
                        })
                    },
                    Err(e) => Ok(GenerationResult {
                        success: false,
                        image_data: None,
                        error_message: Some(e.to_string()),
                        generation_time: start_time.elapsed().as_secs_f64(),
                    }),
                }
            },
            None => Ok(GenerationResult {
                success: false,
                image_data: None,
                error_message: Some("Model not loaded".to_string()),
                generation_time: 0.0,
            }),
        }
    }
}