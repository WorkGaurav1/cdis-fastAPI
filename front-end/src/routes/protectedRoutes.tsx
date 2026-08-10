import type { RouteObject } from "react-router-dom";

import type { FeatureModule } from "@/config/navigation/featureModule";
import { chartsModule } from "@/features/charts";
import { dashboardModule } from "@/features/dashboard";
import { graphsModule } from "@/features/graphs";
import { tablesModule } from "@/features/tables";
import { usersModule } from "@/features/users";
import { RequireAuth, RequirePermission } from "@/auth";
import { ProtectedLayout } from "../layouts";

/**
 * Every pluggable feature registers itself here. Deleting a feature
 * folder only requires removing its entry from this array — the route
 * tree and the sidebar (navigationConfig.ts) both derive from it.
 */
const featureModules: FeatureModule[] = [dashboardModule, graphsModule, chartsModule, tablesModule, usersModule];

function toRoute(module: FeatureModule): RouteObject {
  const route: RouteObject = { path: module.segment, element: module.element };

  if (!module.permission) {
    return route;
  }

  return {
    element: <RequirePermission permission={module.permission} />,
    children: [route],
  };
}

export const protectedRoutes: RouteObject[] = [
  {
    element: <RequireAuth />,
    children: [
      {
        element: <ProtectedLayout />,
        children: featureModules.map(toRoute),
      },
    ],
  },
];
