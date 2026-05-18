import { Tabs } from "antd";
import { useTranslation } from "react-i18next";
import TokensTab from "../tabs/TokensTab";
import ConversationsTab from "../tabs/ConversationsTab";
import ModelsTab from "../tabs/ModelsTab";
import SkillsTab from "../tabs/SkillsTab";
import McpTab from "../tabs/McpTab";
import AcpTab from "../tabs/AcpTab";
import PluginsTab from "../tabs/PluginsTab";
import type {
  DashboardTokensResponse,
  DashboardAgentsResponse,
  DashboardModelsResponse,
  DashboardSkillsResponse,
} from "../../../api/dashboard";

interface ModuleTabsProps {
  tokensData?: DashboardTokensResponse;
  agentsData?: DashboardAgentsResponse;
  modelsData?: DashboardModelsResponse;
  skillsData?: DashboardSkillsResponse;
  loading?: boolean;
}

export default function ModuleTabs({
  tokensData,
  agentsData,
  modelsData,
  skillsData,
  loading,
}: ModuleTabsProps) {
  const { t } = useTranslation();

  const items = [
    {
      key: "tokens",
      label: t("dashboard.tab.tokens"),
      children: <TokensTab data={tokensData} loading={loading} />,
    },
    {
      key: "conversations",
      label: t("dashboard.tab.conversations"),
      children: <ConversationsTab data={agentsData} loading={loading} />,
    },
    {
      key: "models",
      label: t("dashboard.tab.models"),
      children: <ModelsTab data={modelsData} loading={loading} />,
    },
    {
      key: "skills",
      label: t("dashboard.tab.skills"),
      children: <SkillsTab data={skillsData} loading={loading} />,
    },
    {
      key: "mcp",
      label: t("dashboard.tab.mcp"),
      children: <McpTab />,
    },
    {
      key: "acp",
      label: t("dashboard.tab.acp"),
      children: <AcpTab />,
    },
    {
      key: "plugins",
      label: t("dashboard.tab.plugins"),
      children: <PluginsTab />,
    },
  ];

  return <Tabs items={items} />;
}
