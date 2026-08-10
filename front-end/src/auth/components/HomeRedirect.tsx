import { Navigate } from "react-router-dom";

import { ROUTES } from "@/routes/routeConfig";

import { useAuth } from "../context/useAuth";

/**
 * Sends "/" to the dashboard or the login page depending on auth state,
 * instead of always bouncing to /login and then immediately bouncing
 * again via RedirectIfAuthenticated for signed-in users.
 */
export function HomeRedirect() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return null;
  }

  return <Navigate to={isAuthenticated ? ROUTES.DASHBOARD : ROUTES.LOGIN} replace />;
}
