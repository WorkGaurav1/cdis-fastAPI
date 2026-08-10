import { Navigate, Outlet, useLocation } from "react-router-dom";

import { ROUTES } from "@/routes/routeConfig";

import { useAuth } from "../context/useAuth";

/**
 * Wraps protected route trees. Redirects to /login (preserving the
 * attempted location so login can return the user there) unless the
 * session-restore check has confirmed the user is authenticated.
 */
export function RequireAuth() {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return null;
  }

  if (!isAuthenticated) {
    return <Navigate to={ROUTES.LOGIN} replace state={{ from: location }} />;
  }

  return <Outlet />;
}
