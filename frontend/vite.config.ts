import { defineConfig } from 'vite';
import { tanstackStart } from '@tanstack/react-start/plugin/vite';
import { tanstackRouterVite } from '@tanstack/router-vite-plugin';
import path from 'path';

export default defineConfig({
  plugins: [
    tanstackRouterVite({
      routesDirectory: './routes',
    }),
    tanstackStart(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './'),
    },
  },
  build: {
    // TanStack Start handles bundling; make sure we don't over-externalize
    rollupOptions: {
      external: ['react-is'],
    },
  },
});
