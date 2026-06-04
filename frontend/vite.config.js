import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 3000,
    proxy: {
      '/api': backendUrl,
    },
  },
  preview: {
    host: true,
    port: 3000,
    allowedHosts: true,
    proxy: {
      '/api': backendUrl,
    },
  },
})