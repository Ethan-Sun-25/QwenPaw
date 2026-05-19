import { Alert } from "antd";
import { useTranslation } from "react-i18next";
import type { DashboardKpis, DashboardTrends } from "../../../api/dashboard";

interface AlertBannerProps {
  kpis?: DashboardKpis;
  trends?: DashboardTrends;
}

export default function AlertBanner({ kpis, trends }: AlertBannerProps) {
  const { t } = useTranslation();

  if (!kpis || !trends) return null;

  const alerts: { type: "warning" | "error"; message: string }[] = [];

  // Token spike alert
  if (trends.total_tokens_trend > 100) {
    alerts.push({
      type: "warning",
      message: t("dashboard.alert.tokenSpike", {
        pct: trends.total_tokens_trend.toFixed(0),
      }),
    });
  }

  // High error rate alert
  if (kpis.error_rate > 5) {
    alerts.push({
      type: "error",
      message: t("dashboard.alert.highErrorRate", {
        rate: kpis.error_rate.toFixed(1),
      }),
    });
  }

  // Budget warning
  if (kpis.budget_used_pct > 80) {
    alerts.push({
      type: "warning",
      message: t("dashboard.alert.budgetWarning", {
        pct: kpis.budget_used_pct.toFixed(0),
      }),
    });
  }

  if (alerts.length === 0) return null;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {alerts.map((alert, idx) => (
        <Alert
          key={idx}
          type={alert.type}
          message={alert.message}
          showIcon
          closable
          banner
        />
      ))}
    </div>
  );
}
