import { HEATMAP_GRADIENT_CSS } from "../tierStyles";

interface GradientLegendProps {
  title: string;
  labels: [high: string, medium: string, low: string];
}

export function GradientLegend({ title, labels }: GradientLegendProps) {
  const [high, medium, low] = labels;

  return (
    <div className="rounded-lg border border-gray-200 bg-white/95 p-3 shadow-md">
      <div className="mb-2 text-xs font-semibold text-gray-700">{title}</div>
      <div className="flex items-stretch gap-2">
        <div aria-hidden="true" className="w-2.5 rounded-full" style={{ background: HEATMAP_GRADIENT_CSS }} />
        <div className="flex flex-col justify-between py-0.5 text-xs text-gray-600">
          <span>{high}</span>
          <span>{medium}</span>
          <span>{low}</span>
        </div>
      </div>
    </div>
  );
}
