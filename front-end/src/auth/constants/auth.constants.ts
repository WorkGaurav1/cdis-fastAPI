/**
 * Must match the backend's cookie/header names exactly
 * (back-end/src/lib/cookies.ts).
 */
export const CSRF_COOKIE_NAME = "csrf_token";
export const CSRF_HEADER_NAME = "x-csrf-token";

/**
 * Dispatched on `window` when a request fails auth even after a silent
 * refresh attempt — the session is definitively over. AuthProvider
 * listens for this to clear its state without every call site needing
 * to know about it.
 */
export const SESSION_EXPIRED_EVENT = "auth:session-expired";

export const AUTH_QUERY_KEYS = {
  currentUser: ["auth", "me"] as const,
};
