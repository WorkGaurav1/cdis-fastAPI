/**
 * -----------------------------------------------------------------------------
 * File: navigationConfig.ts
 * -----------------------------------------------------------------------------
 *
 * Layer:
 * Configuration
 *
 * Purpose:
 * Centralize all application navigation definitions.
 *
 * Responsibilities:
 * - Define the navigation model.
 * - Define sidebar navigation items.
 * - Provide a single source of truth for application navigation.
 *
 * Not Responsible For:
 * - Rendering navigation.
 * - Routing.
 * - Authentication.
 * - Authorization.
 *
 * Dependencies:
 * - ROUTES
 *
 * Consumers:
 * - Sidebar
 * - Breadcrumbs
 * - Mobile Navigation
 * - Future Permission Guards
 *
 * Pattern:
 * Centralized Navigation Configuration
 * -----------------------------------------------------------------------------
 */

import type { LucideIcon } from "lucide-react";
import { Settings as SettingsIcon } from "lucide-react";

import { chartsModule } from "@/features/charts";
import { dashboardModule } from "@/features/dashboard";
import { graphsModule } from "@/features/graphs";
import { tablesModule } from "@/features/tables";
import { usersModule } from "@/features/users";

import { ROUTES } from "../../routes/routeConfig";
import type { FeatureModule } from "./featureModule";

/**
 * -----------------------------------------------------------------------------
 * Navigation Item
 * -----------------------------------------------------------------------------
 *
 * Represents one navigable item inside the application.
 * -----------------------------------------------------------------------------
 */

export interface NavigationItem {
    label: string;
    path: string;
    icon?: LucideIcon;
    permission?: string;
    children?: NavigationItem[];
}

/**
 * -----------------------------------------------------------------------------
 * Navigation Configuration
 * -----------------------------------------------------------------------------
 *
 * Every pluggable feature contributes its nav item via its FeatureModule
 * (see featureModule.ts and protectedRoutes.tsx, which derive routes from
 * the same list) — the two are always in sync by construction. Settings
 * has no backing feature folder yet, so it stays a plain static entry.
 * -----------------------------------------------------------------------------
 */

function toNavItem(module: FeatureModule): NavigationItem {
    return {
        label: module.label,
        path: module.path,
        icon: module.icon,
        permission: module.permission,
    };
}

const featureModules: FeatureModule[] = [dashboardModule, graphsModule, chartsModule, tablesModule, usersModule];

export const navigationConfig: NavigationItem[] = [
    ...featureModules.map(toNavItem),
    {
        label: "Settings",
        path: ROUTES.SETTINGS,
        icon: SettingsIcon,
    },
];