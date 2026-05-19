import { request } from "./request";

// ── Types ────────────────────────────────────────────────────────────────────

export interface DashboardPeriod {
  start_date: string;
  end_date: string;
  range_type: string;
}

export interface DashboardHealthResponse {
  status: string;
  timestamp: string;
  message: string;
}

export interface DashboardKpis {
  total_sessions: number;
  total_messages: number;
  llm_calls: number;
  tool_calls: number;
  total_tokens: number;
  estimated_cost: number;
  budget_used_pct: number;
  error_rate: number;
  avg_latency_ms: number;
  active_agents: number;
  mcp_connections: number;
  system_uptime_seconds: number;
}

export interface DashboardTrends {
  total_sessions_trend: number;
  total_tokens_trend: number;
  error_rate_trend: number;
}

export interface DashboardOverviewResponse {
  period: DashboardPeriod;
  kpis: DashboardKpis;
  trends: DashboardTrends;
}

export interface TokenTimelineItem {
  date: string;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  llm_calls: number;
}

export interface TokenByModel {
  provider_id: string;
  model_name: string;
  model_key: string;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  call_count: number;
  pct_of_total: number;
  estimated_cost: number;
}

export interface TokenSummary {
  total_prompt_tokens: number;
  total_completion_tokens: number;
  total_tokens: number;
  total_cost: number;
}

export interface DashboardTokensResponse {
  period: DashboardPeriod;
  summary: TokenSummary;
  timeline: TokenTimelineItem[];
  by_model: TokenByModel[];
}

export interface AgentStatsItem {
  agent_id: string;
  agent_name: string;
  sessions: number;
  messages: number;
  llm_calls: number;
  tokens: number;
  avg_tokens_per_session: number;
}

export interface ChannelStatsItem {
  channel_name: string;
  sessions: number;
  messages: number;
  llm_calls: number;
}

export interface AgentStatsSummary {
  total_agents: number;
  total_sessions: number;
  total_messages: number;
  total_llm_calls: number;
}

export interface DashboardAgentsResponse {
  period: DashboardPeriod;
  agents: AgentStatsItem[];
  by_channel: ChannelStatsItem[];
  summary: AgentStatsSummary;
}

export interface SkillCallItem {
  skill_name: string;
  skill_type: string;
  call_count: number;
  error_count: number;
  error_rate: number;
  avg_duration_ms: number;
}

export interface SkillsSummary {
  total_installed: number;
  total_by_type: Record<string, number>;
}

export interface DashboardSkillsResponse {
  period: DashboardPeriod;
  summary: SkillsSummary;
  top_calls: SkillCallItem[];
  by_type: Record<string, number>;
}

export interface ModelStatsItem {
  provider_id: string;
  model_name: string;
  model_key: string;
  call_count: number;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  avg_latency_ms: number;
  error_count: number;
  success_rate: number;
  pct_of_calls: number;
}

export interface ModelsSummary {
  total_providers: number;
  active_models: number;
  total_calls: number;
  total_tokens: number;
}

export interface DashboardModelsResponse {
  period: DashboardPeriod;
  summary: ModelsSummary;
  models: ModelStatsItem[];
}

// ── Query params ─────────────────────────────────────────────────────────────

export interface DashboardQueryParams {
  range?: string;
  start?: string;
  end?: string;
  [key: string]: string | number | undefined;
}

export interface TokensQueryParams extends DashboardQueryParams {
  group_by?: string;
}

export interface AgentsQueryParams extends DashboardQueryParams {
  agent_id?: string;
}

export interface SkillsQueryParams extends DashboardQueryParams {
  top?: number;
}

// ── Helpers ──────────────────────────────────────────────────────────────────

function buildQueryString(params: Record<string, unknown>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") {
      search.set(key, String(value));
    }
  }
  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

// ── API functions ────────────────────────────────────────────────────────────

export const dashboardApi = {
  getHealth: () =>
    request<DashboardHealthResponse>("/dashboard/health"),

  getOverview: (params: DashboardQueryParams = {}) =>
    request<DashboardOverviewResponse>(
      `/dashboard/overview${buildQueryString(params)}`,
    ),

  getTokens: (params: TokensQueryParams = {}) =>
    request<DashboardTokensResponse>(
      `/dashboard/tokens${buildQueryString(params)}`,
    ),

  getAgentsStats: (params: AgentsQueryParams = {}) =>
    request<DashboardAgentsResponse>(
      `/dashboard/agents/stats${buildQueryString(params)}`,
    ),

  getSkillsStats: (params: SkillsQueryParams = {}) =>
    request<DashboardSkillsResponse>(
      `/dashboard/skills/stats${buildQueryString(params)}`,
    ),

  getModelsStats: (params: DashboardQueryParams = {}) =>
    request<DashboardModelsResponse>(
      `/dashboard/models/stats${buildQueryString(params)}`,
    ),
};
