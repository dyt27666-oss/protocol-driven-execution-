<div align="center">

<h1>🧭 protocol-driven-execution</h1>

<p><strong>长周期任务协议化推进框架 · Claude / Codex 都能跑的 7-stage 自驱执行协议</strong></p>

<p>
  <a href="./README.md"><strong>中文</strong></a>
  ·
  <a href="./README.en.md">English</a>
</p>

<p>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/Claude_Code-skill-7c3aed.svg" alt="Claude Code Skill">
  <img src="https://img.shields.io/badge/Codex_CLI-adapter-111827.svg" alt="Codex CLI adapter">
  <img src="https://img.shields.io/badge/platform-Linux_|_macOS-success.svg" alt="Linux/macOS">
  <img src="https://img.shields.io/badge/status-stable-green.svg" alt="Status: Stable">
</p>

<p>把"用户全程盯流程"降级为"只在 chips 出现时排版反馈" · Stage 0 contract → 7-stage 循环 → 独立 review → checkpoint</p>

</div>

---

## 🤔 为什么需要它？

长周期工程任务（跨 5+ step、跨多会话、含架构决策）有两个常被忽略的协作失败模式：

- 🌫️ **用户精力是稀缺资源**——盯流程的每个 step 消耗远比关键决策点参与多
- 🔍 **AI 自审会产生确认偏差**——同一个 context 内的 review 找不到自己的盲区
- 📚 **临时决策无法跨会话恢复**——context 压缩后，"为什么这样设计"的来龙去脉丢失

### 效果对比

<table>
<tr>
<th align="left">😩 Before（无协议）</th>
<th align="left">✨ After（用 protocol-driven-execution）</th>
</tr>
<tr>
<td>

```
用户: "实现监控系统"
AI: 写完一通 → 用户审核 → 改 → 改 →
     用户疲劳 → 关键决策 AI 自己定 →
     后续发现架构有问题 → 回退一周工作
```

</td>
<td>

```
用户: "/coop-protocol 实现监控系统"
AI: Stage 0 contract chips 对齐 scope →
    自驱 Stage 1-2 → Codex review → P1
    chips 批量决策 → 用户 5 分钟排版 →
    Stage 5 修复 → Stage 6 commit
```

</td>
</tr>
</table>

---

## ✨ 核心特性

- 🧭 **7-stage 流水线** — Stage 0 contract → 1 实施 → 2 validation → 3 review → 4 协商 → 5 修复 → 6 checkpoint
- 🎯 **chips 反馈机制** — 架构决策用 AskUserQuestion / Codex adapter 结构化选项，2-3 秒判断完
- 🔬 **独立 reviewer 强制** — 外部进程 / subagent / 自审标注，禁止裸提交无审查代码
- 📊 **P1 三层分类** — P1-decision 必问 / P1-defaultable 推荐推进 / P1-low-impact 写日志
- 🛡️ **按风险复审** — 修复触及接口/schema/安全必跑 full re-review，不按数量
- 📋 **跨会话恢复** — Stage 0 contract + TaskList 自洽快照，不依赖完整对话历史
- 🎨 **领域无关** — coding / docs / research / strategy 任务通用，自带 domain validation 矩阵

---

## 📦 安装

### 方式一：clone 到 Claude Code skill 路径（推荐）

```bash
git clone https://github.com/dyt27666-oss/protocol-driven-execution-.git \
  ~/.claude/skills/protocol-driven-execution
```

### 方式二：作为子模块嵌入项目

```bash
cd <your-plugin-project>/skills/
git submodule add https://github.com/dyt27666-oss/protocol-driven-execution-.git
```

### 方式三：手动复制

直接 `git clone` 后把 `SKILL.md` + `references/` 拷贝到你的 skill 目录。

---

## 🚀 使用

### 基础：让 Claude 启动协议

在任意会话中告诉 Claude：

```
启动 protocol-driven-execution 协议来实施 <你的任务>
```

或在 `/skills` 列表里启用后用：

```
/protocol-driven-execution
```

Claude 会自动走启动 SOP：评估适用性 → 拆 step → chips 对齐 checkpoint / reviewer / /loop 参数 → 进入循环。

### 进阶：手动指定 Stage 0 contract

启动前你可以预先写好 contract，Claude 会从其中提取 scope / non-goals / acceptance criteria：

```markdown
## Step 1: <名称> — Stage 0 contract

### scope
- <要交付的产物 1>
- <要交付的产物 2>

### non-goals
- <显式排除项>

### acceptance criteria
- <可验证的验收点>

### affected artifacts
- new / modify / delete / protected: <files>

### rollback plan
- <如何回退>
```

详见 [`references/stage-0-contract.md`](references/stage-0-contract.md)。

### Codex CLI：使用 chips adapter

Codex 原生 UI chips 已有官方 feature flag。先启用并重启 Codex：

```bash
codex features enable default_mode_request_user_input
```

如果新会话仍没有原生 `request_user_input`，协议不会静默降级为 AI 自己决定，而是按顺序选择 backend：

```text
request_user_input → omx question → scripts/codex_chips.py → plain-text record
```

本地 fallback 可直接模拟：

```bash
python3 scripts/codex_chips.py ask --spec /tmp/chips.json
```

所有 fallback 决策都会写入 `.chips/decisions.jsonl`，后续 checkpoint / ADR / 知识库都能引用。

---

## 🏗️ How It Works

### 7-stage 循环全景

```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│  Stage 0: contract（scope / DoD / 回滚 / 决策点预报）          │
│       │                                                        │
│       ▼                                                        │
│  Stage 1: 实施 ──────────── ✗ scope 需改 ──┐                  │
│       │                                    │                  │
│       ▼                                    │                  │
│  Stage 2: domain validation                │                  │
│       │ (coding=tests / docs=outline /     │                  │
│       │  research=evidence audit / ...)    │                  │
│       │ ✗ FAIL → 退回 Stage 1              │                  │
│       ▼                                    │                  │
│  Stage 3: 独立 review ──────────┐          │                  │
│       │                         │          │                  │
│       │ (外部进程 / subagent)    │          │                  │
│       │                         ▼          │                  │
│       ▼                  ┌─ 横切机制 ─┐    │                  │
│  Stage 4: 协商           │ • chips     │    │                  │
│       │ (P0 必修 /        │ • TaskList  │    │                  │
│       │  P1-decision     │ • /loop(可选)│    │                  │
│       │  chips 必问 /     └────────────┘    │                  │
│       │  P1-defaultable                     │                  │
│       │  推荐推进 + 标注 /                    │                  │
│       │  P1-low-impact 日志 /                │                  │
│       │  P2 日志 / 无效给证据)                │                  │
│       ▼                                    │                  │
│  Stage 5: 修复（按风险复审）                  │                  │
│       │ (公共接口 / schema / 安全 → full)    │                  │
│       │ (单函数本地修复 → targeted re-review)│                  │
│       ▼                                    │                  │
│  Stage 6: checkpoint                       │                  │
│       │ (commit / PR / patch /              │                  │
│       │  doc savepoint / no VCS)            │                  │
│       └──────────────── TaskUpdate completed                  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 关键招数

1. **Stage 0 contract 冻结范围** —— 实施过程中改 scope 必须停下来回 Stage 0 重新冻结，禁止边做边改
2. **P1 三层降级** —— 不是所有 P1 都 chips，可逆 + 有先例的走 P1-defaultable 自动推进
3. **按风险复审** —— 修复后是否重跑 review 看"改了什么"不是"修了几个 P0"
4. **/loop 报告轮只读** —— 报告轮禁止 TaskUpdate / 改代码 / commit，避免周期性偷偷改状态

---

## 📁 项目结构

```
protocol-driven-execution/
├── SKILL.md                                # skill 入口（Claude Code 加载点）
├── references/
│   ├── stage-0-contract.md                 # Stage 0 模板 + 实例
│   ├── six-phase-loop.md                   # 7-stage 完整流程图
│   ├── review-mechanism.md                 # reviewer 三种形态 + P1 三层
│   ├── chips-design.md                     # chips 设计模式
│   ├── codex-chips-adapter.md              # Codex backend 优先级 + fallback 日志
│   ├── codex-native-ui-chips.md             # 原生 request_user_input 启用与排障
│   ├── decision-points-checklist.md        # 6 维度判定 + 边界 case
│   ├── checkpoint-strategies.md            # 5 种 checkpoint 形态
│   └── loop-progress-template.md           # /loop 可选机制（只读不写）
├── scripts/
│   └── codex_chips.py                      # Codex CLI fallback chips 记录器
├── README.md                               # 中文（你正在看的这份）
├── README.en.md                            # English
└── LICENSE
```

---

## ❓ FAQ

<details>
<summary><b>这和 GitFlow / PR review / TDD 是什么关系？</b></summary>

protocol-driven-execution 是 **agent orchestration wrapper**，**不替代**团队既有质量流程：

- PR review 是协议 Stage 3 review 的一种形态（外部 human reviewer）
- TDD 适用于 coding 任务的 Stage 2 domain validation
- ADR 可以从 chips 决策记录中生成，但 ADR 本身是产物不是协议机制

协议是给 AI agent 用的工作流框架，团队既有流程是上层验收手段，互补不冲突。

</details>

<details>
<summary><b>没有 git / 不是 coding 任务能用吗？</b></summary>

可以。Stage 6 checkpoint 有 5 种形态：commit / PR / patch / **doc savepoint** / **no VCS**。Stage 2 domain validation 矩阵覆盖 coding / docs / research / design / schema / strategy 6 类任务。

不适用的场景：**纯 LLM API 调用**（无 TaskList / 结构化 chips 工具）、**完全脚本化 pipeline**（无交互式 chips 反馈）。

</details>

<details>
<summary><b>chips 太多会让用户疲劳吗？</b></summary>

协议设计了 P1 三层降级 + "按推荐推进（不问我）" 选项：

- P1-decision 必问（不可逆 / 跨多系统）
- P1-defaultable 按 reviewer 推荐 + 标注（局部 / 有先例）
- P1-low-impact 写 issue log（不阻塞 step）

实测在 G1-A v3.3（12 ISSUE / 4 轮 review）中，用户排版次数控制在 8 次以内。

</details>

<details>
<summary><b>/loop 是必备的吗？</b></summary>

**不**。默认不开。/loop 是可选辅助看板，只在以下场景启用：

- 任务跨 ≥ 1 个工作日
- 用户希望被动 polling 看进度（不主动 TaskList）

跨会话恢复**不依赖** /loop（cron 不跨 session），依赖 checkpoint summary + TaskList。

</details>

<details>
<summary><b>独立 reviewer 用什么？</b></summary>

按隔离强度优先选：

1. **外部进程 reviewer**（最高隔离）：`codex exec --ephemeral` / 外部 LLM API
2. **Subagent**（session 内隔离）：Claude `Task` / Codex `spawn_agent`
3. **自审 + 标注**（降级）：受限环境时使用，必须显式标注「自审查」

详见 [`references/review-mechanism.md`](references/review-mechanism.md)。

</details>

<details>
<summary><b>协议 P0 修复后必须重跑完整 review 吗？</b></summary>

**按风险，不按数量**：

| 修复触及范围 | 复审强度 |
|------------|---------|
| 仅本地 / 单函数内部 | targeted re-review |
| 公共接口 / schema | full re-review |
| 安全 / 认证 / 状态机 | full re-review |
| 仅 P1-low-impact / P2 | 可跳过 |

一处接口破坏修复 > 五处局部 P0 修复在风险上。

</details>

<details>
<summary><b>能用在 Codex CLI 或其他 agent 平台吗？</b></summary>

协议核心机制依赖：
- task tracker（TaskCreate / TaskUpdate / TaskList）
- 结构化决策 prompt（AskUserQuestion 或等价）
- skill 加载机制

Claude Code 全支持。Codex CLI 通过 `references/codex-chips-adapter.md` 支持协议化 chips：原生 `request_user_input` 可用时走 UI chips，不可用时走 `omx question` / `scripts/codex_chips.py` / plain-text record fallback。**纯 LLM API** 无原生 task tracker，需要自行实现。

</details>

---

## 🛡️ 兼容性

| 项目 | 版本 |
|------|------|
| Claude Code | 1.x（已在 G1-A v3.3 实战验证） |
| Codex CLI | 支持 adapter fallback；原生 UI chips 取决于 `request_user_input` feature |
| 其他 agent | 需平台具备 task tracker + 结构化决策 prompt 或等价 adapter |
| 外部依赖 | 无 |

---

## 🌱 起源

源自 [`gaming_ai_meta_skills`](https://github.com/gamexproject/gaming_ai_meta_skills) G1-A v3.3 监控基础设施实施过程沉淀（2026-05）：

- 12 个 ISSUE 闭环 / 4 轮 Codex adversarial review
- 9 个 skill 改造 / 15 个 Python 模块 / 11 个 schema
- 用户提议沉淀为可复用 skill ("复用的机会很多")

经 Codex 二轮 review 协商后版本（4 P0 / 6 P1 / 3 P2 全部修复）。

---

## 🤝 贡献

欢迎 issue 和 PR！

- 🐛 [报告 Bug](https://github.com/dyt27666-oss/protocol-driven-execution-/issues/new)
- 💡 [功能建议](https://github.com/dyt27666-oss/protocol-driven-execution-/issues/new)
- 🌍 翻译到其他语言

---

## 📄 License

[MIT](./LICENSE) © 2026 dyt27666-oss
