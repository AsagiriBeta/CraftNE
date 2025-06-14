import { defineStore } from 'pinia'
import { save } from '@tauri-apps/plugin-dialog'
import { writeFile } from '@tauri-apps/plugin-fs'

export const useSkinStore = defineStore('skin', {
  state: () => ({
    generatedSkins: [] as Array<{
      id: string
      prompt: string
      imageData: string
      timestamp: Date
    }>
  }),

  actions: {
    async saveSkin(imageData: string) {
      const filePath = await save({
        filters: [
          {
            name: 'PNG Images',
            extensions: ['png']
          }
        ],
        defaultPath: 'minecraft_skin.png'
      })

      if (filePath) {
        // 从base64转换为字节数组
        const base64Data = imageData.split(',')[1]
        const binaryString = atob(base64Data)
        const bytes = new Uint8Array(binaryString.length)
        
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i)
        }

        await writeFile(filePath, bytes)
      }
    },

    addGeneratedSkin(prompt: string, imageData: string) {
      this.generatedSkins.push({
        id: Date.now().toString(),
        prompt,
        imageData,
        timestamp: new Date()
      })
    }
  }
})