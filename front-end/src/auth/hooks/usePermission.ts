import { useAuth } from "../context/useAuth";
import type { User } from "../types";

/**
 * Plain (non-hook) permission check — mirrors the backend's
 * requirePermission semantics: true if the user holds at least one of
 * the given permissions. Always checks permissions, never role names —
 * same hybrid-RBAC rule the backend guards follow.
 *
 * Exported separately from usePermission so callers who already have a
 * `user` (e.g. checking permissions per-item in a list) can reuse this
 * logic without calling a hook inside a loop, which would violate the
 * Rules of Hooks.
 */
export function hasPermission(user: User | null, permission: string | string[]): boolean {
  if (!user) {
    return false;
  }

  const required = Array.isArray(permission) ? permission : [permission];

  return required.some((needed) => user.permissions.includes(needed));
}

export function usePermission(permission: string | string[]): boolean {
  const { user } = useAuth();

  return hasPermission(user, permission);
}
