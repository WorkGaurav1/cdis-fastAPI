import type { LucideIcon } from "lucide-react";
import { ArrowUp } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string;
  icon: LucideIcon;
  /** Tailwind background class for the icon badge, e.g. "bg-indigo-500". */
  iconBgClassName: string;
  /** Positive percent change shown as an upward trend, e.g. 12 -> "↑ 12% from last month". */
  trendPercent?: number;
}

export function StatCard({ label, value, icon: Icon, iconBgClassName, trendPercent }: StatCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md">
      <div className="flex items-center gap-3">
        <span className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg ${iconBgClassName}`}>
          <Icon aria-hidden="true" className="h-5 w-5 text-white" />
        </span>
        <div>
          <div className="text-xs font-medium text-gray-500">{label}</div>
          <div className="text-xl font-bold text-gray-900">{value}</div>
        </div>
      </div>

      {trendPercent !== undefined && (
        <div className="mt-3 flex items-center gap-1 text-xs">
          <ArrowUp aria-hidden="true" className="h-3 w-3 text-green-600" />
          <span className="font-semibold text-green-600">{trendPercent}%</span>
          <span className="text-gray-400">from last month</span>
        </div>
      )}
    </div>
  );
}
