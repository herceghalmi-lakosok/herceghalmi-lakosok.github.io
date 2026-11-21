import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Relatív alap: a /nyitott/koltsegvetes/ almappában is működik
export default defineConfig({
  base: './',
  plugins: [react()],
})
