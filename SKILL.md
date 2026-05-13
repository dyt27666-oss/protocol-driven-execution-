---
name: protocol-driven-execution
description: |
  长周期任务的协议化推进框架，适用于 Claude Code agentic workflow 内任意领域（coding / docs / research / strategy）：
  跨多个 step 的实施任务、跨多次会话的工程项目、涉及架构决策且需要独立审查的工作。
  把"用户全程盯流程"降级为"只在架构决策点排版反馈"。
user-invocable: true
---

# protocol-driven-execution — 协议化推进框架

## 适用范围（重要）

**适用平台**：Claude Code agentic workflow（依赖 `TaskCreate` / `AskUserQuestion` / `/loop` / `Skill` 等能力）；Codex CLI（通过 `references/codex-chips-adapter.md` 适配 `request_user_input` / `omx question` / local CLI fallback）。
**不适用平台**：纯 LLM API 调用 / 无 task tracker 的 IDE assistant / 完全脚本化 pipeline——协议核心机制无法兑现。

**适用领域（cross-domain）**：
- 工程类：代码实施 / 重构 / schema 设计 / 跨 skill 改造
- 文档类：长报告 / 设计文档 / 标准制定
- 研究类：跨多 step 的调研 / 评测 / 实验规划
- 策略类：长周期方案制定 / 多阶段决策

**不是替代品**：协议是 **agent orchestration wrapper**，**不替代**团队既有质量流程：
- 不替代 GitFlow / PR review（PR review 是协议第 3 阶段 review 的一种形态）
- 不替代 TDD（TDD 适用于 coding 任务的"domain validation"——见下表）
- 不替代 ADR（chips 决策记录可以喂给 ADR，但 ADR 本身是产物不是协议机制）

---

## 核心洞察

长周期工程任务有两个常被忽略的人机协作模式：

1. **用户精力是稀缺资源**——用户不应该全程盯每个 step 的执行，但必须在不可逆决策点参与
2. **AI 的盲区需要独立 reviewer 检测**——自审会产生确认偏差，必须由隔离上下文的 reviewer 攻击结论

本协议把这两点系统化：让 AI 在确定性 step 上自驱动，在决策点和审查发现处主动暂停等用户。

---

## 一句话工作流

```
[用户启动] → AI 拆 step + 起 TaskList + (可选) /loop
  ↓
[每个 step] 7 stage
  Stage 0: contract（scope / DoD / 回滚 / 决策点预报）
  Stage 1: 实施
  Stage 2: domain validation（按任务类型选验证形式）
  Stage 3: 独立 review
  Stage 4: 协商 P0 / P1-decision / P1-defaultable / P1-low-impact / P2 / 无效
  Stage 5: 修复（按风险判定是否复审）
  Stage 6: checkpoint（commit / PR / patch / doc savepoint / 视项目而定）
  ↓
[完成] (可选) CronDelete /loop + SUMMARY.md + chips 问下一步
```

**横切支撑机制**（不是 stage，是覆盖全流程的工具）：
- chips 反馈（Stage 4 / 协议调整 / 启动 SOP）
- TaskList 全程维护
- /loop 周期报告（可选）

---

## 何时启用本协议

满足**任一**条件：

1. step 数 ≥ 5 且有顺序依赖
2. 任意 step 涉及不可逆决策（schema / 架构 / 接口 / 安全边界 / 成本承诺 / 数据保留）
3. 预期 ≥ 2 个用户排版判断点
4. 跨多个会话（context 限制可能截断）

不满足时直接干，不要 over-protocol。

---

## 协议组成：7 stage + 3 横切机制

### Stage 0：step contract（实施前冻结）

每个 step 开工前必须明确：

| 项 | 内容 |
|----|------|
| **scope** | 本 step 要交付什么（产物级别） |
| **non-goals** | 本 step 不解决什么（防止 scope creep） |
| **acceptance criteria** | 怎么知道完成了（验收标准，是 stage 2 validation 的输入） |
| **affected artifacts** | 允许修改 / 新增 / 删除的文件 / 接口 / 数据 |
| **rollback plan** | 如果中途失败如何回退（branch 删 / patch 撤 / doc 恢复版本） |
| **decision points forecast** | 预判哪几处会出 chips（让用户提前热身） |

Stage 0 写好后，**实施过程中如需修改 scope，必须回 Stage 0 重新冻结**，不能边做边改。

### Stage 1：实施

按 Stage 0 contract 的 scope / affected artifacts 执行。期间 TaskUpdate status=in_progress。

如发现需修改 scope，**必须停下回 Stage 0 重新冻结**，不能边做边改 contract。

### Stage 2：domain validation（按任务类型）

不是所有任务都跑 self-test，按任务类型选验证形式：

| 任务类型 | Stage 2 形态 |
|---------|-------------|
| 代码实施 | 单元测试 / self-test 函数 / 类型检查 |
| 文档 / 报告 | outline 一致性检查 / 引用源头校验 / 结构 checklist |
| 研究 / 调研 | source/evidence audit（引用是否真实存在、声明是否过强） |
| 设计文档 | constraint traceability（每条结论能否反查到需求） |
| schema 设计 | jsonschema validate + 反例 case 跑通 |
| 策略制定 | 决策回溯（每个选择是否给出 trade-off） |

**通用要求**：必须有可验证产物（PASS / FAIL 信号），不接受"我自己检查过没问题"。

### Stage 3：独立 review（隔离强度优先）

reviewer 形态：
- 外部进程 reviewer（最高隔离，如 codex exec --ephemeral / 外部 LLM）
- Subagent（同 session 内隔离 context）
- 自审 + 标注（受限环境降级，必须显式标注「自审查」）

**默认**：选**隔离强度最高且可用**的 reviewer。

详见 `references/review-mechanism.md`。

### Stage 4：协商 P0/P1/P2 分层

review 出的 issue 按风险（不按数量）分类：

| 级别 | 判定标准（按"破坏什么"判定） | 处理 |
|------|----------------------------|------|
| **P0** | 破坏既有调用 / 数据正确性 / 安全承诺 / 协议本身 / 接口兼容 | 必修，不修不进 Stage 6 |
| **P1-decision** | 不可逆决策（schema / 状态机 / 接口 / 安全 / 成本承诺） | chips 必问用户 |
| **P1-defaultable** | 可逆 / 影响未来扩展 / 已有先例 | 按先例或推荐推进 + commit/PR 中标注 |
| **P1-low-impact** | 只影响局部行为 / 不阻塞 step | 写 issue log，下次再说 |
| **P2** | 纯可读性 / 命名 / 注释 | 写 issue log |
| **无效** | reviewer 误判 | 必须给 verify 证据 + 反驳理由 |

详见 `references/review-mechanism.md` + `references/decision-points-checklist.md`。

### Stage 5：修复后复审（按风险）

| 修复触及范围 | 复审强度 |
|---------|---------|
| 仅本地 / 单函数内部 | targeted re-review（review 限定到 diff） |
| 公共接口 / schema / 数据格式 | full re-review |
| 安全边界 / 认证 / 权限 | full re-review |
| 状态机 / 迁移 / 持久化 | full re-review |
| 仅 P1-low-impact / P2 修复 | 可跳过复审 |

**默认**：不确定时跑 full re-review。

### Stage 6：checkpoint（按项目政策）

不是所有项目都"每 step commit + push"。启动时由 chips 与用户约定 checkpoint 形态：

| checkpoint 形态 | 适用场景 |
|----------------|---------|
| commit 直推 | 单人 repo / 个人项目 |
| PR branch + review | 团队 repo / protected main |
| patch file / 草稿 | 实验性分支 / 无 VCS 环境 |
| doc savepoint | 文档类项目（versioned file / 备份） |
| no VCS | 一次性脚本 / 本地探索 |

详见 `references/checkpoint-strategies.md`。

---

## 3 横切机制

### 横切 1：chips 反馈

架构决策 / P1-decision / 协议调整 / 启动 SOP 必须用 chips（结构化选项），不用纯文本。

**强规则：所有 chips 调用必须先经过 chips adapter。**
- Claude Code：优先使用 `AskUserQuestion`。
- Codex CLI：先确认 `default_mode_request_user_input` 已启用并重启；再按 `references/codex-chips-adapter.md` 的优先级使用 `request_user_input` → `omx question` → `scripts/codex_chips.py` → emergency plain text + record。
- 如果当前 Codex Default mode 没有暴露 `request_user_input`，不得让 AI 静默代选；必须使用 fallback 并写入 `.chips/decisions.jsonl`。

设计原则见 `references/chips-design.md`。

### 横切 2：TaskList 全程维护

启动时一次性创建全部 step（含 Stage 0 contract 摘要作为 description），每完成一个**立即**标 completed，禁止批量更新。

理由：
- 跨会话恢复执行状态
- 让用户随时看清推进位置
- 任何 /loop 进度依赖真实状态

### 横切 3：周期 /loop 进度报告（可选）

**默认不开**。仅当满足以下**全部**条件时启用：
- 任务跨 ≥ 1 个工作日
- 用户希望被动 polling 看进度（不主动 TaskList）
- 报告频率合理（不会成为噪音）

**铁律**：
- /loop 报告轮**只读 TaskList，不改任何状态**
- 发现状态不一致：在报告里**建议**调整，让用户决定，不偷偷 TaskUpdate
- 跨会话恢复**依赖 checkpoint summary 而非 /loop**（cron 不跨 session）

详见 `references/loop-progress-template.md`。

---

## 完整启动 SOP

### 步骤 1 — 评估适用性

不是所有任务值得开协议。先看 step 数 / 决策点 / 排版点 / 跨会话。不适用直接干。

### 步骤 2 — 拆 step + 起 TaskList

读规划 → 拆 step → 一次性 TaskCreate 全部。

每个 task 的 subject 写到看一眼就知道做什么，description 含 Stage 0 contract 五项的草稿。

### 步骤 3 — chips 对齐协议参数

先选择当前平台可用的 chips backend：Claude Code 用 `AskUserQuestion`；Codex 按 `references/codex-chips-adapter.md` 选择 backend。下面是逻辑 payload，不要求所有平台逐字使用同一 API。

```python
ask_chips(questions=[
    {"question": "checkpoint 形态？",
     "options": [
         {"label": "commit 直推 (Recommended)", "description": "单人 repo"},
         {"label": "PR branch", "description": "团队 repo / protected main"},
         {"label": "doc savepoint", "description": "文档类项目"},
         {"label": "no VCS", "description": "一次性脚本"}
     ]},
    {"question": "独立 reviewer？",
     "options": [
         {"label": "外部进程 (Recommended)", "description": "最高隔离"},
         {"label": "subagent", "description": "session 内隔离"},
         {"label": "自审 + 标注", "description": "降级"}
     ]},
    {"question": "/loop 进度报告？",
     "options": [
         {"label": "不开 (Recommended)", "description": "默认；主动 TaskList 即可"},
         {"label": "10m 间隔", "description": "跨日任务 + 用户希望 polling"},
         {"label": "20m 间隔", "description": "低频"}
     ]}
])
```

### 步骤 4 — 每个 step 走 7 stage

Stage 0（contract）→ Stage 1（实施）→ Stage 2（domain validation）→ Stage 3（review）→ Stage 4（协商）→ Stage 5（修复 + 按风险复审）→ Stage 6（checkpoint）。

遇到 P1-decision 出 chips。P1-defaultable 按推荐推进 + 标注。P1-low-impact / P2 写 issue log。

### 步骤 5 — 收尾

- 最后 step checkpoint 后生成 COMPLETION_SUMMARY.md
- 如有 /loop：CronDelete 关闭
- TaskList 验证全部 completed
- chips 问下一步

---

## 协议失效信号

主动观察以下信号并提议调整：

| 信号 | 调整方向 |
|------|----------|
| 同一 step review 出 ≥ 5 个 P0 | 回退上一 step 重新设计 Stage 0 contract |
| 连续 2 个 step 无 P1 反馈 | reviewer 不够 adversarial，更换 |
| 用户连续 3 次回 "都行 / 你定" | chips 太抽象 / 触发条件太松，调整判定表 |
| /loop 报告 ≥ 3 轮同 task in_progress | 该 task 拆细 |
| context 接近压缩阈值且当前 step 未完 | 启动 step 收尾 + 短 summary commit |
| reviewer 反复发现 Stage 0 contract 不清 | Stage 0 模板需要细化 |

---

## 与其他 skill 的关系

- **adversarial-review / expert-review** — 本协议 Stage 3 调用
- 任何 **pipeline-orchestrator 类 skill** — 项目层状态机；本 skill 是**元层**协作协议
- **using-gaming-ai-meta-skills** — Codex 派遣方式

---

## 引用资料

- `references/stage-0-contract.md` — Stage 0 step contract 模板 + 示例
- `references/six-phase-loop.md` — Stage 1-6 完整流程 + 每 stage 输出标准（含 domain validation 矩阵）
- `references/review-mechanism.md` — 独立 reviewer 三种形态 + 协商分类标准 + 按风险复审
- `references/chips-design.md` — chips 设计模式 + 必问 / 可默认 判定
- `references/codex-chips-adapter.md` — Codex CLI chips backend 优先级、fallback CLI、决策日志规范
- `references/codex-native-ui-chips.md` — Codex 原生 `request_user_input` 启用、重启、排障说明
- `references/decision-points-checklist.md` — P1-decision / P1-defaultable / P1-low-impact 判定清单
- `references/checkpoint-strategies.md` — 5 种 checkpoint 形态 + 选择决策树
- `references/loop-progress-template.md` — /loop 模板（可选机制）
