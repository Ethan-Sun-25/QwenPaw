import { useRequest } from "ahooks";
import {
  dashboardApi,
  type DashboardOverviewResponse,
  type DashboardTokensResponse,
  type DashboardAgentsResponse,
  type DashboardSkillsResponse,
  type DashboardModelsResponse,
} from "../../../api/dashboard";

interface UseDashboardDataOptions {
  queryParams: Record<string, string>;
  refreshInterval?: number;
}

export function useDashboardData({
  queryParams,
  refreshInterval = 60000,
}: UseDashboardDataOptions) {
  const overview = useRequest<DashboardOverviewResponse, []>(
    () => dashboardApi.getOverview(queryParams),
    {
      pollingInterval: refreshInterval,
      refreshDeps: [JSON.stringify(queryParams)],
    },
  );

  const tokens = useRequest<DashboardTokensResponse, []>(
    () => dashboardApi.getTokens({ ...queryParams, group_by: "day" }),
    {
      pollingInterval: refreshInterval,
      refreshDeps: [JSON.stringify(queryParams)],
    },
  );

  const agents = useRequest<DashboardAgentsResponse, []>(
    () => dashboardApi.getAgentsStats(queryParams),
    {
      pollingInterval: refreshInterval,
      refreshDeps: [JSON.stringify(queryParams)],
    },
  );

  const skills = useRequest<DashboardSkillsResponse, []>(
    () => dashboardApi.getSkillsStats({ ...queryParams, top: 10 }),
    {
      pollingInterval: refreshInterval,
      refreshDeps: [JSON.stringify(queryParams)],
    },
  );

  const models = useRequest<DashboardModelsResponse, []>(
    () => dashboardApi.getModelsStats(queryParams),
    {
      pollingInterval: refreshInterval,
      refreshDeps: [JSON.stringify(queryParams)],
    },
  );

  const refreshAll = () => {
    overview.refresh();
    tokens.refresh();
    agents.refresh();
    skills.refresh();
    models.refresh();
  };

  const loading =
    overview.loading ||
    tokens.loading ||
    agents.loading ||
    skills.loading ||
    models.loading;

  return {
    overview,
    tokens,
    agents,
    skills,
    models,
    refreshAll,
    loading,
  };
}
