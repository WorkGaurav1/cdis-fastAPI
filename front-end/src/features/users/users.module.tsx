import { Users as UsersIcon } from "lucide-react";

import type { FeatureModule } from "@/config/navigation/featureModule";
import { ROUTE_SEGMENTS, ROUTES } from "@/routes/routeConfig";

import UsersPage from "./pages/UsersPage";

export const usersModule: FeatureModule = {
  segment: ROUTE_SEGMENTS.USERS,
  path: ROUTES.USERS,
  element: <UsersPage />,
  label: "Users",
  icon: UsersIcon,
  permission: "users:read",
};
