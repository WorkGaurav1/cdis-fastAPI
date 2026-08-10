/**
 * -----------------------------------------------------------------------------
 * File: Sidebar.tsx
 * Layer: Application Shell
 *
 * Purpose:
 * Renders the application's primary navigation.
 *
 * Responsibilities:
 * - Render navigation items.
 * - Delegate navigation data to configuration.
 * - Present as a static panel on desktop, an accessible slide-over
 *   drawer (Radix Dialog) on mobile.
 * - Support a collapsed (icon-only) desktop state.
 *
 * Not Responsible For:
 * - Route definitions.
 * - Permissions.
 * - Navigation configuration.
 * -----------------------------------------------------------------------------
 */

import { Dialog } from "radix-ui";
import { ChevronsLeft, ChevronsRight } from "lucide-react";
import { NavLink } from "react-router-dom";

import { PermissionGate } from "@/auth";

import { navigationConfig, type NavigationItem } from "../../config/navigation/navigationConfig.ts";

function NavigationLink({
    item,
    onNavigate,
    collapsed,
}: {
    item: NavigationItem;
    onNavigate?: () => void;
    collapsed?: boolean;
}) {
    const Icon = item.icon;

    return (
        <li>
            <NavLink
                to={item.path}
                onClick={onNavigate}
                title={collapsed ? item.label : undefined}
                className={({ isActive }) =>
                    `flex items-center gap-2.5 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                        collapsed ? "justify-center" : ""
                    } ${isActive ? "bg-white/10 text-white" : "text-slate-400 hover:bg-white/5 hover:text-white"}`
                }
            >
                {Icon && <Icon aria-hidden="true" className="h-4 w-4 flex-shrink-0" />}
                {!collapsed && item.label}
            </NavLink>
        </li>
    );
}

function SidebarNav({ onNavigate, collapsed }: { onNavigate?: () => void; collapsed?: boolean }) {
    return (
        <nav className="flex-1 overflow-y-auto">
            <ul className="space-y-1">
                {navigationConfig.map((item: NavigationItem) =>
                    item.permission ? (
                        <PermissionGate key={item.path} permission={item.permission}>
                            <NavigationLink item={item} onNavigate={onNavigate} collapsed={collapsed} />
                        </PermissionGate>
                    ) : (
                        <NavigationLink key={item.path} item={item} onNavigate={onNavigate} collapsed={collapsed} />
                    ),
                )}
            </ul>
        </nav>
    );
}

function SidebarBrand({ collapsed }: { collapsed?: boolean }) {
    return (
        <div className="flex items-center gap-2.5 px-1 py-2">
            <span className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg bg-white p-1 shadow-sm">
                <img src="/cdis_logo.png" alt="CDIS" className="h-full w-full object-contain" />
            </span>
            {!collapsed && (
                <div className="leading-tight">
                    <div className="text-sm font-bold tracking-wide text-white">CDIS</div>
                    <div className="text-[10px] font-semibold tracking-widest text-slate-400">DASHBOARD</div>
                </div>
            )}
        </div>
    );
}

interface SidebarProps {
    mobileOpen: boolean;
    onMobileOpenChange: (open: boolean) => void;
    collapsed: boolean;
    onCollapsedChange: (collapsed: boolean) => void;
}

function Sidebar({ mobileOpen, onMobileOpenChange, collapsed, onCollapsedChange }: SidebarProps) {
    return (
        <>
            {/* Desktop: static, always visible */}
            <aside
                className={`hidden md:fixed md:inset-y-0 md:flex md:flex-col md:border-r md:border-white/10 md:bg-slate-900 md:p-4 md:transition-[width] md:duration-200 ${
                    collapsed ? "md:w-20" : "md:w-64"
                }`}
            >
                <SidebarBrand collapsed={collapsed} />

                <div className="mt-4 flex flex-1 flex-col">
                    <SidebarNav collapsed={collapsed} />
                </div>

                <button
                    type="button"
                    onClick={() => { onCollapsedChange(!collapsed); }}
                    aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
                    className={`flex items-center gap-2 border-t border-white/10 pt-3 text-sm font-medium text-slate-400 hover:text-white ${
                        collapsed ? "justify-center" : ""
                    }`}
                >
                    {collapsed ? (
                        <ChevronsRight aria-hidden="true" className="h-4 w-4" />
                    ) : (
                        <>
                            <ChevronsLeft aria-hidden="true" className="h-4 w-4" />
                            Collapse
                        </>
                    )}
                </button>
            </aside>

            {/* Mobile: accessible slide-over drawer (never collapsed) */}
            <Dialog.Root open={mobileOpen} onOpenChange={onMobileOpenChange}>
                <Dialog.Portal>
                    <Dialog.Overlay className="fixed inset-0 z-40 bg-black/40 md:hidden" />
                    <Dialog.Content className="fixed inset-y-0 left-0 z-50 flex w-64 flex-col bg-slate-900 p-4 shadow-lg md:hidden">
                        <Dialog.Title className="sr-only">Navigation menu</Dialog.Title>
                        <SidebarBrand />
                        <div className="mt-4 flex flex-1 flex-col">
                            <SidebarNav onNavigate={() => { onMobileOpenChange(false); }} />
                        </div>
                    </Dialog.Content>
                </Dialog.Portal>
            </Dialog.Root>
        </>
    );
}

export default Sidebar;
