import { PROJECT_COUNT_TIER_COLORS, PROJECT_COUNT_TIER_LABELS, PROJECT_COUNT_TIER_ORDER } from "../tierStyles";

interface MapLegendProps {
  title: string;
}

export function MapLegend({ title }: MapLegendProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white/95 p-3 shadow-md">
      <div className="mb-2 text-xs font-semibold text-gray-700">{title}</div>
      <div className="space-y-1.5">
        {PROJECT_COUNT_TIER_ORDER.map((tier) => (
          <div key={tier} className="flex items-center gap-2 text-xs text-gray-600">
            <span
              aria-hidden="true"
              className="h-3 w-3 flex-shrink-0 rounded-sm border border-black/5"
              style={{ backgroundColor: PROJECT_COUNT_TIER_COLORS[tier] }}
            />
            {PROJECT_COUNT_TIER_LABELS[tier]}
          </div>
        ))}
      </div>
    </div>
  );
}
