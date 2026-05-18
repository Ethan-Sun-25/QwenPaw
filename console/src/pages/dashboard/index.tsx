import { Button, Col, DatePicker, Row, Segmented, Space, Typography } from "antd";
import { ReloadOutlined } from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import dayjs from "dayjs";
import { useTimeRange, type RangeType } from "./hooks/useTimeRange";
import { useDashboardData } from "./hooks/useDashboardData";
import AlertBanner from "./components/AlertBanner";
import KpiGrid from "./components/KpiGrid";
import TokensTrendChart from "./components/TokensTrendChart";
import ModelsDonutChart from "./components/ModelsDonutChart";
import TopSkillsBar from "./components/TopSkillsBar";
import ModuleTabs from "./components/ModuleTabs";

const { Title } = Typography;
const { RangePicker } = DatePicker;

export default function DashboardPage() {
  const { t } = useTranslation();
  const { timeRange, setRange, setCustomRange, getQueryParams } =
    useTimeRange("7d");

  const { overview, tokens, agents, skills, models, refreshAll, loading } =
    useDashboardData({
      queryParams: getQueryParams(),
    });

  const rangeOptions = [
    { label: t("dashboard.range.today"), value: "today" },
    { label: t("dashboard.range.7d"), value: "7d" },
    { label: t("dashboard.range.30d"), value: "30d" },
  ];

  return (
    <div style={{ padding: "24px", maxWidth: 1600, margin: "0 auto" }}>
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 16,
          flexWrap: "wrap",
          gap: 12,
        }}
      >
        <Title level={4} style={{ margin: 0 }}>
          {t("dashboard.title")}
        </Title>
        <Space wrap>
          <Segmented
            options={rangeOptions}
            value={timeRange.range === "custom" ? undefined : timeRange.range}
            onChange={(val) => setRange(val as RangeType)}
          />
          <RangePicker
            size="small"
            value={
              timeRange.range === "custom" && timeRange.start && timeRange.end
                ? [dayjs(timeRange.start), dayjs(timeRange.end)]
                : null
            }
            onChange={(dates) => {
              if (dates && dates[0] && dates[1]) {
                setCustomRange(
                  dates[0].format("YYYY-MM-DD"),
                  dates[1].format("YYYY-MM-DD"),
                );
              }
            }}
          />
          <Button
            icon={<ReloadOutlined />}
            onClick={refreshAll}
            loading={loading}
          >
            {t("common.refresh")}
          </Button>
        </Space>
      </div>

      {/* Alert Banner */}
      <div style={{ marginBottom: 16 }}>
        <AlertBanner
          kpis={overview.data?.kpis}
          trends={overview.data?.trends}
        />
      </div>

      {/* KPI Cards */}
      <div style={{ marginBottom: 24 }}>
        <KpiGrid
          kpis={overview.data?.kpis}
          trends={overview.data?.trends}
          timeline={tokens.data?.timeline}
          loading={overview.loading}
        />
      </div>

      {/* Charts Row */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={10}>
          <TokensTrendChart
            data={tokens.data?.timeline}
            loading={tokens.loading}
          />
        </Col>
        <Col xs={24} lg={7}>
          <ModelsDonutChart
            data={tokens.data?.by_model}
            loading={tokens.loading}
          />
        </Col>
        <Col xs={24} lg={7}>
          <TopSkillsBar
            data={skills.data?.top_calls}
            loading={skills.loading}
          />
        </Col>
      </Row>

      {/* Module Tabs */}
      <ModuleTabs
        tokensData={tokens.data}
        agentsData={agents.data}
        modelsData={models.data}
        skillsData={skills.data}
        loading={loading}
      />
    </div>
  );
}
