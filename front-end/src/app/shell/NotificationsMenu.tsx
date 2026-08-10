import { Popover } from "radix-ui";
import { Bell } from "lucide-react";

/**
 * No notifications backend/data model exists yet in this template.
 * Rather than fabricate sample notifications (or a fake unread-count
 * badge), this shows the real state honestly — an empty list, no
 * badge — while still providing the UI pattern a future notifications
 * feature can plug real data into.
 */
function NotificationsMenu() {
    return (
        <Popover.Root>
            <Popover.Trigger asChild>
                <button
                    type="button"
                    aria-label="Notifications"
                    className="rounded-md p-2 text-slate-400 hover:bg-white/5 hover:text-white"
                >
                    <Bell aria-hidden="true" className="h-5 w-5" />
                </button>
            </Popover.Trigger>
            <Popover.Portal>
                <Popover.Content
                    align="end"
                    sideOffset={8}
                    className="z-50 w-64 rounded-md border border-gray-200 bg-white p-4 shadow-lg"
                >
                    <p className="text-sm text-gray-500">No notifications yet.</p>
                </Popover.Content>
            </Popover.Portal>
        </Popover.Root>
    );
}

export default NotificationsMenu;
