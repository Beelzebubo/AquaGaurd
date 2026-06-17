import { defineConfig } from "@tanstack/start/config";

export default defineConfig({
    // Vinxi uses this to find your routes automatically based on your folder structure
    routers: {
        client: {
            entry: "./index.tsx",
        },
    },
});
