import path from "node:path";

import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  // Deliberately not the app's full plugin stack (Tailwind, React
  // Compiler babel preset) — neither affects component test
  // correctness, and skipping them keeps the test run fast and simple.
  plugins: [react()],

  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },

  test: {
    environment: "jsdom",
    setupFiles: ["./vitest.setup.ts"],
    include: ["src/**/*.test.{ts,tsx}"],
    env: {
      VITE_APP_NAME: "CDIS",
      VITE_APP_ENV: "development",
      VITE_API_BASE_URL: "http://localhost:4000/api/v1",
    },
    coverage: {
      provider: "v8",
      reporter: ["text", "html", "lcov"],
      include: ["src/**/*.{ts,tsx}"],
      exclude: [
        "src/**/*.test.{ts,tsx}",
        "src/main.tsx",
        "src/vite-env.d.ts",
        "src/**/index.ts",
      ],
      thresholds: {
        lines: 85,
        statements: 85,
        functions: 85,
        branches: 80,

        "src/auth/hooks/usePermission.ts": { lines: 95, statements: 95, functions: 95, branches: 90 },
        "src/auth/components/RequireAuth.tsx": { lines: 95, statements: 95, functions: 95, branches: 90 },
        "src/auth/components/RequirePermission.tsx": { lines: 95, statements: 95, functions: 95, branches: 90 },
        "src/api/client/interceptors.ts": { lines: 95, statements: 95, functions: 95, branches: 90 },
      },
    },
  },
});
