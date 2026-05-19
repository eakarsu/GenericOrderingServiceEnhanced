import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

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
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8457',
        changeOrigin: true
      }
    }
  }
})
