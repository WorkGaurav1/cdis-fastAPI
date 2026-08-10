import {
  CartesianGrid,
  Line,
  LineChart as RechartsLineChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { ChartContainer } from "./ChartContainer";

interface LineChartProps<T extends object> {
  data: T[];
  xKey: Extract<keyof T, string>;
  yKey: Extract<keyof T, string>;
  title?: string;
  height?: number;
  color?: string;
}

export function LineChart<T extends object>({
  data,
  xKey,
  yKey,
  title,
  height,
  color = "#c10003",
}: LineChartProps<T>) {
  return (
    <ChartContainer title={title} height={height}>
      <RechartsLineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis dataKey={xKey} tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
        <Tooltip />
        <Line type="monotone" dataKey={yKey} stroke={color} strokeWidth={2} dot={{ r: 3 }} />
      </RechartsLineChart>
    </ChartContainer>
  );
}
