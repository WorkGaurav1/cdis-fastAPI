/**
 * -----------------------------------------------------------------------------
 * File: featureModule.ts
 * -----------------------------------------------------------------------------
 *
 * Layer:
 * Configuration
 *
 * Purpose:
 * Let a feature describe its own route and sidebar presence in one place,
 * so protectedRoutes.tsx and navigationConfig.ts stay in sync by
 * construction instead of by two hand-typed entries.
 *
 * Not Responsible For:
 * - Rendering navigation or routes.
 * - Authentication.
 *
 * Consumers:
 * - protectedRoutes.tsx
 * - navigationConfig.ts
 * -----------------------------------------------------------------------------
 */

import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

export interface FeatureModule {
  /** Route segment relative to the protected route tree, e.g. "dashboard". */
  segment: string;
  /** Absolute application path, e.g. "/dashboard" — used for nav links. */
  path: string;
  element: ReactNode;
  label: string;
  icon?: LucideIcon;
  /** When set, the route and nav item are both gated behind this permission. */
  permission?: string;
}
