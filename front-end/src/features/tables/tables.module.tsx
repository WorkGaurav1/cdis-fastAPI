import { Table2 } from "lucide-react";

import type { FeatureModule } from "@/config/navigation/featureModule";
import { ROUTE_SEGMENTS, ROUTES } from "@/routes/routeConfig";

import TablesPage from "./pages/TablesPage";

export const tablesModule: FeatureModule = {
  segment: ROUTE_SEGMENTS.TABLES,
  path: ROUTES.TABLES,
  element: <TablesPage />,
  label: "Table",
  icon: Table2,
};
