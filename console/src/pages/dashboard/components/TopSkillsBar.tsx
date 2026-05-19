import { Card } from "antd";
import { Column } from "@ant-design/plots";
import { useTranslation } from "react-i18next";
import { useTheme } from "../../../contexts/ThemeContext";
import type { SkillCallItem } from "../../../api/dashboard";

interface TopSkillsBarProps {
  data?: SkillCallItem[];
  loading?: boolean;
}

export default function TopSkillsBar({ data, loading }: TopSkillsBarProps) {
  const { t } = useTranslation();
  const { isDark } = useTheme();

  const chartData =
    data?.map((item) => ({
      skill: item.skill_name,
      calls: item.call_count,
    })) ?? [];

  return (
    <Card
      title={t("dashboard.chart.topSkills")}
      size="small"
      loading={loading}
      style={{ height: "100%" }}
    >
      <div style={{ height: 280 }}>
        {chartData.length > 0 ? (
          <Column
            data={chartData}
            xField="skill"
            yField="calls"
            theme={isDark ? "dark" : "light"}
            autoFit
            axis={{
              x: {
                title: false,
                labelAutoRotate: true,
              },
              y: { title: false },
            }}
            style={{ fill: "#FF7F16" }}
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
