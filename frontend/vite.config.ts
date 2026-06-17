import { defineConfig } from 'vite';
import { tanstackRouterVite } from '@tanstack/router-vite-plugin';

export default defineConfig({
  plugins: [
    tanstackRouterVite({
      routesDirectory: './routes', // Tell it to look here instead of src/routes
    }),
  ],
  // ... rest of your config
});
