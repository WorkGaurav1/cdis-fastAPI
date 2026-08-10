import axios from "axios";

import { appConfig } from "../../config";
import { registerInterceptors } from "./interceptors";

export const httpClient = axios.create({
  baseURL: appConfig.api.baseUrl,
  timeout: appConfig.api.timeout,
  // Authentication is httpOnly cookies, not a bearer header — the
  // browser must be told to send/store cookies on cross-origin requests.
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

registerInterceptors();