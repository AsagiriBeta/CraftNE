pub mod model_manager;
pub mod diffusion;

pub use model_manager::*;
pub use diffusion::*;

use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct GenerationRequest {
    pub prompt: String,
    pub model_path: String,
    pub output_size: (u32, u32),
    pub model_type: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GenerationResult {
    pub success: bool,
    pub image_data: Option<Vec<u8>>,
    pub error_message: Option<String>,
    pub generation_time: f64,
}