import { Table, Card, Row, Col, Statistic, Tag } from "antd";
import { useTranslation } from "react-i18next";
import type { DashboardSkillsResponse } from "../../../api/dashboard";

interface SkillsTabProps {
  data?: DashboardSkillsResponse;
  loading?: boolean;
}

export default function SkillsTab({ data, loading }: SkillsTabProps) {
  const { t } = useTranslation();

  const columns = [
    {
      title: t("dashboard.skills.skillName"),
      dataIndex: "skill_name",
      key: "skill_name",
    },
    {
      title: t("dashboard.skills.skillType"),
      dataIndex: "skill_type",
      key: "skill_type",
      render: (v: string) => (
        <Tag
          color={
            v === "builtin" ? "blue" : v === "mcp" ? "green" : "orange"
          }
        >
          {v}
        </Tag>
      ),
    },
    {
      title: t("dashboard.skills.callCount"),
      dataIndex: "call_count",
      key: "call_count",
    },
    {
      title: t("dashboard.skills.errorRate"),
      dataIndex: "error_rate",
      key: "error_rate",
      render: (v: number) => `${v.toFixed(1)}%`,
    },
    {
      title: t("dashboard.skills.avgDuration"),
      dataIndex: "avg_duration_ms",
      key: "avg_duration_ms",
      render: (v: number) => `${v}ms`,
    },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <Row gutter={16}>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title={t("dashboard.skills.totalInstalled")}
              value={data?.summary?.total_installed ?? 0}
              loading={loading}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title={t("dashboard.skills.builtin")}
              value={data?.by_type?.builtin ?? 0}
              loading={loading}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="MCP"
              value={data?.by_type?.mcp ?? 0}
              loading={loading}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title={t("dashboard.skills.custom")}
              value={data?.by_type?.custom ?? 0}
              loading={loading}
            />
          </Card>
        </Col>
      </Row>

      <Card title={t("dashboard.skills.topCallsTitle")} size="small">
        <Table
          columns={columns}
          dataSource={data?.top_calls}
          rowKey="skill_name"
          size="small"
          loading={loading}
          pagination={false}
        />
      </Card>
    </div>
  );
}
