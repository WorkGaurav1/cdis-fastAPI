import axios, { type InternalAxiosRequestConfig } from "axios";

import { ApiError } from "../apiError";
import type { ApiErrorEnvelope } from "../types";
import { httpClient } from "./httpClient";
import {
  CSRF_COOKIE_NAME,
  CSRF_HEADER_NAME,
  SESSION_EXPIRED_EVENT,
} from "../../auth/constants";
import { getCookie } from "../../shared/utils";

const MUTATING_METHODS = new Set(["post", "put", "patch", "delete"]);

interface RetriableRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

/**
 * Only one refresh call is ever in flight at a time. Without this, N
 * simultaneous 401s (e.g. a page firing several requests at once) would
 * each try to refresh independently — and since refresh tokens rotate
 * on use, the second call would be presenting an already-rotated token,
 * which the backend's reuse-detection treats as theft and revokes the
 * entire session. Every concurrent 401 instead awaits this same promise.
 */
let refreshPromise: Promise<void> | null = null;

function performRefresh(): Promise<void> {
  refreshPromise ??= httpClient
    .post("/auth/refresh", undefined, {
      headers: csrfHeaders(),
    })
    .then(() => undefined)
    .finally(() => {
      refreshPromise = null;
    });

  return refreshPromise;
}

function csrfHeaders(): Record<string, string> {
  const token = getCookie(CSRF_COOKIE_NAME);
  return token ? { [CSRF_HEADER_NAME]: token } : {};
}

function toApiError(error: unknown): ApiError {
  if (axios.isAxiosError<ApiErrorEnvelope>(error)) {
    const envelope = error.response?.data;

    if (envelope && envelope.success === false) {
      return new ApiError(envelope.error.message, envelope.error.code, error.response?.status);
    }

    return new ApiError(
      error.message || "Something went wrong. Please try again.",
      "NETWORK_ERROR",
      error.response?.status,
    );
  }

  return new ApiError("Something went wrong. Please try again.", "UNKNOWN_ERROR", undefined);
}

/**
 * Register all request and response interceptors.
 */
export function registerInterceptors(): void {
  httpClient.interceptors.request.use((config) => {
    const method = config.method?.toLowerCase();

    if (method && MUTATING_METHODS.has(method)) {
      const token = getCookie(CSRF_COOKIE_NAME);

      if (token) {
        config.headers.set(CSRF_HEADER_NAME, token);
      }
    }

    return config;
  }, (error) => Promise.reject(toApiError(error)));

  httpClient.interceptors.response.use(
    (response) => response,
    async (error: unknown) => {
      if (!axios.isAxiosError(error) || !error.config) {
        return Promise.reject(toApiError(error));
      }

      const originalRequest = error.config as RetriableRequestConfig;
      const requestUrl = originalRequest.url ?? "";
      const isAuthBootstrapRequest =
        requestUrl.includes("/auth/refresh") ||
        requestUrl.includes("/auth/login") ||
        requestUrl.includes("/auth/register");

      if (error.response?.status === 401 && !originalRequest._retry && !isAuthBootstrapRequest) {
        originalRequest._retry = true;

        try {
          await performRefresh();
          return httpClient(originalRequest);
        } catch {
          window.dispatchEvent(new CustomEvent(SESSION_EXPIRED_EVENT));
          return Promise.reject(toApiError(error));
        }
      }

      return Promise.reject(toApiError(error));
    },
  );
}
