import { defineConfig } from "@lovable.dev/vite-tanstack-config";

export default defineConfig({
  tanstackStart: {
    routesDirectory: "./src/routes",
    router: { entry: "../frontend/router.tsx" },
    server: { entry: "../frontend/server.ts" },
  } as Record<string, unknown>,
  vite: {
    resolve: {
      alias: {
        "@": `${process.cwd()}/frontend`,
      },
    },
  },
});
