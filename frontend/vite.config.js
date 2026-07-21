import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const frontendPort = Number(process.env.VITE_FRONT_PORT || 3000)
const backendPort = Number(process.env.VITE_BACKEND_PORT || 8000)

export default defineConfig({
  // Tell @vitejs/plugin-react to also transform .js files (default is .jsx only).
  plugins: [react({ include: /\.(mjs|js|jsx|ts|tsx)$/ })],
  // Treat .js as JSX for esbuild (used by Vite's transform pipeline + deps optimizer).
  esbuild: {
    loader: 'jsx',
    include: [/src\/.*\.js$/, /src\/.*\.jsx$/],
    exclude: [],
  },
  optimizeDeps: {
    esbuildOptions: {
      loader: { '.js': 'jsx' },
    },
  },
  server: {
    host: process.env.FRONTEND_HOST || '127.0.0.1',
    port: frontendPort,
    proxy: {
      '/api': {
        target: `http://127.0.0.1:${backendPort}`,
        changeOrigin: true
      }
    }
  }
})
