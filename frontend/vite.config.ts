import { defineConfig } from 'vite';
import { tanstackStart } from '@tanstack/react-start/plugin/vite';
import { TanStackRouterVite } from '@tanstack/router-plugin/vite'; // Import from here
import path from 'path';

export default defineConfig({
  plugins: [
    TanStackRouterVite({
      routesDirectory: './routes',
    }),
    tanstackStart(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './'),
    },
  },
});
