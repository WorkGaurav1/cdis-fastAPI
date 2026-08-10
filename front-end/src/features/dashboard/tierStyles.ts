export type ProjectCountTier = "none" | "veryLow" | "low" | "medium" | "high" | "veryHigh";

/** Bucket a generic count metric into the 6 tiers shown in the Project Distribution legend. */
export function getProjectCountTier(count: number): ProjectCountTier {
  if (count >= 100) return "veryHigh";
  if (count >= 50) return "high";
  if (count >= 20) return "medium";
  if (count >= 5) return "low";
  if (count >= 1) return "veryLow";
  return "none";
}

/** Red monochrome scale anchored on the brand primary — darker means a higher project count. */
export const PROJECT_COUNT_TIER_COLORS: Record<ProjectCountTier, string> = {
  veryHigh: "#7a0002",
  high: "#c10003",
  medium: "#e2434b",
  low: "#f0989c",
  veryLow: "#fbd9da",
  none: "#f1f5f9",
};

export const PROJECT_COUNT_TIER_LABELS: Record<ProjectCountTier, string> = {
  veryHigh: "100+",
  high: "50 - 100",
  medium: "20 - 50",
  low: "5 - 20",
  veryLow: "1 - 5",
  none: "0",
};

/** Display order for the legend, highest tier first. */
export const PROJECT_COUNT_TIER_ORDER: ProjectCountTier[] = ["veryHigh", "high", "medium", "low", "veryLow", "none"];

/**
 * Continuous blue -> cyan -> green -> yellow -> red thermal scale for the
 * Activity Intensity map — an approximation of a raster heatmap using
 * per-state fill color rather than true cross-boundary pixel blending,
 * which would need a different rendering technique (e.g. a canvas
 * heatmap layer) than this primitive's per-feature GeoJSON styling.
 */
const HEATMAP_STOPS: Array<{ stop: number; rgb: [number, number, number] }> = [
  { stop: 0, rgb: [37, 99, 235] },
  { stop: 0.25, rgb: [34, 211, 238] },
  { stop: 0.5, rgb: [74, 222, 128] },
  { stop: 0.75, rgb: [250, 204, 21] },
  { stop: 1, rgb: [239, 68, 68] },
];

export function getHeatmapColor(value: number, maxValue: number): string {
  const t = maxValue > 0 ? Math.min(Math.max(value / maxValue, 0), 1) : 0;

  for (let i = 0; i < HEATMAP_STOPS.length - 1; i += 1) {
    const from = HEATMAP_STOPS[i];
    const to = HEATMAP_STOPS[i + 1];
    if (t >= from.stop && t <= to.stop) {
      const localT = (t - from.stop) / (to.stop - from.stop);
      const r = Math.round(from.rgb[0] + (to.rgb[0] - from.rgb[0]) * localT);
      const g = Math.round(from.rgb[1] + (to.rgb[1] - from.rgb[1]) * localT);
      const b = Math.round(from.rgb[2] + (to.rgb[2] - from.rgb[2]) * localT);
      return `rgb(${String(r)}, ${String(g)}, ${String(b)})`;
    }
  }

  const last = HEATMAP_STOPS[HEATMAP_STOPS.length - 1].rgb;
  return `rgb(${String(last[0])}, ${String(last[1])}, ${String(last[2])})`;
}

/** CSS gradient stops matching getHeatmapColor, for rendering the legend bar. */
export const HEATMAP_GRADIENT_CSS = "linear-gradient(to top, rgb(37,99,235), rgb(34,211,238), rgb(74,222,128), rgb(250,204,21), rgb(239,68,68))";
