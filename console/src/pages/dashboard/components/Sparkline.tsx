import { Line } from "@ant-design/plots";
import { useTheme } from "../../../contexts/ThemeContext";

interface SparklineProps {
  data: number[];
  color?: string;
  height?: number;
}

export default function Sparkline({
  data,
  color = "#FF7F16",
  height = 32,
}: SparklineProps) {
  const { isDark } = useTheme();

  if (!data || data.length === 0) {
    return null;
  }

  const chartData = data.map((value, index) => ({ index, value }));

  return (
    <div style={{ height, width: "100%" }}>
      <Line
        data={chartData}
        xField="index"
        yField="value"
        theme={isDark ? "dark" : "light"}
        autoFit
        smooth
        axis={false}
        legend={false}
        tooltip={false}
        style={{ stroke: color, lineWidth: 1.5 }}
        animate={false}
      />
    </div>
  );
}
