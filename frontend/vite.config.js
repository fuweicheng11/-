import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Vite 配置：通过代理将 /api 转发到后端
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:7863',
        changeOrigin: true,
      },
      '/sample-image': {
        target: 'http://127.0.0.1:7863',
        changeOrigin: true,
      },
      '/fafu.jpg': {
        target: 'http://127.0.0.1:7863',
        changeOrigin: true,
      },
    }
  }
})
