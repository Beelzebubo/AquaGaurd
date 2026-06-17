import { defineConfig } from 'vite';
import { tanstackStart } from '@tanstack/react-start/plugin/vite';

export default defineConfig({
  plugins: [tanstackStart()], // Ensure the plugin is here!
  build: {
    rollupOptions: {
      // Point Vite to your actual entry file (usually src/main.tsx or src/entry-client.tsx)
      input: 'src/main.tsx', 
      external: ['react-is'],
    },
  },
});
