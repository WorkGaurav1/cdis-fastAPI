import {
  Bar,
  BarChart as RechartsBarChart,
  CartesianGrid,
  Cell,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { ChartContainer } from "./ChartContainer";

interface BarChartProps<T extends object> {
  data: T[];
  xKey: Extract<keyof T, string>;
  yKey: Extract<keyof T, string>;
  title?: string;
  height?: number;
  /** Matches the --color-primary value in globals.css's @theme block. Ignored when `colors` is set. */
  color?: string;
  /** Per-bar colors, cycling if shorter than `data` — for categorical (not sequential) bars. */
  colors?: string[];
}

export function BarChart<T extends object>({
  data,
  xKey,
  yKey,
  title,
  height,
  color = "#c10003",
  colors,
}: BarChartProps<T>) {
  return (
    <ChartContainer title={title} height={height}>
      <RechartsBarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis dataKey={xKey} tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
        <Tooltip />
        <Bar dataKey={yKey} fill={color} radius={[4, 4, 0, 0]}>
          {colors && data.map((_, index) => <Cell key={index} fill={colors[index % colors.length]} />)}
        </Bar>
      </RechartsBarChart>
    </ChartContainer>
  );
}
