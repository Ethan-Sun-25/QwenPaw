import { Col, Row } from "antd";
import { useTranslation } from "react-i18next";
import KpiCard from "./KpiCard";
import type {
  DashboardKpis,
  DashboardTrends,
  TokenTimelineItem,
} from "../../../api/dashboard";

interface KpiGridProps {
  kpis?: DashboardKpis;
  trends?: DashboardTrends;
  timeline?: TokenTimelineItem[];
  loading?: boolean;
}

function formatUptime(seconds: number): string {
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`;
  return `${Math.floor(seconds / 86400)}d`;
}

function formatTokens(n: number): string {
  if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`;
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
  return String(n);
}

export default function KpiGrid({
  kpis,
  trends,
  timeline,
  loading,
}: KpiGridProps) {
  const { t } = useTranslation();

  const sparklineTokens = timeline?.map((item) => item.total_tokens) ?? [];

  const cards = [
    {
      title: t("dashboard.kpi.totalSessions"),
      value: kpis?.total_sessions ?? 0,
      trend: trends?.total_sessions_trend,
    },
    {
      title: t("dashboard.kpi.totalTokens"),
      value: formatTokens(kpis?.total_tokens ?? 0),
      trend: trends?.total_tokens_trend,
      sparklineData: sparklineTokens,
    },
    {
      title: t("dashboard.kpi.llmCalls"),
      value: kpis?.llm_calls ?? 0,
    },
    {
      title: t("dashboard.kpi.estimatedCost"),
      value: kpis?.estimated_cost?.toFixed(2) ?? "0.00",
      prefix: "¥",
    },
    {
      title: t("dashboard.kpi.errorRate"),
      value: kpis?.error_rate?.toFixed(1) ?? "0.0",
      suffix: "%",
      trend: trends?.error_rate_trend,
    },
    {
      title: t("dashboard.kpi.avgLatency"),
      value: kpis?.avg_latency_ms ?? 0,
      suffix: "ms",
    },
    {
      title: t("dashboard.kpi.activeAgents"),
      value: kpis?.active_agents ?? 0,
    },
    {
      title: t("dashboard.kpi.uptime"),
      value: formatUptime(kpis?.system_uptime_seconds ?? 0),
    },
  ];

  return (
    <Row gutter={[16, 16]}>
      {cards.map((card) => (
        <Col key={card.title} xs={12} sm={8} md={6} lg={6} xl={4} xxl={3}>
          <KpiCard
            title={card.title}
            value={card.value}
            trend={card.trend}
            suffix={card.suffix}
            prefix={card.prefix}
            sparklineData={card.sparklineData}
            loading={loading}
          />
        </Col>
      ))}
    </Row>
  );
}
