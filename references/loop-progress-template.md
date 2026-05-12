# /loop 进度报告（可选机制）

> 周期性输出 TaskList 进度概要。**可选**机制，默认不开。

## 开启条件（满足全部才开）

- 任务跨 ≥ 1 个工作日
- 用户希望被动 polling 看进度（不主动 TaskList）
- 报告频率合理（不会成为噪音）

不满足任一条件 → 不开 /loop，让用户主动 TaskList。

---

## 启动 /loop

```
/loop 10m 用以下格式给一份 <项目代号> 实施进度概要（参考 TaskList 工具拉最新状态）：

🟢 已完成（绿色，列已 completed 的 task 编号 + subject）
🔵 进行中（蓝色，列 in_progress 的 task）
⚪ 待办（白色，列 pending 的 task 编号 + subject，最多列前 3 条）
🔴 阻塞（红色，列被 reviewer 或架构决策卡住的 task；无则写"无"）

末尾加一行：📊 <项目代号> 总进度: X / N task 完成（百分比）

只输出这份概要，不做其他工作。简洁，无废话。
```

---

## 间隔选择

| 任务规模 | 推荐间隔 |
|---------|---------|
| < 1 天 | 不开 /loop |
| 1-3 天 | 10m |
| > 3 天 | 20m |
| 跨多会话 | 不开 /loop，依赖 checkpoint summary 跨会话恢复 |

---

## 输出格式（固定）

```
🟢 已完成：Step 1 / Step 2 / Step 3

🔵 进行中：Step 4

⚪ 待办：Step 5 / Step 6 / Step 7

🔴 阻塞：无

📊 总进度: 3 / 7 task 完成（43%）
```

---

## 关键约束（铁律）

### 1. 报告轮**只读 TaskList，不改任何状态**

报告轮里**不允许**：
- TaskUpdate（不改状态）
- 写代码 / 改文件
- commit / push
- 调用其他 skill

报告轮里**允许**：
- TaskList 读
- 渲染 emoji 概要
- 在概要里**建议**状态调整（让用户在主执行轮处理）

### 2. 跨会话恢复**不依赖** /loop

cron 不跨 session。跨会话恢复机制：
- 最近一份 checkpoint summary（含 commit hash / PR 号 / Stage 0 contract 摘要）
- TaskList 状态

/loop 报告**不能**作为跨会话锚点。

### 3. 发现状态不一致时

报告里写：

```
⚠️ 检测到状态不一致：Task #5 在主执行轮显示已完成但 TaskList 仍 in_progress。
建议主执行轮 TaskUpdate #5 status=completed 后下次报告会同步。
```

**不偷偷自己 TaskUpdate**——让用户决定。

---

## 副产品检测

报告输出过程中如发现：
- task 状态与实际不一致 → 报告里**建议**，不修
- task 长期 in_progress（≥ 3 轮）→ 建议拆细
- 全部 completed → 建议 CronDelete 关闭 /loop

---

## 关闭 /loop

任务完成或暂停时必须 CronDelete：

```bash
CronList  # 找 cron id
CronDelete --id <cron_id>
```

否则 /loop 持续 7 天自动到期前一直发报告。

---

## 与跨会话恢复的关系

**正确做法**（不依赖 /loop）：

```
[会话 1] Step 1-3 完成 → 写 SUMMARY.md → commit → 关闭会话
[会话 2] 启动时读 SUMMARY.md + TaskList → 从 Step 4 继续
```

**错误做法**（依赖 /loop）：

```
[会话 1] Step 1-3 完成 → /loop 报告 → 关闭会话
[会话 2] 启动时 ??? 无 /loop 报告参考 ??? → 失败
```

`/loop` 是 session 内的辅助看板，**不是**持久化机制。
