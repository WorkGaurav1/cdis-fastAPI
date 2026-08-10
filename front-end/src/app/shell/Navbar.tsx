/**
 * -----------------------------------------------------------------------------
 * File: Navbar.tsx
 * Layer: Application Shell
 *
 * Purpose:
 * Provides the top navigation bar for the application.
 *
 * Responsibilities:
 * - Render the application header.
 * - Provide the mobile navigation toggle.
 * - Compose navigation search, notifications, and the account menu.
 *
 * Not Responsible For:
 * - Authentication.
 * - Routing.
 * - Business Logic.
 * -----------------------------------------------------------------------------
 */

import { Menu, Sun } from "lucide-react";

import NavSearch from "./NavSearch";
import NotificationsMenu from "./NotificationsMenu";
import ProfileMenu from "./ProfileMenu";

interface NavbarProps {
    onMenuClick: () => void;
}

function Navbar({ onMenuClick }: NavbarProps) {
    return (
        <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b border-white/10 bg-slate-900 px-4 md:px-6">
            <button
                type="button"
                onClick={onMenuClick}
                aria-label="Open navigation menu"
                className="rounded-md p-2 text-slate-400 hover:bg-white/5 hover:text-white md:hidden"
            >
                <Menu aria-hidden="true" className="h-5 w-5" />
            </button>

            <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-white p-1 shadow-sm">
                <img src="/cdis_logo.png" alt="CDIS" className="h-full w-full object-contain" />
            </span>

            <select
                defaultValue="CDIS Standard Project"
                aria-label="Project"
                className="hidden rounded-md border border-white/10 bg-white/5 px-3 py-1.5 text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-primary/40 sm:block"
            >
                <option>CDIS Standard Project</option>
            </select>

            <div className="ml-auto flex items-center gap-2">
                <NavSearch />
                <NotificationsMenu />

                {/*
                  Decorative only — a real light/dark toggle would mean
                  theming every page in the app, not just this chrome,
                  which is out of scope here. Left as a visible affordance
                  rather than silently dropped, but intentionally inert.
                */}
                <button
                    type="button"
                    aria-label="Toggle theme"
                    className="hidden rounded-md p-2 text-slate-400 hover:bg-white/5 hover:text-white sm:block"
                >
                    <Sun aria-hidden="true" className="h-5 w-5" />
                </button>

                <ProfileMenu />
            </div>
        </header>
    );
}

export default Navbar;
