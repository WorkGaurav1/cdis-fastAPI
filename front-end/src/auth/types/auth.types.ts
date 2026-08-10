/**
 * Login request payload.
 */
export interface LoginRequest {
  email: string;
  password: string;
}

export interface User {
  id: string;
  name: string;
  email: string;
  roles: string[];
  permissions: string[];
}

/**
 * Shape returned by /auth/login, /auth/refresh, and /auth/me. Tokens
 * are never present here — they travel exclusively as httpOnly cookies
 * set by the server, never as JSON the frontend could read or store.
 */
export interface AuthResponse {
  user: User;
}
