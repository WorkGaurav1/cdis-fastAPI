import { seededRandom } from "./randomSeed";

export interface OverviewStat {
  label: string;
  value: number;
  trendPercent: number;
}

function makeStat(seed: string, label: string, base: number, spread: number): OverviewStat {
  const rng = seededRandom(seed);
  return {
    label,
    value: Math.round(base + rng() * spread),
    trendPercent: Math.round(4 + rng() * 20),
  };
}

/** Generic, project-agnostic overview metrics — placeholders for whatever a real project tracks. */
export function generateOverviewStats(): OverviewStat[] {
  return [
    makeStat("overview-total-projects", "Total Projects", 15, 20),
    makeStat("overview-active-users", "Active Users", 800, 900),
    makeStat("overview-total-requests", "Total Requests", 2500, 2000),
  ];
}
