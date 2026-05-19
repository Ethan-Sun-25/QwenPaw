import { Card } from "antd";
import { Line } from "@ant-design/plots";
import { useTranslation } from "react-i18next";
import { useTheme } from "../../../contexts/ThemeContext";
import type { TokenTimelineItem } from "../../../api/dashboard";

interface TokensTrendChartProps {
  data?: TokenTimelineItem[];
  loading?: boolean;
}

export default function TokensTrendChart({
  data,
  loading,
}: TokensTrendChartProps) {
  const { t } = useTranslation();
  const { isDark } = useTheme();

  const chartData =
    data?.flatMap((item) => [
      { date: item.date, value: item.prompt_tokens, type: "Prompt" },
      { date: item.date, value: item.completion_tokens, type: "Completion" },
    ]) ?? [];

  return (
    <Card
      title={t("dashboard.chart.tokensTrend")}
      size="small"
      loading={loading}
      style={{ height: "100%" }}
    >
      <div style={{ height: 280 }}>
        {chartData.length > 0 ? (
          <Line
            data={chartData}
            xField="date"
            yField="value"
            colorField="type"
            smooth
            theme={isDark ? "dark" : "light"}
            autoFit
            axis={{
              x: { title: false },
              y: { title: false },
            }}
            tooltip={{ title: "date" }}
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
