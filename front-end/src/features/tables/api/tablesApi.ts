import { apiClient } from "@/api";
import type { User } from "@/auth";

/**
 * Deliberately independent from the other features' API modules —
 * features must never depend on each other directly. All of them
 * simply call the same public backend endpoint, which is a
 * platform-level contract, not a frontend feature dependency.
 */
export const tablesApi = {
  listUsers(): Promise<{ users: User[] }> {
    return apiClient.get<{ users: User[] }>("/users");
  },
};
