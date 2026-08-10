import { env } from "./env";

export const appConfig = {
  app: {
    name: env.appName,
    environment: env.appEnv,
  },

  api: {
    baseUrl: env.apiBaseUrl,
    timeout: 30000,
  },
} as const;