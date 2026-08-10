// src/config/env.ts

/**
 * Supported application environments.
 */
export type AppEnvironment =
  | "development"
  | "testing"
  | "staging"
  | "production";

/**
 * Environment contract.
 */
export interface Environment {
  appName: string;
  appEnv: AppEnvironment;
  apiBaseUrl: string;
}

/**
 * Allowed environment values.
 */
const VALID_ENVIRONMENTS: AppEnvironment[] = [
  "development",
  "testing",
  "staging",
  "production",
];

/**
 * Read raw environment variables.
 */
const appName = import.meta.env.VITE_APP_NAME;
const appEnv = import.meta.env.VITE_APP_ENV;
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

/**
 * Validate required variables.
 */
if (!appName) {
  throw new Error(
    "[Configuration Error] Missing required environment variable: VITE_APP_NAME"
  );
}

if (!appEnv) {
  throw new Error(
    "[Configuration Error] Missing required environment variable: VITE_APP_ENV"
  );
}

if (!apiBaseUrl) {
  throw new Error(
    "[Configuration Error] Missing required environment variable: VITE_API_BASE_URL"
  );
}

/**
 * Validate environment value.
 */
if (!VALID_ENVIRONMENTS.includes(appEnv as AppEnvironment)) {
  throw new Error(
    `[Configuration Error] Invalid VITE_APP_ENV: "${appEnv}". Valid values are: ${VALID_ENVIRONMENTS.join(
      ", "
    )}`
  );
}

/**
 * Export validated configuration.
 */
export const env: Environment = {
  appName,
  appEnv: appEnv as AppEnvironment,
  apiBaseUrl,
};