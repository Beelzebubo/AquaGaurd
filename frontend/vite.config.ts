import { defineConfig } from 'vite';
import { tanstackStart } from '@tanstack/react-start/plugin/vite';
import { tanstackRouterVite } from '@tanstack/router-vite-plugin';
import path from 'path';

export default defineConfig({
  plugins: [
    // tanstackStart handles the server-side logic
    tanstackStart(),
    // tanstackRouterVite handles your file-based routing
    tanstackRouterVite({
      routesDirectory: './routes', // Points to your 'routes' folder
    }),
  ],
  resolve: {
    alias: {
      // Maps '@/' to the current directory (the 'frontend' folder)
      '@': path.resolve(__dirname, './'),
    },
  },
  build: {
    rollupOptions: {
      // Bypasses the specific module resolution error for react-is
      external: ['react-is'],
    },
  },
});
