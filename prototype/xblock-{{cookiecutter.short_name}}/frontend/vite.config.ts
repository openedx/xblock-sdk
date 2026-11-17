import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  return {
    define: {
      global: "globalThis",
      // Don't force NODE_ENV in test mode so vitest can set it to 'test'
      ...(mode !== "test" && {
        "process.env.NODE_ENV": JSON.stringify("production"),
      }),
    },
    root: "src",
    plugins: [react()],
    css: {
      lightningcss: {
        errorRecovery: true, // Otherwise lightningcss fails with var() usage in media queries.
      },
    },
    build: {
      cssMinify: "lightningcss",
      lib: {
        entry: {
          student: resolve(import.meta.dirname, "src/student-ui/main.tsx"),
          studio: resolve(import.meta.dirname, "src/studio-ui/main.tsx"),
        },
        formats: ["es"],
      },
      outDir: resolve(import.meta.dirname, "../src/{{cookiecutter.short_name}}/public"),
      emptyOutDir: true,
    },
    test: {
      globals: true,
      environment: "jsdom",
    },
    resolve: {
      alias: {
        "@": resolve(import.meta.dirname, "src"),
      },
    },
  };
});
