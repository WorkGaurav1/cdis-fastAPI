import { Navigate, Outlet } from "react-router-dom";

import { ROUTES } from "@/routes/routeConfig";

import { usePermission } from "../hooks/usePermission";

interface RequirePermissionProps {
  permission: string | string[];
}

/**
 * Route-level guard: blocks navigation into the wrapped route tree
 * unless the user holds at least one of the given permissions. Must be
 * nested inside RequireAuth — it assumes a user is already loaded, it
 * doesn't check authentication itself.
 */
export function RequirePermission({ permission }: RequirePermissionProps) {
  const allowed = usePermission(permission);

  if (!allowed) {
    return <Navigate to={ROUTES.FORBIDDEN} replace />;
  }

  return <Outlet />;
}
