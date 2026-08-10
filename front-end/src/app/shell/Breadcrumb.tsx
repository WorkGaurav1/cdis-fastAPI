import { useLocation } from "react-router-dom";

import { navigationConfig } from "../../config/navigation/navigationConfig.ts";
import { ROUTES } from "../../routes/routeConfig.ts";

/**
 * Derives the current section's label from navigationConfig — the
 * single source of truth for nav labels — rather than a separate
 * route-title map that could drift out of sync with it.
 *
 * Only shows a single current-section crumb for now: nothing in this
 * template has nested routes yet (e.g. /users/:id), so a multi-level
 * trail would have nowhere real to point.
 */
function Breadcrumb() {
    const location = useLocation();

    if (location.pathname === ROUTES.DASHBOARD) {
        return null;
    }

    const current = navigationConfig.find((item) => item.path === location.pathname);

    if (!current) {
        return null;
    }

    return (
        <nav aria-label="Breadcrumb" className="mb-4 text-sm text-gray-500">
            <ol className="flex items-center gap-2">
                <li>Dashboard</li>
                <li aria-hidden="true">/</li>
                <li className="font-medium text-gray-900">{current.label}</li>
            </ol>
        </nav>
    );
}

export default Breadcrumb;
