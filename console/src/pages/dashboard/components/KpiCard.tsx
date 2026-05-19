import { Card, Statistic } from "antd";
import { ArrowUpOutlined, ArrowDownOutlined } from "@ant-design/icons";
import Sparkline from "./Sparkline";

interface KpiCardProps {
  title: string;
  value: number | string;
  trend?: number;
  suffix?: string;
  prefix?: string;
  sparklineData?: number[];
  loading?: boolean;
}

export default function KpiCard({
  title,
  value,
  trend,
  suffix,
  prefix,
  sparklineData,
  loading,
}: KpiCardProps) {
  const trendColor =
    trend === undefined || trend === 0
      ? undefined
      : trend > 0
        ? "#52c41a"
        : "#f5222d";

  const trendIcon =
    trend === undefined || trend === 0 ? null : trend > 0 ? (
      <ArrowUpOutlined />
    ) : (
      <ArrowDownOutlined />
    );

  return (
    <Card
      size="small"
      style={{ height: "100%" }}
      loading={loading}
      styles={{ body: { padding: "16px 20px" } }}
    >
      <Statistic
        title={title}
        value={value}
        suffix={suffix}
        prefix={prefix}
        valueStyle={{ fontSize: 24, fontWeight: 600 }}
      />
      {trend !== undefined && (
        <div
          style={{
            marginTop: 4,
            fontSize: 12,
            color: trendColor,
            display: "flex",
            alignItems: "center",
            gap: 4,
          }}
        >
          {trendIcon}
          <span>{Math.abs(trend).toFixed(1)}%</span>
        </div>
      )}
      {sparklineData && sparklineData.length > 0 && (
        <div style={{ marginTop: 8 }}>
          <Sparkline data={sparklineData} />
        </div>
      )}
    </Card>
  );
}
