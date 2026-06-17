import { defineConfig } from 'vite';
import { tanstackStart } from '@tanstack/react-start/plugin/vite';
import { TanStackRouterVite } from '@tanstack/router-plugin/vite';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export default defineConfig({
  plugins: [
    TanStackRouterVite({
      // We are pointing it explicitly to the 'routes' folder in the root
      routesDirectory: path.resolve(__dirname, 'routes'),
                       generatedRouteTree: path.resolve(__dirname, 'routeTree.gen.ts'),
    }),
    tanstackStart(),
  ],
  resolve: {
    alias: {
      '@': __dirname,
    },
  },
});
