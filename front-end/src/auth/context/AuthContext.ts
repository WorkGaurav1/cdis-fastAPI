import { createContext } from "react";

import type { LoginRequest, User } from "../types";

/**
 * Authentication context contract.
 *
 * Responsibilities:
 * - Define the authentication state available across the application.
 * - Define authentication actions.
 *
 * Not Responsible For:
 * - API calls
 * - Token storage
 * - Authentication logic
 * - Route protection
 */

export interface AuthContextValue {
  /**
   * Currently authenticated user.
   */
  user: User | null;

  /**
   * Whether the user is authenticated.
   */
  isAuthenticated: boolean;

  /**
   * Indicates whether authentication state is being initialized.
   */
  loading: boolean;

  /**
   * Sign in the user.
   */
  login(credentials: LoginRequest): Promise<void>;

  /**
   * Sign out the current user.
   */
  logout(): Promise<void>;
}

export const AuthContext = createContext<AuthContextValue | undefined>(
  undefined,
);