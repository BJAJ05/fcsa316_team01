import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Where the Django dev server runs. Override with the BACKEND_URL environment variable.
const backendUrl = process.env.BACKEND_URL ?? 'http://127.0.0.1:8000'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Forward API and uploaded-file requests to Django, so the browser sees one
    // site (no CORS setup needed in development).
    proxy: {
      '/api': backendUrl,
      '/media': backendUrl,
    },
  },
})
