import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

// App lives at repo root (CLAUDE.md §9). /public is served at /, so processed
// data is fetched from /data/sailor_ego.json (see scripts/build_subgraph.py).
export default defineConfig({
  plugins: [vue(), tailwindcss()],
})
