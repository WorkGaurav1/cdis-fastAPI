import {
  Area,
  AreaChart as RechartsAreaChart,
  CartesianGrid,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { ChartContainer } from "./ChartContainer";

interface AreaChartProps<T extends object> {
  data: T[];
  xKey: Extract<keyof T, string>;
  yKey: Extract<keyof T, string>;
  title?: string;
  height?: number;
  color?: string;
}

export function AreaChart<T extends object>({
  data,
  xKey,
  yKey,
  title,
  height,
  color = "#c10003",
}: AreaChartProps<T>) {
  return (
    <ChartContainer title={title} height={height}>
      <RechartsAreaChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis dataKey={xKey} tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
        <Tooltip />
        <Area type="monotone" dataKey={yKey} stroke={color} fill={color} fillOpacity={0.15} />
      </RechartsAreaChart>
    </ChartContainer>
  );
}
