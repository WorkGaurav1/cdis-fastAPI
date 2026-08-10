import { apiClient } from "@/api";
import type { User } from "@/auth";

export const userApi = {
  list(): Promise<{ users: User[] }> {
    return apiClient.get<{ users: User[] }>("/users");
  },
};
