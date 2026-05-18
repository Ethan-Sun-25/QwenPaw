import { Table, Card, Row, Col, Statistic } from "antd";
import { useTranslation } from "react-i18next";
import type { DashboardAgentsResponse } from "../../../api/dashboard";

interface ConversationsTabProps {
  data?: DashboardAgentsResponse;
  loading?: boolean;
}

export default function ConversationsTab({
  data,
  loading,
}: ConversationsTabProps) {
  const { t } = useTranslation();

  const agentColumns = [
    {
      title: t("dashboard.conversations.agentName"),
      dataIndex: "agent_name",
      key: "agent_name",
    },
    {
      title: t("dashboard.conversations.sessions"),
      dataIndex: "sessions",
      key: "sessions",
    },
    {
      title: t("dashboard.conversations.messages"),
      dataIndex: "messages",
      key: "messages",
    },
    {
      title: t("dashboard.conversations.llmCalls"),
      dataIndex: "llm_calls",
      key: "llm_calls",
    },
    {
      title: t("dashboard.conversations.tokens"),
      dataIndex: "tokens",
      key: "tokens",
      render: (v: number) => v.toLocaleString(),
    },
    {
      title: t("dashboard.conversations.avgTokens"),
      dataIndex: "avg_tokens_per_session",
      key: "avg_tokens_per_session",
      render: (v: number) => v.toLocaleString(),
    },
  ];

  const channelColumns = [
    {
      title: t("dashboard.conversations.channelName"),
      dataIndex: "channel_name",
      key: "channel_name",
    },
    {
      title: t("dashboard.conversations.sessions"),
      dataIndex: "sessions",
      key: "sessions",
    },
    {
      title: t("dashboard.conversations.messages"),
      dataIndex: "messages",
      key: "messages",
    },
    {
      title: t("dashboard.conversations.llmCalls"),
      dataIndex: "llm_calls",
      key: "llm_calls",
    },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <Row gutter={16}>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title={t("dashboard.conversations.totalAgents")}
              value={data?.summary?.total_agents ?? 0}
              loading={loading}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title={t("dashboard.conversations.totalSessions")}
              value={data?.summary?.total_sessions ?? 0}
              loading={loading}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title={t("dashboard.conversations.totalMessages")}
              value={data?.summary?.total_messages ?? 0}
              loading={loading}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title={t("dashboard.conversations.totalLlmCalls")}
              value={data?.summary?.total_llm_calls ?? 0}
              loading={loading}
            />
          </Card>
        </Col>
      </Row>

      <Card title={t("dashboard.conversations.byAgent")} size="small">
        <Table
          columns={agentColumns}
          dataSource={data?.agents}
          rowKey="agent_id"
          size="small"
          loading={loading}
          pagination={false}
        />
      </Card>

      <Card title={t("dashboard.conversations.byChannel")} size="small">
        <Table
          columns={channelColumns}
          dataSource={data?.by_channel}
          rowKey="channel_name"
          size="small"
          loading={loading}
          pagination={false}
        />
      </Card>
    </div>
  );
}
