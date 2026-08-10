import { Cell, Pie, PieChart as RechartsPieChart, Tooltip } from "recharts";

import { ChartContainer } from "./ChartContainer";

interface PieChartProps<T extends object> {
  data: T[];
  nameKey: Extract<keyof T, string>;
  valueKey: Extract<keyof T, string>;
  title?: string;
  height?: number;
  colors?: string[];
}

/** Matches the brand palette in globals.css's @theme block (primary + 4 logo accents). */
const DEFAULT_COLORS = ["#c10003", "#00a5f1", "#25b146", "#fc7f2d", "#fbc200"];

export function PieChart<T extends object>({
  data,
  nameKey,
  valueKey,
  title,
  height,
  colors = DEFAULT_COLORS,
}: PieChartProps<T>) {
  return (
    <ChartContainer title={title} height={height}>
      <RechartsPieChart>
        <Pie data={data} dataKey={valueKey} nameKey={nameKey} outerRadius="80%" label>
          {data.map((_, index) => (
            <Cell key={index} fill={colors[index % colors.length]} />
          ))}
        </Pie>
        <Tooltip />
      </RechartsPieChart>
    </ChartContainer>
  );
}
