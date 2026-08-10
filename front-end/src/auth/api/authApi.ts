import { apiClient } from "@/api";

import type { AuthResponse, LoginRequest } from "../types";

export const authApi = {
  login(credentials: LoginRequest): Promise<AuthResponse> {
    return apiClient.post<AuthResponse>("/auth/login", credentials);
  },

  refresh(): Promise<AuthResponse> {
    return apiClient.post<AuthResponse>("/auth/refresh");
  },

  getCurrentUser(): Promise<AuthResponse> {
    return apiClient.get<AuthResponse>("/auth/me");
  },

  logout(): Promise<void> {
    return apiClient.post<void>("/auth/logout");
  },
};
