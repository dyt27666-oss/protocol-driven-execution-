# /loop 进度报告模板（领域无关）

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

## 间隔选择

| 任务规模 | 推荐间隔 |
|---------|---------|
| < 1 天 | 5m |
| 1-3 天 | 10m |
| > 3 天 | 20m |
| 跨多会话 | 不开 /loop，手动 TaskList |

## 输出格式（固定）

```
🟢 已完成：Step 1 / Step 2 / Step 3

🔵 进行中：Step 4

⚪ 待办：Step 5 / Step 6 / Step 7

🔴 阻塞：无

📊 总进度: 3 / 7 task 完成（43%）
```

## 关键约束

1. **只输出概要，不做工作** —— /loop 报告轮不写代码不改文件
2. **从 TaskList 取真实状态** —— 不要凭记忆
3. **emoji 必须有** —— 颜色区分
4. **总进度行必须有** —— 用户最常看的一行
5. **不重复 task 描述** —— subject 已说明

## 副产品检测

报告输出过程中如发现：
- task 状态与实际不一致 → 立即 TaskUpdate 修正
- task 长期 in_progress（≥ 3 轮）→ 提示考虑拆细
- 全部 completed → 提示 CronDelete 关闭 /loop

## 关闭 /loop

任务完成或暂停时必须 CronDelete：

```bash
CronList  # 找 cron id
CronDelete --id <cron_id>
```

否则 /loop 持续 7 天自动到期前一直发报告。
