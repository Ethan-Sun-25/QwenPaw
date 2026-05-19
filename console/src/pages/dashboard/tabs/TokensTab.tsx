import { Table, Card, Row, Col, Statistic } from "antd";
import { useTranslation } from "react-i18next";
import type { DashboardTokensResponse } from "../../../api/dashboard";

interface TokensTabProps {
  data?: DashboardTokensResponse;
  loading?: boolean;
}

export default function TokensTab({ data, loading }: TokensTabProps) {
  const { t } = useTranslation();

  const columns = [
    {
      title: t("dashboard.tokens.date"),
      dataIndex: "date",
      key: "date",
    },
    {
      title: t("dashboard.tokens.promptTokens"),
      dataIndex: "prompt_tokens",
      key: "prompt_tokens",
      render: (v: number) => v.toLocaleString(),
    },
    {
      title: t("dashboard.tokens.completionTokens"),
      dataIndex: "completion_tokens",
      key: "completion_tokens",
      render: (v: number) => v.toLocaleString(),
    },
    {
      title: t("dashboard.tokens.totalTokens"),
      dataIndex: "total_tokens",
      key: "total_tokens",
      render: (v: number) => v.toLocaleString(),
    },
    {
      title: t("dashboard.tokens.llmCalls"),
      dataIndex: "llm_calls",
      key: "llm_calls",
    },
  ];

  const modelColumns = [
    {
      title: t("dashboard.tokens.modelName"),
      dataIndex: "model_key",
      key: "model_key",
    },
    {
      title: t("dashboard.tokens.totalTokens"),
      dataIndex: "total_tokens",
      key: "total_tokens",
      render: (v: number) => v.toLocaleString(),
    },
    {
      title: t("dashboard.tokens.callCount"),
      dataIndex: "call_count",
      key: "call_count",
    },
    {
      title: t("dashboard.tokens.pctOfTotal"),
      dataIndex: "pct_of_total",
      key: "pct_of_total",
      render: (v: number) => `${v.toFixed(1)}%`,
    },
    {
      title: t("dashboard.tokens.estimatedCost"),
      dataIndex: "estimated_cost",
      key: "estimated_cost",
      render: (v: number) => `¥${v.toFixed(2)}`,
    },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <Row gutter={16}>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title={t("dashboard.tokens.totalPrompt")}
              value={data?.summary?.total_prompt_tokens ?? 0}
              loading={loading}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title={t("dashboard.tokens.totalCompletion")}
              value={data?.summary?.total_completion_tokens ?? 0}
              loading={loading}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title={t("dashboard.tokens.total")}
              value={data?.summary?.total_tokens ?? 0}
              loading={loading}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title={t("dashboard.tokens.totalCost")}
              value={data?.summary?.total_cost ?? 0}
              precision={2}
              prefix="¥"
              loading={loading}
            />
          </Card>
        </Col>
      </Row>

      <Card title={t("dashboard.tokens.timelineTitle")} size="small">
        <Table
          columns={columns}
          dataSource={data?.timeline}
          rowKey="date"
          size="small"
          loading={loading}
          pagination={false}
          scroll={{ y: 300 }}
        />
      </Card>

      <Card title={t("dashboard.tokens.byModelTitle")} size="small">
        <Table
          columns={modelColumns}
          dataSource={data?.by_model}
          rowKey="model_key"
          size="small"
          loading={loading}
          pagination={false}
        />
      </Card>
    </div>
  );
}
