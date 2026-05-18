# QwenPaw Dashboard 集成代码评审报告

## 总体结论

- 审核结论：**APPROVE_WITH_CHANGES**
- 总体评价：后端和前端集成都符合现有架构设计，未发现阻塞性问题；建议在后续提交中修复下述 should-fix / nice-to-have 问题。


## should-fix（强烈建议修复）

## must-fix（阻塞问题）

当前未发现 must-fix 级别问题。

**问题描述**
- 当通过 /api/dashboard/agents/stats 传入 agent_id 查询参数时，aggregators.agents_stats 先过滤 sessions，但 total_tokens_all 和 total_llm_calls 始终基于所有会话统计。
- 在仅单个 agent 场景下，s_count == all_session_count，导致该 agent 的 tokens/llm_calls 字段被赋值为全局总量，而非该 agent 实际贡献。

### 1. agent_id 过滤时 Agent 统计中的 tokens/llm_calls 统计不准确
[src/qwenpaw/app/routers/dashboard/aggregators.py#L413-L525](/Users/sunyixiang/Desktop/521智能编码/demo1/QwenPaw-source/src/qwenpaw/app/routers/dashboard/aggregators.py)

**风险评估**
- 当前前端未使用 agent_id 过滤，但 API 已对外暴露该参数；一旦被其他调用方使用，将得到严重偏离实际的统计结果，且不易在前端直观发现。
- 该问题仅影响过滤场景，不会导致崩溃或安全问题。

**建议修复方式**
- 方案 A：在存在 agent_id 参数时，先基于过滤后的 sessions 重新计算 total_tokens_all 和 total_llm_calls，再按会话占比分配；
- 方案 B：如果短期内不计划支持精确 per-agent Token 统计，可以暂时移除 agent_id 查询参数，或在 API 文档中标注该参数暂不生效，避免误用。

## nice-to-have（优化建议）

**问题描述**
- 新增的 "dashboard.*" 文案完整添加在 zh/en.json 中，但 ru/ja/id/pt-BR 仅新增了 "nav.opsDashboard"，未包含 dashboard 页面使用的 range/kpi/tab/tokens/conversations/models/skills/empty 等 key。
- 这些语言下访问 Dashboard 时，标题和表格列会回落为英文或 key 字符串，体验不一致。

### 2. Dashboard 多语言文案在部分语言下缺失
[console/src/locales/en.json#L34-L130](/Users/sunyixiang/Desktop/521智能编码/demo1/QwenPaw-source/console/src/locales/en.json)
[console/src/locales/ru.json](/Users/sunyixiang/Desktop/521智能编码/demo1/QwenPaw-source/console/src/locales/ru.json) 等

**建议修复方式**
- 为 ru/ja/id/pt-BR 的 locales JSON 补充与 zh/en 对齐的 "dashboard" 命名空间 key，至少覆盖：标题、时间范围、KPI 名称、Tab 标签、各表格列标题以及空状态文案。
- 若短期内资源有限，可先复制 en.json 的英文文案，保证 key 存在，后续再逐步本地化。

**风险评估**
- 仅影响国际化用户体验，不影响接口功能和系统稳定性。
- 在当前阶段属于体验优化问题。

**问题描述**
- 根目录下  为本次 Dashboard 集成的调研与实现笔记，内容详实但更偏内部工程文档。
- 文件会随源码一起分发，普通用户阅读时可能对其定位和权威性产生困惑。

### 3. _integration-notes.md 建议迁移到正式文档或排除出发行包
[/Users/sunyixiang/Desktop/521智能编码/demo1/QwenPaw-source/_integration-notes.md#L1-L260](/Users/sunyixiang/Desktop/521智能编码/demo1/QwenPaw-source/_integration-notes.md)

**问题描述**
- 根目录下文件 _integration-notes.md 为本次 Dashboard 集成的调研与实现笔记，内容详实但更偏内部工程文档。
- 文件会随源码一起分发，普通用户阅读时可能对其定位和权威性产生困惑。

**风险评估**
- 不影响系统功能和安全性，但可能增加仓库噪音，影响外部用户阅读体验。

**建议修复方式**
- 方案 A：将该笔记移动到 docs/ 或 qwenpaw-wiki/ 目录下，并在 README 或相关文档中增加链接说明；
- 方案 B：若仅用于一次性集成记录，可改名为 .integration-notes.md 并在 .gitignore 中排除，避免进入正式发行包。

## Summary of Changes（变更摘要）

- 后端新增 src/qwenpaw/app/routers/dashboard 子包，引入基于 WORKING_DIR 的只读数据源和聚合逻辑，对 token_usage.json、sessions/ 与 qwenpaw.log 进行 KPI 统计。
- 新增 /api/dashboard/health、/overview、/tokens、/agents/stats、/skills/stats、/models/stats 等接口，并在 _app.py 中通过 dashboard_router 统一挂载。
- Console 侧新增 dashboard 页面（console/src/pages/dashboard），使用 Ant Design 与 @ant-design/plots 实现 KPI 卡片、折线图、饼图和技能排行等可视化组件。
- MainLayout 与 Sidebar 增加 /dashboard 路由和 "运营监控" 菜单项，通过 React.lazy + Suspense 实现懒加载，并在 locales zh/en 中新增 dashboard 命名空间文案。
- 引入 cachetools>=5.3.0 依赖和 model_prices.json，实现 Dashboard 聚合结果的 TTL 缓存以及按模型价格估算 Token 成本，并补充 tests/console_api/test_dashboard_aggregators.py 等单元测试覆盖核心聚合逻辑。