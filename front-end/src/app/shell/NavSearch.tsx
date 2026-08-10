import { useEffect, useRef, useState } from "react";
import { Popover } from "radix-ui";
import { Search } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { hasPermission, useAuth } from "@/auth";

import { navigationConfig } from "../../config/navigation/navigationConfig.ts";

/**
 * There's no searchable data/backend endpoint in this template yet — a
 * text input that appeared to "search" but silently did nothing would
 * be dishonest UI. What this searches instead is real: the app's own
 * navigation, filtered by what the current user can actually access.
 */
function NavSearch() {
    const [query, setQuery] = useState("");
    const navigate = useNavigate();
    const { user } = useAuth();
    const inputRef = useRef<HTMLInputElement>(null);

    // The ⌘K/Ctrl+K hint next to the input is a real shortcut, not
    // decoration — it focuses the field from anywhere in the app.
    useEffect(() => {
        function handleKeyDown(event: KeyboardEvent) {
            if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
                event.preventDefault();
                inputRef.current?.focus();
            }
        }
        window.addEventListener("keydown", handleKeyDown);
        return () => { window.removeEventListener("keydown", handleKeyDown); };
    }, []);

    const accessibleItems = navigationConfig.filter(
        (item) => !item.permission || hasPermission(user, item.permission),
    );

    const results = query.trim()
        ? accessibleItems.filter((item) => item.label.toLowerCase().includes(query.trim().toLowerCase()))
        : [];

    function handleSelect(path: string) {
        setQuery("");
        navigate(path);
    }

    return (
        <Popover.Root open={results.length > 0}>
            <Popover.Anchor asChild>
                <div className="relative w-40 sm:w-72">
                    <Search
                        aria-hidden="true"
                        className="pointer-events-none absolute inset-y-0 left-2.5 my-auto h-4 w-4 text-slate-500"
                    />
                    <input
                        ref={inputRef}
                        type="search"
                        value={query}
                        onChange={(event) => { setQuery(event.target.value); }}
                        placeholder="Search anything..."
                        aria-label="Search navigation"
                        className="w-full rounded-md border border-white/10 bg-white/5 py-1.5 pl-8 pr-12 text-sm text-white placeholder:text-slate-500 focus:border-primary focus:bg-slate-800 focus:outline-none"
                    />
                    <kbd className="pointer-events-none absolute inset-y-0 right-2 my-auto hidden h-fit rounded border border-white/10 px-1.5 py-0.5 text-[10px] font-medium text-slate-500 sm:block">
                        &#8984;K
                    </kbd>
                </div>
            </Popover.Anchor>
            <Popover.Portal>
                <Popover.Content
                    onOpenAutoFocus={(event) => { event.preventDefault(); }}
                    className="z-50 w-56 rounded-md border border-gray-200 bg-white p-1 shadow-lg"
                >
                    <ul>
                        {results.map((item) => (
                            <li key={item.path}>
                                <button
                                    type="button"
                                    onClick={() => { handleSelect(item.path); }}
                                    className="block w-full rounded-md px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-100"
                                >
                                    {item.label}
                                </button>
                            </li>
                        ))}
                    </ul>
                </Popover.Content>
            </Popover.Portal>
        </Popover.Root>
    );
}

export default NavSearch;
