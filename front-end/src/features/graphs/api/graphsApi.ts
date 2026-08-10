import { apiClient } from "@/api";
import type { User } from "@/auth";

/**
 * Deliberately independent from features/users' and features/table's API
 * modules — features must never depend on each other directly. All three
 * simply call the same public backend endpoint, which is a platform-level
 * contract, not a frontend feature dependency.
 */
export const graphsApi = {
  listUsers(): Promise<{ users: User[] }> {
    return apiClient.get<{ users: User[] }>("/users");
  },
};
