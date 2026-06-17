import { defineConfig } from "@tanstack/react-start/config";

export default defineConfig({
    // This forces vinxi to look in 'routes', not 'src/routes'
    routers: {
        client: {
            entry: "./index.tsx", // Ensure this path matches your actual entry file
        },
    },
    vite: {
        // This plugin configuration overrides the internal TanStack defaults
        plugins: [],
    },
});
