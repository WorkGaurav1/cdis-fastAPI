/**
 * Builds the small banner + rows hover card used across every map
 * layer (zones, clusters, corridors) — same visual language, just fed
 * different rows per layer type.
 */
export function buildHoverCard(title: string, rows: Array<[label: string, value: string]>): string {
  const rowsHtml = rows
    .map(
      ([label, value]) =>
        `<div class="flex items-center justify-between gap-4 px-2.5 py-1 text-[11px] text-gray-600">` +
        `<span>${label}</span><span class="font-semibold text-gray-900">${value}</span></div>`,
    )
    .join("");

  return (
    `<div class="min-w-[170px] overflow-hidden rounded-md border border-gray-200 bg-white shadow-lg">` +
    `<div class="bg-gray-800 px-2.5 py-1.5 text-[11px] font-semibold tracking-wide text-white">${title}</div>` +
    `${rowsHtml}</div>`
  );
}
