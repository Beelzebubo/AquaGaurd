import { defineConfig } from "@lovable.dev/vite-tanstack-config";

export default defineConfig({
  tanstackStart: {
    srcDirectory: "./frontend",
    routesDirectory: "./routes",
    router: {
      entry: "./router",
    },
    server: {
      entry: "./server",
    },
  } as Record<string, unknown>,
  vite: {
    resolve: {
      alias: {
        "@": `${process.cwd()}/frontend`,
      },
    },
  },
});
