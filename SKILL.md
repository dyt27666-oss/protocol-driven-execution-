---
name: protocol-driven-execution
description: |
  长周期任务的协议化推进框架，适用于任何领域：跨多个 step 的实施任务、跨多次会话的重构、
  涉及架构决策且需要独立审查的工程项目。把"用户全程盯流程"降级为"只在架构决策点排版"。
user-invocable: true
---

# protocol-driven-execution — 协议化推进框架

> **领域无关**：不限于 RL / 游戏 AI / 任何特定技术栈。本 skill 沉淀的是**协作模式**，
> 不是某个项目的实施细节。

## 核心洞察

长周期工程任务有两个常被忽略的人机协作模式：

1. **用户精力是稀缺资源**——用户不应该全程盯每个 step 的执行，但必须在不可逆决策点参与
2. **AI 的盲区需要独立 reviewer 检测**——自审会产生确认偏差，必须由隔离上下文的 reviewer 攻击结论

本协议把这两点系统化：让 AI 在确定性 step 上自驱动，在决策点和审查发现处主动暂停等用户。

---

## 一句话工作流

```
[用户启动] → AI 拆 step + 起 TaskList + /loop
  ↓
[循环] Step → self-test → 独立 reviewer → 分类 P0/P1/P2
              ↓                            ↓
              失败回退                   chips 让用户排版 P1
              ↓                            ↓
              修复 + 重跑                 修复 + commit
  ↓
[完成] CronDelete /loop + SUMMARY.md + chips 问下一步
```

---

## 何时启用本协议

满足**任一**条件：

1. step 数 ≥ 5 且有顺序依赖
2. 任意 step 涉及不可逆决策（schema / 架构 / 接口 / 安全边界）
3. 预期 ≥ 2 个用户排版判断点
4. 跨多个会话（context 限制可能截断）

不满足时直接干，不要 over-protocol。

---

## 五个核心机制

### 1. Step → self-test → review → 协商 → fix → commit

每个 step 走 6 阶段，缺一不可：

| 阶段 | 输出 | 通过条件 |
|------|------|---------|
| 1. 实施 | 代码 / 文档 / schema | 完成定义的 deliverable |
| 2. self-test | 模块级测试 PASS | 必须有覆盖关键路径的 self-test |
| 3. 独立 review | reviewer 输出 issue 列表 | 跑完不论结论 |
| 4. 协商 | P0/P1/P2/无效分类 | P0 必修；P1 需用户排版；P2 记录；无效给反驳理由 |
| 5. 修复 | 修复代码 | self-test 再次 PASS |
| 6. commit | 含 review 来源的 commit message | 推到约定 remote |

**铁律**：
- 没 self-test PASS 不进 review
- 带 P0 不入主线
- 多个 P1 批量打包 chips，不要分次问

### 2. chips 反馈

架构决策 / 修复方案 / 协议调整必须用 chips（结构化选项），不用纯文本。

设计原则见 `references/chips-design.md`。

### 3. /loop 周期进度报告

启动协议同步起 /loop（默认 10 分钟），输出**颜色分明**的进度概要：

```
🟢 已完成：<列 task>
🔵 进行中：<列 task>
⚪ 待办：<列 task 前 3 条>
🔴 阻塞：<列 task 或"无">
📊 总进度: X / N (百分比)
```

**关键**：/loop 报告轮**只输出概要，不做实际工作**。

### 4. TaskList 全程维护

启动时一次性创建全部 step，每完成一个**立即**标 completed，禁止批量更新。

理由：
- /loop 进度依赖 TaskList 真实状态
- 跨会话恢复执行状态
- 让用户随时看清推进位置

### 5. commit 协议（启动时用户约定）

- 默认 push 哪个 remote
- 哪些 remote 只在指令下推
- 是否走标准 footer
- 是否允许 amend（默认 NO）

写入项目的 memory / CLAUDE.md，跨会话生效。

---

## 完整启动 SOP

### 步骤 1 — 评估适用性

不是所有任务值得开协议。先看 step 数 / 决策点 / 排版点 / 跨会话。不适用直接干。

### 步骤 2 — 拆 step + TaskList

读规划 → 拆 step → 一次性 TaskCreate 全部。

每个 task 的 subject 写到看一眼就知道做什么（不写"实施 step 3"，写"step 3: <具体模块> <具体动作>"）。

### 步骤 3 — chips 对齐协议参数

```python
AskUserQuestion(questions=[
    {"question": "默认 commit/push 范围？",
     "options": [
         {"label": "主 remote (Recommended)", "description": "default 自动推"},
         {"label": "全部 remote", "description": "每次都推所有"},
         {"label": "每次问", "description": "保守"}
     ]},
    {"question": "独立 reviewer 用谁？",
     "options": [
         {"label": "Codex 外部进程 (Recommended)", "description": "完全隔离 context"},
         {"label": "subagent (Task / spawn_agent)", "description": "同 session 内隔离 context"},
         {"label": "自审 + 标注", "description": "无独立 reviewer 时的降级"}
     ]},
    {"question": "/loop 间隔？",
     "options": [
         {"label": "10m (Recommended)", "description": "默认"},
         {"label": "5m", "description": "高频追踪"},
         {"label": "20m", "description": "低频"},
         {"label": "不开 /loop", "description": "用户主动 TaskList"}
     ]}
])
```

### 步骤 4 — 循环执行

每个 step 走 6 阶段。遇到架构决策 / P1 出 chips。

### 步骤 5 — 收尾

- 最后 step commit 后生成 COMPLETION_SUMMARY.md
- CronDelete 关闭 /loop
- TaskList 验证全部 completed
- chips 问下一步

---

## 协议失效信号

主动观察以下信号并提议调整：

| 信号 | 调整方向 |
|------|----------|
| 同一 step review 出 ≥ 5 个 P0 | 回退上一 step 重新设计 |
| 连续 2 个 step 无 P1 反馈 | reviewer 不够 adversarial，更换 |
| 用户连续 3 次回 "都行 / 你定" | chips 太抽象，简化或合并 |
| /loop 报告 ≥ 3 轮同 task in_progress | 该 task 拆细 |
| context 接近压缩阈值且当前 step 未完 | 启动 step 收尾 + 短 summary commit |

---

## 与其他 skill 的关系

- **adversarial-review / expert-review** — 本协议第 3 阶段调用，做 P0 检测
- 任何 **pipeline-orchestrator 类 skill** — 项目层状态机；本 skill 是**元层**协作协议，不冲突
- **using-gaming-ai-meta-skills** 中的 `references/codex-tools.md` — Codex 派遣方式

---

## 引用资料

- `references/six-phase-loop.md` — 6 阶段循环完整流程图 + 每阶段输出标准
- `references/chips-design.md` — chips 设计模式（架构决策 / P1 批处理 / 协议调整 / preview 用法）
- `references/loop-progress-template.md` — /loop 进度报告固定模板
- `references/review-mechanism.md` — 独立 reviewer 三种形态 + 协商分类标准
- `references/decision-points-checklist.md` — 何时必须 chips / 何时可以默认推进 的判定清单
