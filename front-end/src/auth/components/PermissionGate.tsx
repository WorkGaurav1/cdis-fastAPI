import type { ReactNode } from "react";

import { usePermission } from "../hooks/usePermission";

interface PermissionGateProps {
  permission: string | string[];
  children: ReactNode;
  /** Rendered instead of children when the permission check fails. Optional — defaults to rendering nothing. */
  fallback?: ReactNode;
}

/**
 * Inline conditional rendering based on permission — for hiding/showing
 * a piece of UI (a nav link, an action button) without blocking
 * navigation. Use RequirePermission instead when the whole route should
 * be blocked.
 */
export function PermissionGate({ permission, children, fallback = null }: PermissionGateProps) {
  const allowed = usePermission(permission);

  return allowed ? children : fallback;
}
