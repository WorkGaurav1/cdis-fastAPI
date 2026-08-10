import { authApi } from "../api";

import type { LoginRequest, User } from "../types";

export const authService = {
  async login(credentials: LoginRequest): Promise<User> {
    const { user } = await authApi.login(credentials);
    return user;
  },

  async getCurrentUser(): Promise<User> {
    const { user } = await authApi.getCurrentUser();
    return user;
  },

  async logout(): Promise<void> {
    await authApi.logout();
  },
};
