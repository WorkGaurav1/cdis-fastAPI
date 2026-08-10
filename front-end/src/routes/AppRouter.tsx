/**
 * -----------------------------------------------------------------------------
 * File: AppRouter.tsx
 * -----------------------------------------------------------------------------
 *
 * Layer:
 * Routing
 *
 * Purpose:
 * Creates and provides the application's router.
 *
 * Responsibilities:
 * - Create the React Router instance.
 * - Compose public and protected routes.
 * - Register fallback routes.
 * - Provide routing to the application.
 *
 * Not Responsible For:
 * - Authentication.
 * - Authorization.
 * - Layout composition.
 * - Business logic.
 *
 * Dependencies:
 * - publicRoutes
 * - protectedRoutes
 * - NotFoundPage
 *
 * Consumers:
 * - App.tsx
 *
 * Pattern:
 * React Router Data Router
 * -----------------------------------------------------------------------------
 */

// -----------------------------------------------------------------------------
// External Imports
// -----------------------------------------------------------------------------

import {
    createBrowserRouter,
    RouterProvider,
} from "react-router-dom";

// -----------------------------------------------------------------------------
// Internal Imports
// -----------------------------------------------------------------------------

import { publicRoutes } from "./publicRoutes";
import { protectedRoutes } from "./protectedRoutes";
import { ROUTE_SEGMENTS } from "./routeConfig";
import NotFoundPage from "../shared/pages/NotFoundPage";
import ForbiddenPage from "../shared/pages/ForbiddenPage";

// -----------------------------------------------------------------------------
// Router Configuration
// -----------------------------------------------------------------------------

const router = createBrowserRouter([
    ...publicRoutes,

    ...protectedRoutes,

    // Status routes: reachable regardless of auth state, so they live
    // outside both RequireAuth and RedirectIfAuthenticated.
    {
        path: ROUTE_SEGMENTS.FORBIDDEN,
        element: <ForbiddenPage />,
    },
    {
        path: "*",
        element: <NotFoundPage />,
    },
]);

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------

function AppRouter() {
    return <RouterProvider router={router} />;
}

export default AppRouter;