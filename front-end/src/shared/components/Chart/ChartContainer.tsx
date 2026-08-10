import type { ReactNode } from "react";
import { ResponsiveContainer } from "recharts";

interface ChartContainerProps {
  title?: string;
  height?: number;
  children: ReactNode;
}

/**
 * Shared shell every chart type renders inside: consistent card
 * styling, optional title, and a ResponsiveContainer so charts resize
 * with their parent rather than needing a fixed pixel width.
 */
export function ChartContainer({ title, height = 300, children }: ChartContainerProps) {
  return (
    <div className="rounded-md border border-gray-200 bg-white p-4">
      {title && <h3 className="mb-3 text-sm font-medium text-gray-700">{title}</h3>}
      <ResponsiveContainer width="100%" height={height}>
        {children}
      </ResponsiveContainer>
    </div>
  );
}
