import { Navigate, Outlet } from "react-router-dom";

import { ROUTES } from "@/routes/routeConfig";

import { useAuth } from "../context/useAuth";

/**
 * Wraps public-only routes (login) — an already-authenticated user
 * hitting /login is sent straight to the dashboard instead of seeing
 * the form again.
 */
export function RedirectIfAuthenticated() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return null;
  }

  if (isAuthenticated) {
    return <Navigate to={ROUTES.DASHBOARD} replace />;
  }

  return <Outlet />;
}
