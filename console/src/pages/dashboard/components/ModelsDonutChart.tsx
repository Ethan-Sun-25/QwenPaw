import { Card } from "antd";
import { Pie } from "@ant-design/plots";
import { useTranslation } from "react-i18next";
import { useTheme } from "../../../contexts/ThemeContext";
import type { TokenByModel } from "../../../api/dashboard";

interface ModelsDonutChartProps {
  data?: TokenByModel[];
  loading?: boolean;
}

export default function ModelsDonutChart({
  data,
  loading,
}: ModelsDonutChartProps) {
  const { t } = useTranslation();
  const { isDark } = useTheme();

  const chartData =
    data?.map((item) => ({
      type: item.model_name,
      value: item.total_tokens,
    })) ?? [];

  return (
    <Card
      title={t("dashboard.chart.modelsDistribution")}
      size="small"
      loading={loading}
      style={{ height: "100%" }}
    >
      <div style={{ height: 280 }}>
        {chartData.length > 0 ? (
          <Pie
            data={chartData}
            angleField="value"
            colorField="type"
            innerRadius={0.6}
            theme={isDark ? "dark" : "light"}
            autoFit
            label={{
              text: "type",
              position: "outside",
            }}
            legend={{ position: "bottom" }}
            tooltip={{
              title: "type",
            }}
          />
        ) : (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              height: "100%",
              color: "var(--ant-color-text-secondary)",
            }}
          >
            {t("dashboard.empty.noData")}
          </div>
        )}
      </div>
    </Card>
  );
}
