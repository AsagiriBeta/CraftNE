import { invoke } from '@tauri-apps/api/core'
import { open } from '@tauri-apps/plugin-dialog'

export interface GenerationResult {
  success: boolean
  image_data?: number[]
  error_message?: string
  generation_time: number
}

export const useModelManager = () => {
  const selectModelFile = async (): Promise<string | null> => {
    const selected = await open({
      multiple: false,
      filters: [
        {
          name: 'Model Files',
          extensions: ['pt', 'pth', 'safetensors', 'ckpt']
        }
      ]
    })
    
    return Array.isArray(selected) ? selected[0] : selected
  }

  const generateSkin = async (prompt: string, modelPath: string): Promise<GenerationResult> => {
    return await invoke('generate_skin', { prompt, modelPath })
  }

  const generateItemTexture = async (prompt: string, modelPath: string): Promise<GenerationResult> => {
    return await invoke('generate_item_texture', { prompt, modelPath })
  }

  const loadModel = async (modelPath: string, modelType: string): Promise<boolean> => {
    return await invoke('load_model', { modelPath, modelType })
  }

  return {
    selectModelFile,
    generateSkin,
    generateItemTexture,
    loadModel
  }
}