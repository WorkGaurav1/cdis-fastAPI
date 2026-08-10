import { ChartPie } from "lucide-react";

import type { FeatureModule } from "@/config/navigation/featureModule";
import { ROUTE_SEGMENTS, ROUTES } from "@/routes/routeConfig";

import ChartsPage from "./pages/ChartsPage";

export const chartsModule: FeatureModule = {
  segment: ROUTE_SEGMENTS.CHARTS,
  path: ROUTES.CHARTS,
  element: <ChartsPage />,
  label: "Charts",
  icon: ChartPie,
};
