import { Table, Card, Row, Col, Statistic } from "antd";
import { useTranslation } from "react-i18next";
import type { DashboardModelsResponse } from "../../../api/dashboard";

interface ModelsTabProps {
  data?: DashboardModelsResponse;
  loading?: boolean;
}

export default function ModelsTab({ data, loading }: ModelsTabProps) {
  const { t } = useTranslation();

  const columns = [
    {
      title: t("dashboard.models.modelKey"),
      dataIndex: "model_key",
      key: "model_key",
    },
    {
      title: t("dashboard.models.callCount"),
      dataIndex: "call_count",
      key: "call_count",
    },
    {
      title: t("dashboard.models.totalTokens"),
      dataIndex: "total_tokens",
      key: "total_tokens",
      render: (v: number) => v.toLocaleString(),
    },
    {
      title: t("dashboard.models.avgLatency"),
      dataIndex: "avg_latency_ms",
      key: "avg_latency_ms",
      render: (v: number) => `${v}ms`,
    },
    {
      title: t("dashboard.models.successRate"),
      dataIndex: "success_rate",
      key: "success_rate",
      render: (v: number) => `${v.toFixed(1)}%`,
    },
    {
      title: t("dashboard.models.pctOfCalls"),
      dataIndex: "pct_of_calls",
      key: "pct_of_calls",
      render: (v: number) => `${v.toFixed(1)}%`,
    },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <Row gutter={16}>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title={t("dashboard.models.totalProviders")}
              value={data?.summary?.total_providers ?? 0}
              loading={loading}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title={t("dashboard.models.activeModels")}
              value={data?.summary?.active_models ?? 0}
              loading={loading}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title={t("dashboard.models.totalCalls")}
              value={data?.summary?.total_calls ?? 0}
              loading={loading}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title={t("dashboard.models.totalTokens")}
              value={data?.summary?.total_tokens ?? 0}
              loading={loading}
            />
          </Card>
        </Col>
      </Row>

      <Card title={t("dashboard.models.detailTitle")} size="small">
        <Table
          columns={columns}
          dataSource={data?.models}
          rowKey="model_key"
          size="small"
          loading={loading}
          pagination={false}
        />
      </Card>
    </div>
  );
}
