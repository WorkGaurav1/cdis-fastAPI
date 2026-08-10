import { Home } from "lucide-react";

import type { FeatureModule } from "@/config/navigation/featureModule";
import { ROUTE_SEGMENTS, ROUTES } from "@/routes/routeConfig";

import DashboardPage from "./pages/DashboardPage";

export const dashboardModule: FeatureModule = {
  segment: ROUTE_SEGMENTS.DASHBOARD,
  path: ROUTES.DASHBOARD,
  element: <DashboardPage />,
  label: "Dashboard",
  icon: Home,
};
