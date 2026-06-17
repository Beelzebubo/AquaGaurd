import { defineConfig } from 'vite';
import { tanstackStart } from '@tanstack/react-start/plugin/vite';

export default defineConfig({
  plugins: [tanstackStart()],
  build: {
    rollupOptions: {
     
      input: 'start.ts',
      external: ['react-is'],
    },
  },
});
