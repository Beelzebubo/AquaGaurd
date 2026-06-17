import { defineConfig } from 'vite';
import { tanstackStart } from '@tanstack/react-start/plugin/vite';
import { TanStackRouterVite } from '@tanstack/router-plugin/vite';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

// Recreate __dirname for ES Modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export default defineConfig({
  plugins: [
    TanStackRouterVite({
      routesDirectory: './routes',
    }),
    tanstackStart(),
  ],
  resolve: {
    alias: {
      '@': __dirname, // Now __dirname is safely defined
    },
  },
});
