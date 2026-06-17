import { defineConfig } from 'vite';
import { tanstackStart } from '@tanstack/react-start/plugin/vite';
import { nitro } from 'nitro/vite';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  resolve: {
    tsconfigPaths: true,
  },
  plugins: [
    tailwindcss(),
    tanstackStart({
      srcDirectory: '.',
      server: {
        entry: './server.ts',
      },
      router: {
        routesDirectory: './routes',
      },
    }),
    nitro({ preset: 'node' }),
  ],
});
