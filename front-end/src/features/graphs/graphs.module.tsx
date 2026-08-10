import { LineChart } from "lucide-react";

import type { FeatureModule } from "@/config/navigation/featureModule";
import { ROUTE_SEGMENTS, ROUTES } from "@/routes/routeConfig";

import GraphsPage from "./pages/GraphsPage";

export const graphsModule: FeatureModule = {
  segment: ROUTE_SEGMENTS.GRAPHS,
  path: ROUTES.GRAPHS,
  element: <GraphsPage />,
  label: "Graphs",
  icon: LineChart,
};
