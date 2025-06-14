import { defineStore } from 'pinia'
import { save } from '@tauri-apps/plugin-dialog'
import { writeFile } from '@tauri-apps/plugin-fs'

export const useItemStore = defineStore('item', {
  state: () => ({
    generatedTextures: [] as Array<{
      id: string
      prompt: string
      category: string
      style: string
      imageData: string
      timestamp: Date
    }>
  }),

  actions: {
    async saveTexture(imageData: string) {
      const filePath = await save({
        filters: [
          {
            name: 'PNG Images',
            extensions: ['png']
          }
        ],
        defaultPath: 'item_texture.png'
      })

      if (filePath) {
        const base64Data = imageData.split(',')[1]
        const binaryString = atob(base64Data)
        const bytes = new Uint8Array(binaryString.length)
        
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i)
        }

        await writeFile(filePath, bytes)
      }
    },

    addGeneratedTexture(prompt: string, category: string, style: string, imageData: string) {
      this.generatedTextures.push({
        id: Date.now().toString(),
        prompt,
        category,
        style,
        imageData,
        timestamp: new Date()
      })
    }
  }
})