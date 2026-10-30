import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";

// https://vitest.dev/config/
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
    test: {
      globals: true,
      environment: "jsdom",
      onConsoleLog(log) {
        // Paragon needs to update their components. We don't do this.
        if (log.includes("Support for defaultProps will be removed")) {
          return false;
        }
        // MockJax doesn't allow us to suppress this info with the way
        // we import it.
        if (log.includes("Initializing Mockjax and adding methods to jQuery")) {
          return false;
        }
      },
      // Set up our test environment, including adding mockJax to mock out AJAX calls.
      setupFiles: ["testSetup.ts"],
      coverage: {
        provider: "v8",
        enabled: true,
        reporter: ["text", "html"],
        reportsDirectory: "../coverage",
        include: ["**/*.{ts,tsx}"],
      },
      sequence: {
        shuffle: true,
      },
    },
    resolve: {
      alias: {
        "@": resolve(import.meta.dirname, "src"),
      },
    },
  };
});
