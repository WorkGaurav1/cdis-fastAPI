import { useState } from "react";
import { Outlet } from "react-router-dom";

import Breadcrumb from "./Breadcrumb";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";

function AppShell() {
    const [mobileNavOpen, setMobileNavOpen] = useState(false);
    const [collapsed, setCollapsed] = useState(false);

    return (
        <div className="min-h-screen bg-gray-50">
            <Sidebar
                mobileOpen={mobileNavOpen}
                onMobileOpenChange={setMobileNavOpen}
                collapsed={collapsed}
                onCollapsedChange={setCollapsed}
            />

            <div className={collapsed ? "md:pl-20" : "md:pl-64"}>
                <Navbar onMenuClick={() => { setMobileNavOpen(true); }} />

                <main className="p-4 md:p-6">
                    <Breadcrumb />
                    <Outlet />
                </main>
            </div>
        </div>
    );
}

export default AppShell;
