# QwenPaw 源码集成笔记 — Dashboard 后端/前端集成指南

**版本**: QwenPaw 1.1.4 + agentscope-runtime 1.1.4  
**调研时间**: 2026-05-18  
**集成目标**: 将已有 Dashboard（FastAPI + React + Arco + ECharts）集成到 QwenPaw 运营监控平台

---

## 问题 1: 后端 FastAPI 入口与路由注册

### 关键文件位置
- **主应用文件**: `/Users/sunyixiang/Desktop/521智能编码/demo1/QwenPaw-source/src/qwenpaw/app/_app.py`
- **路由集合**: `/Users/sunyixiang/Desktop/521智能编码/demo1/QwenPaw-source/src/qwenpaw/app/routers/__init__.py`
- **CLI 启动**: `/Users/sunyixiang/Desktop/521智能编码/demo1/QwenPaw-source/src/qwenpaw/cli/app_cmd.py`

### 如何创建 FastAPI 应用
```python
# src/qwenpaw/app/_app.py 第 547-552 行
app = FastAPI(
    lifespan=lifespan,
    docs_url="/docs" if DOCS_ENABLED else None,
    redoc_url="/redoc" if DOCS_ENABLED else None,
    openapi_url="/openapi.json" if DOCS_ENABLED else None,
)
```
- 应用实例全局名为 `app`，由 CLI 通过 uvicorn 启动
- Uvicorn 启动命令: `uvicorn.run("qwenpaw.app._app:app", host=host, port=port, ...)`

### Router 注册模式
```python
# src/qwenpaw/app/routers/__init__.py 第 30-54 行 (主路由器)
router = APIRouter()
router.include_router(agents_router)
router.include_router(config_router)
# ... 其他 routers
router.include_router(token_usage_router)  # 现有参考
# ...

# src/qwenpaw/app/_app.py 第 646-649 行 (挂载)
app.include_router(api_router, prefix="/api")
app.include_router(approval_router, prefix="/api")
agent_scoped_router = create_agent_scoped_router()
app.include_router(agent_scoped_router, prefix="/api")
```

**集成建议**: 
1. 在 `src/qwenpaw/app/routers/` 目录下创建 `dashboard.py`，定义 `router = APIRouter(prefix="/dashboard", tags=["dashboard"])`
2. 在 `src/qwenpaw/app/routers/__init__.py` 中导入并 include
3. 在 `_app.py` 第 646 行后添加 `app.include_router(dashboard_router)`（前缀已包含在 router 中）

### CORS 中间件与身份验证
```python
# src/qwenpaw/app/_app.py 第 557-569 行
app.add_middleware(AuthMiddleware)

if CORS_ORIGINS:
    origins = [o.strip() for o in CORS_ORIGINS.split(",") if o.strip()]
    app.add_middleware(CORSMiddleware, allow_origins=origins, ...)
```

- **环境变量**: `QWENPAW_CORS_ORIGINS` (constant.py 第 28 行读取)
- **AuthMiddleware** 在 `src/qwenpaw/app/auth.py`，会自动验证 Bearer token（如启用认证）
- **Dashboard 无需特殊 auth**，仅需遵循全局中间件链

### 依赖注入与 app.state
```python
# src/qwenpaw/app/_app.py lifespan 第 283-299 行
app.state.multi_agent_manager = multi_agent_manager
app.state.provider_manager = provider_manager
app.state.local_model_manager = local_model_manager
app.state.get_agent_by_id = _get_agent_by_id  # 异步函数
```

**可用共享资源**: 在路由处理函数中通过 `request.app.state.xxx` 访问

### uvicorn 端口
- **默认**: 8088 (constant.py 第 168 行, app_cmd.py 第 24 行)
- **当前绑定**: 127.0.0.1:8088

---

## 问题 2: 数据源访问层 (token_usage 模块)

### Token Usage 模块位置
- **主管理器**: `/Users/sunyixiang/Desktop/521智能编码/demo1/QwenPaw-source/src/qwenpaw/token_usage/manager.py`
- **初始化导出**: `/Users/sunyixiang/Desktop/521智能编码/demo1/QwenPaw-source/src/qwenpaw/token_usage/__init__.py`
- **现有 API 路由**: `src/qwenpaw/app/routers/token_usage.py`

### 工作目录与数据文件
```python
# constant.py 第 89-101 行
WORKING_DIR = Path("~/.qwenpaw").expanduser().resolve()  # 优先级: env > ~/.copaw > 默认

# constant.py 第 174-177 行
TOKEN_USAGE_FILE = "token_usage.json"  # 相对于 WORKING_DIR
```

**完整路径**: `~/.qwenpaw/token_usage.json` (或 `~/.copaw/token_usage.json` 如果是旧安装)

### 现有 Token Usage 查询 API
```python
# src/qwenpaw/app/routers/token_usage.py
GET /api/token-usage              # 聚合摘要 (TokenUsageSummary)
GET /api/token-usage/details      # 原始记录 (list[TokenUsageRecord])

# 数据模型 (manager.py 第 19-63 行)
class TokenUsageStats:
    prompt_tokens: int
    completion_tokens: int
    call_count: int

class TokenUsageRecord(TokenUsageStats):
    date: str (YYYY-MM-DD)
    provider_id: str
    model: str

class TokenUsageSummary:
    total_prompt_tokens: int
    total_completion_tokens: int
    total_calls: int
    by_model: dict[str, TokenUsageByModel]
    by_date: dict[str, TokenUsageStats]
```

### 获取单例实例
```python
from qwenpaw.token_usage import get_token_usage_manager

manager = get_token_usage_manager()
summary = await manager.get_summary(start_date=..., end_date=..., model_name=..., provider_id=...)
records = await manager.get_details(...)
```

**集成建议**:
1. Dashboard 数据源可直接复用 `get_token_usage_manager()` 和 `.get_summary()`
2. 其他数据（agents、models、skills）读取方式见问题 3-5

---

## 问题 3: Console 前端路由与菜单

### 主路由定义
```typescript
// console/src/layouts/MainLayout/index.tsx 第 48-72 行
const pathToKey: Record<string, string> = {
  "/chat": "chat",
  "/token-usage": "token-usage",
  "/agent-stats": "agent-stats",
  // ...
};

// 第 108-149 行：Route 定义
<Routes>
  <Route path="/" element={<Navigate to="/chat" replace />} />
  <Route path="/chat/*" element={<Chat />} />
  <Route path="/token-usage" element={<TokenUsagePage />} />
  <Route path="/agent-stats" element={<AgentStatsPage />} />
  {/* Plugin routes */}
  {pluginRoutes.map((route) => (
    <Route key={route.path} path={route.path} element={<route.component />} />
  ))}
</Routes>
```

### 左侧菜单项数据源
```typescript
// console/src/layouts/Sidebar.tsx 第 209-420 行
const collapsedNavItems = [
  { key: "chat", icon: ..., path: "/chat", label: t("nav.chat") },
  { key: "token-usage", icon: <SparkDataLine />, path: "/token-usage", label: t("nav.tokenUsage") },
  { key: "agent-stats", icon: <SparkBarChartLine />, path: "/agent-stats", label: t("nav.agentStats") },
  // ...
];

// 菜单项分组（collapsible groups）—— 第 420-550 行
const menuItems = [
  {
    label: t("nav.chatGroup"),
    key: "chat-group",
    children: [{ key: "chat", ... }],
  },
  {
    label: t("nav.controlGroup"),
    key: "control-group",
    children: [{ key: "channels", ... }, { key: "sessions", ... }],
  },
  {
    label: t("nav.agentGroup"),
    key: "agent-group",
    children: [{ key: "skills", ... }, { key: "models", ... }],
  },
  {
    label: t("nav.settingsGroup"),
    key: "settings-group",
    children: [{ key: "token-usage", ... }, { key: "agent-stats", ... }],
  },
];
```

### i18n 资源文件
```typescript
// console/src/i18n.ts 第 1-20 行
import i18n from 'i18next';
i18n.use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: { zh, en, ja, ru, id },
    ns: ['translation'],
    defaultNS: 'translation',
  });
```

- **资源位置**: `console/src/locales/[lang].json`
- **菜单 i18n keys**: `nav.xxx` (如 `nav.tokenUsage`, `nav.agentStats`)
- **添加新菜单项**: 在各语言的 locales JSON 中添加相应 key

**集成建议**:
1. 在 `/agent-stats` 下方创建 `/dashboard` 路由（或放在 `/settings-group` 内）
2. 在 `console/src/layouts/Sidebar.tsx` 的 `collapsedNavItems` 数组中添加新菜单项
3. 在 `console/src/layouts/MainLayout/index.tsx` 中添加对应 Route（使用 `lazyImportWithRetry`）
4. 更新 `console/src/locales/*.json` 中的 i18n keys
5. 在 `pathToKey` 中添加映射

---

## 问题 4: Console 设计系统与主题

### 设计系统包
```typescript
// console/src/App.tsx 第 1-6 行
import {
  ConfigProvider,
  bailianDarkTheme,
  bailianTheme,
} from "@agentscope-ai/design";

// package.json 第 22-25 行
"@agentscope-ai/design": "^1.0.14",
"@agentscope-ai/icons": "^1.0.67",
"@agentscope-ai/chat": "^1.1.63",
"@ant-design/plots": "^2.6.8",
```

### 常用组件与主题 Token
```typescript
// App.tsx 第 174-188 行
<ConfigProvider
  {...selectedTheme}
  prefix="qwenpaw"
  prefixCls="qwenpaw"
  locale={antdLocale}
  theme={{
    algorithm: isDark ? antdTheme.darkAlgorithm : antdTheme.defaultAlgorithm,
    token: { colorPrimary: "#FF7F16" }  // 橙色主色
  }}
>
  <AntdApp>...</AntdApp>
</ConfigProvider>
```

### 深色主题切换
```typescript
// console/src/contexts/ThemeContext.tsx (已有)
const { isDark } = useTheme();  // 返回布尔值
const selectedTheme = isDark ? bailianDarkTheme : bailianTheme;

// 实现逻辑：antd-style + antd ConfigProvider
```

### 页面级 Layout 模板
```typescript
// console/src/layouts/MainLayout/index.tsx 第 91-156 行
<Layout className={styles.mainLayout}>
  <Header />  <!-- 顶部导航栏 -->
  <Layout>
    <Sidebar selectedKey={selectedKey} />  <!-- 左侧菜单 -->
    <Content className="page-container">
      <ConsolePollService />  <!-- 后台消息轮询 -->
      <div className="page-content">
        <ChunkErrorBoundary resetKey={currentPath}>
          <Suspense fallback={<Spin />}>
            <Routes>...</Routes>
          </Suspense>
        </ChunkErrorBoundary>
      </div>
    </Content>
  </Layout>
</Layout>
```

### 典型页面结构（参考）
```typescript
// console/src/pages/Settings/TokenUsage/index.tsx (参考)
import { Layout, Card, Statistic, Table, Space } from "antd";
import { useTranslation } from "react-i18next";

export default function TokenUsagePage() {
  const { t } = useTranslation();
  
  return (
    <div className={styles.container}>
      <Card title={t("pages.tokenUsage.title")}>
        <Space direction="vertical" style={{ width: "100%" }}>
          {/* KPI 卡片 */}
          <Statistic title="..." value={...} />
          {/* 图表 */}
          {/* 表格 */}
        </Space>
      </Card>
    </div>
  );
}
```

**集成建议**:
1. Dashboard 页面遵循上述 Layout 模板
2. 使用 `@agentscope-ai/design` 的 `bailianTheme`/`bailianDarkTheme` 自动适配
3. 主色调已固定为 `#FF7F16` (橙色)
4. 使用 Antd 原生组件（Card, Statistic, Tabs, Table, Empty, Skeleton）
5. 图表用 `@ant-design/plots` (见问题 6)

---

## 问题 5: Console 数据请求层

### 基础请求客户端
```typescript
// console/src/api/request.ts 第 60-104 行
export async function request<T = unknown>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const url = getApiUrl(path);  // 自动补全 /api 前缀
  const method = options.method || "GET";
  const headers = buildHeaders(method, options.headers);
  
  const response = await fetch(url, { ...options, headers });
  
  if (!response.ok) {
    if (response.status === 401) {
      clearAuthToken();  // 自动登出
      window.location.href = "/login";
    }
    throw new Error(errorMessage);
  }
  return response.json() as T;
}

// API 地址拼装 (config.ts 第 10-16 行)
function getApiUrl(path: string): string {
  const base = VITE_API_BASE_URL || "";  // 前端后构建时设置，默认空 = 同源
  const apiPrefix = "/api";
  return `${base}${apiPrefix}${path}`;
}
```

### 请求 Hook 模式（参考现有代码）
```typescript
// console/src/api/modules/token_usage.ts (新建)
import { request } from '../request';

export const tokenUsageApi = {
  getSummary: (params) => request('/token-usage', { params }),
  getDetails: (params) => request('/token-usage/details', { params }),
};

// 在页面中使用
import { useRequest } from 'ahooks';
const { data, loading, error } = useRequest(() => tokenUsageApi.getSummary(...));
```

### 鉴权 Header
```typescript
// console/src/api/authHeaders.ts 第 1-15 行
function buildAuthHeaders(): Record<string, string> {
  const token = getApiToken();
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}
```

- **Token 存储**: localStorage 中 key 为 `qwenpaw_auth_token`
- **自动添加**: 每个 fetch 请求都会调用 `buildAuthHeaders()`

### 错误展示模式
```typescript
// console/src/api/request.ts 第 73-92 行
if (!response.ok) {
  // 提取错误信息: response.detail > response.message > response.error > 原文本
  const errorMessage = getErrorMessageFromBody(text, contentType);
  throw new Error(errorMessage);
}

// 在页面中
import { useAppMessage } from '../hooks/useAppMessage';
const { message } = useAppMessage();

try {
  await apiCall();
} catch (err) {
  message.error(err instanceof Error ? err.message : '请求失败');
}
```

- **加载状态**: `useRequest` hook 返回 `loading` boolean，绑定 Spin/Skeleton
- **错误处理**: 统一用 `message.error()` 显示

**集成建议**:
1. 在 `console/src/api/modules/` 下创建 `dashboard.ts`，导出 `dashboardApi` 对象
2. 在页面中用 `useRequest(dashboardApi.xxx)` 封装请求
3. 错误和加载状态由 ahooks 自动管理

---

## 问题 6: Console 图表方案

### 图表库与导入
```typescript
// package.json 第 26 行
"@ant-design/plots": "^2.6.8",

// 典型导入
import { Line, Column, DualAxes, Pie } from '@ant-design/plots';
```

### 已有用法示例位置
```
console/src/pages/Settings/TokenUsage/index.tsx  (参考)
console/src/pages/Control/Heartbeat/index.tsx (参考)
```

### 图表类型与常用 props
```typescript
// Line Chart (趋势)
<Line
  data={data}
  xField="date"
  yField="value"
  seriesField="type"
  smooth={true}
  theme={isDark ? 'dark' : 'light'}
  tooltip={{ showTitle: true }}
/>

// Column (柱状图)
<Column
  data={data}
  xField="category"
  yField="value"
  seriesField="type"
  theme={isDark ? 'dark' : 'light'}
/>

// Pie (饼图 / Donut)
<Pie
  data={data}
  angleField="value"
  colorField="type"
  innerRadius={0.6}  // Donut 效果
  theme={isDark ? 'dark' : 'light'}
/>
```

### 主题配置（深色模式）
```typescript
// 方式 1: theme prop（推荐）
theme={isDark ? 'dark' : 'light'}

// 方式 2: 全局 StaticConfig
import { setDefaultOptions } from '@ant-design/plots';
setDefaultOptions({
  theme: isDark ? 'dark' : 'light',
});
```

**集成建议**:
1. 在 Dashboard 页面中导入 `@ant-design/plots` 组件（如 `Line`, `Column`, `Pie`）
2. 使用 `useTheme()` hook 获取 `isDark` 布尔值
3. 传递 `theme={isDark ? 'dark' : 'light'}` 给所有图表组件
4. 对标已有的 Token Usage/Agent Stats 页面样式与布局

---

## 问题 7: Console Build 产物与 SPA 挂载

### Vite 构建配置
```typescript
// console/vite.config.ts 第 99-103 行
build: {
  // Output to QwenPaw's console directory
  // outDir: path.resolve(__dirname, "../src/qwenpaw/console"),
  // emptyOutDir: true,
  cssCodeSplit: true,
  sourcemap: mode !== "production",
  chunkSizeWarningLimit: 1000,
}
```

**当前构建输出**: `console/dist/` (注释掉自动复制，手动管理)

### Package 打包配置
```python
# pyproject.toml 第 58-69 行
[tool.setuptools.package-data]
"qwenpaw" = [
    "console/**",  # 包含所有 console 目录下文件
    "agents/md_files/**",
    "tokenizer/**",
    "security/tool_guard/rules/**",
    "docs/*.md",
]
```

**包含路径**: `src/qwenpaw/console/` (setuptools 按此包含)

### FastAPI SPA 挂载与回退
```python
# src/qwenpaw/app/_app.py 第 572-718 行
_CONSOLE_STATIC_DIR = _resolve_console_static_dir()  # 查找 console 目录

@app.get("/console/{full_path:path}")
def _console_spa_alias(full_path: str = ""):
    return _serve_console_index()

@app.get("/{full_path:path}")  # SPA catch-all
def _console_spa(full_path: str):
    if full_path in ("docs", "redoc", "openapi.json"):
        raise HTTPException(status_code=404)
    if full_path.startswith("api/") or full_path == "api":
        raise HTTPException(status_code=404)
    # 尝试返回静态文件，否则回到 index.html
    return _serve_console_index()
```

**路由优先级** (从高到低):
1. `/api/*` — API 路由（FastAPI 注册）
2. `/docs`, `/redoc`, `/openapi.json` — OpenAPI 文档
3. `/console/*` — 别名：回到 index.html（支持 /console/path 也能工作）
4. `/{path}` — SPA catch-all（history fallback）

### /dashboard 路由能否被处理
```
YES ✓
/dashboard 会被 _console_spa catch-all 捕获 → index.html 返回
React Router 在前端处理 /dashboard 路由
```

**集成建议**:
1. 构建 console: `npm run build` → `console/dist/`
2. 复制到包: `cp -r console/dist/. src/qwenpaw/console/`
3. 重新打包: `pip install -e .`
4. Dashboard 前端路由在 React Router 中定义，无需后端特殊处理
5. API 由后端 router 在 `/api/dashboard/*` 下提供

---

## 问题 8: 测试与 Lint 基线

### 后端测试
```bash
# Makefile 第 10-11 行
make test                    # 所有测试: tests/ -v
make test-unit              # 单元测试: tests/unit/
make test-contract          # 协议测试: tests/contract/
make test-integration       # 集成测试: tests/integration/
make coverage-full          # 完整覆盖率报告

# 底层命令
pytest tests/ -v --tb=short -q
pytest tests/ --cov=src/qwenpaw --cov-report=term-missing --cov-report=html
```

**Pytest 配置** (`pyproject.toml` 第 116-127 行):
```ini
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
markers = ["slow", "unit", "contract", "integration"]
```

### 前端测试与构建
```bash
# console/package.json 第 6-19 行
npm run build              # tsc -b && vite build
npm run lint              # eslint .
npm run test              # vitest
npm run test:run          # vitest run (单次)
npm run test:coverage     # vitest run --coverage

# ESLint + Prettier
npm run format            # prettier --write
npm run format:check      # prettier --check
```

**Vite 配置** (`console/vite.config.ts` 第 50-94 行):
```typescript
test: {
  globals: true,
  environment: "jsdom",
  setupFiles: ["./src/test/setup.ts"],
  css: true,
  exclude: ["**/node_modules/**", "**/dist/**", "..."],
  coverage: {
    provider: "v8",
    reporter: ["text", "html", "json", "lcov"],
    include: ["src/**/*.{ts,tsx}"],
    fail_under: 30  // 最低覆盖率 30%
  }
}
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
- pylint (Python lint + 样式检查)
- black (Python 格式化, 行长 79)
- flake8 (Python 额外检查)
- mypy (Python 类型检查)
- prettier (TS/TSX 格式化)
- add-trailing-comma (自动加尾逗号)
```

**激活**: `pre-commit install` (仓库提供)

**集成建议**:
1. 新增 Dashboard 后端代码: 遵循黑名单排除规则（skills/ 目录），运行 `make test`
2. 前端代码: 运行 `npm run lint` 和 `npm run test:run`
3. 提交前: 运行 pre-commit hooks (`pre-commit run --all-files`)

---

## 附加信息

### src/qwenpaw 顶层目录结构
```
src/qwenpaw/
├── __init__.py
├── __main__.py
├── __version__.py
├── constant.py                 # 工作目录、文件路径常量
├── exceptions.py
├── app/                        # ← FastAPI 应用核心
│   ├── _app.py                 # 主应用、中间件、lifespan
│   ├── routers/                # API 路由 (include token_usage.py)
│   ├── auth.py                 # 鉴权中间件
│   └── ...
├── token_usage/                # ← Token 追踪模块
│   ├── __init__.py
│   ├── manager.py              # TokenUsageManager 单例
│   ├── buffer.py
│   └── storage.py
├── cli/                        # CLI 命令
│   ├── main.py                 # 入口，定义所有子命令
│   ├── app_cmd.py              # `qwenpaw app` 启动 uvicorn
│   └── ...
├── config/                     # 配置管理
├── agents/                     # 代理实现
├── plugins/                    # 插件系统
└── ...
```

### console/src 顶层目录结构
```
console/src/
├── main.tsx                    # React 入口
├── App.tsx                     # 主应用（ThemeProvider + Router）
├── api/                        # HTTP 请求层
│   ├── config.ts               # API 基础配置
│   ├── request.ts              # 通用 fetch 包装
│   ├── authHeaders.ts
│   └── modules/                # 按模块组织 API
│       ├── auth.ts
│       ├── token_usage.ts
│       └── ...
├── layouts/                    # 全局布局
│   ├── MainLayout/index.tsx    # 主框架 (Header + Sidebar + Content)
│   ├── Sidebar.tsx             # 左侧菜单
│   ├── Header.tsx              # 顶部导航
│   └── constants.ts            # 菜单常量、路由映射
├── pages/                      # 各页面
│   ├── Chat/
│   ├── Control/
│   ├── Settings/               # 包括 TokenUsage, AgentStats
│   ├── Agent/
│   └── ...
├── components/                 # 可复用组件
├── hooks/                      # 自定义 hooks
├── contexts/                   # React Context (主题、插件等)
├── stores/                     # Zustand 状态管理
├── locales/                    # i18n 资源文件
├── styles/                     # 全局样式
└── utils/                      # 工具函数
```

### pyproject.toml 关键依赖
```ini
# 已声明（检验现有）:
fastapi               (通过 agentscope-runtime 1.1.4)
uvicorn >= 0.40.0
pydantic              (通过 fastapi)
httpx >= 0.27.0

# Dashboard 可用:
无需新增 — 使用已有的 fastapi, pydantic, httpx
```

### console/package.json 关键依赖
```json
{
  "antd": "^5.29.1",
  "@agentscope-ai/design": "^1.0.14",
  "@ant-design/plots": "^2.6.8",
  "@ant-design/x-markdown": "^2.2.2",
  "react-router-dom": "^7.13.0",
  "zustand": "^5.0.3",
  "ahooks": "^3.9.6",
  "i18next": "^25.8.4",
  "react-i18next": "^16.5.4"
}
```

---

## 快速集成清单

### 后端集成
- [ ] 创建 `src/qwenpaw/app/routers/dashboard.py` (含 dashboard 端点)
- [ ] 在 `src/qwenpaw/app/routers/__init__.py` 导入并 include
- [ ] 在 `src/qwenpaw/app/_app.py` 第 646 行后添加 router 挂载
- [ ] 实现数据源访问（复用 token_usage 单例，其他数据直接读文件或从 app.state 获取）

### 前端集成
- [ ] 创建 `console/src/pages/Dashboard/` 页面组件
- [ ] 创建 `console/src/api/modules/dashboard.ts` 请求层
- [ ] 在 `console/src/layouts/MainLayout/index.tsx` 添加 Route
- [ ] 在 `console/src/layouts/Sidebar.tsx` 添加菜单项
- [ ] 在 `console/src/layouts/constants.ts` 添加 pathToKey 映射
- [ ] 在 `console/src/locales/*.json` 添加 i18n keys

### 构建与部署
- [ ] `cd console && npm run build`
- [ ] `cp -r console/dist/. ../src/qwenpaw/console/`
- [ ] `cd .. && pip install -e .`
- [ ] 验证: `qwenpaw app --port 8088`

---

**本笔记将持续维护。** 遵循此指南，Coding Agent 可直接动手集成，无需重复阅读源码。
