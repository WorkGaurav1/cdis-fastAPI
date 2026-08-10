/**
 * -----------------------------------------------------------------------------
 * File: PublicLayout.tsx
 * Layer: Layout
 *
 * Purpose:
 * Provides the layout for all public pages.
 *
 * Responsibilities:
 * - Render shared public UI.
 * - Render child routes using Outlet.
 *
 * Not Responsible For:
 * - Authentication
 * - Login logic
 * - Navigation decisions
 * -----------------------------------------------------------------------------
 */

import { Outlet } from "react-router-dom";

function PublicLayout() {
    return <Outlet />;
}

export default PublicLayout;