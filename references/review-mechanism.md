# review 机制（领域无关）

> 第 3 阶段：独立 review 的三种形态 + 协商分类标准。

## 三种 reviewer 形态

| 形态 | 适用场景 | 工具 | 隔离强度 |
|------|---------|------|---------|
| 外部进程（如 Codex CLI） | 大量代码或长上下文 | `codex exec --ephemeral` | 完全外部进程 |
| 同 session 隔离 agent | 主对话需同步等结果 | Claude `Task` / Codex `spawn_agent` | context 隔离 |
| 自审 + 标注 | 临时方案或受限环境 | 直接读代码 | 无隔离（必须显式标注「自审查」）|

**默认推荐**：外部进程或 subagent，自审作为降级。

## review prompt 模板

```
你是一个 adversarial reviewer。目标是摧毁下面这个 step 的实现。

【实施目标】
<step 在 spec / 规划中的描述>

【实施产物】
- 文件 1: <path> (新增 / 修改)
- 文件 2: <path> (新增 / 修改)

【审查要点】
1. 实施是否真的兑现了目标？（找语义鸿沟）
2. self-test 是否覆盖关键路径？（找 happy path only）
3. 边界条件 / 异常路径？
4. 与依赖模块的接口兼容性？

【输出要求】
- 分级：P0（阻断 commit）/ P1（需用户排版）/ P2（记录即可）
- 每条问题：描述、位置、修复方向、严重性理由
- 如果没找到问题：说明你检查了哪些假设、攻击了哪些路径
```

## 协商分类标准（P1 三层）

| 级别 | 标准（按"破坏什么"判定） | 处理 |
|------|----------------------------|------|
| **P0** | 破坏既有调用 / 数据正确性 / 安全承诺 / 协议本身 / 接口兼容 | 必修，不修不进 Stage 6 |
| **P1-decision** | 不可逆 / 跨多系统影响 / schema / 安全 / 成本承诺 | chips 必问用户 |
| **P1-defaultable** | 可逆 / 局部 / 已有先例 / 有明显推荐方向 | 按先例 / 推荐推进 + 标注 |
| **P1-low-impact** | 仅命名 / 局部行为 / 不阻塞 step | 写 issue log，下次再说 |
| **P2** | 纯可读性 / 注释 / 命名 | 写 issue log |
| **无效** | reviewer 误判 | 必须给 verify 证据 + 反驳理由 |

详见 `decision-points-checklist.md` 的 6 维度判定表。

## 协商流程

### 第一步：分类（AI 主动）

读完 review 报告后，按上表给每条 issue 打标签。**不确定时默认上升一级**（保守）。

### 第二步：P0 直接修

不需要用户排版。修完跑 Stage 2 validation。

### 第三步：P1-decision 批量 chips

把所有 P1-decision 一起 chips（每个含"按推荐推进（不问我）"选项让用户降级）：

```
question: "review 出 N 个 P1-decision，请逐一排版"

P1-decision-1: <描述>
  - 选项 A (Recommended) / B / 按推荐推进（不问我）
P1-decision-2: <描述>
  - 选项 A (Recommended) / B / 按推荐推进（不问我）
```

### 第四步：P1-defaultable 推进 + 标注

按 reviewer 推荐 / 项目先例推进。commit / PR 中标注：

```
P1-defaultable 处理: <方案> (用户授权 AI 自主选择)
```

### 第五步：P1-low-impact / P2 记录

写入 issue log（如 `docs/issues/` 或项目 markdown 文档）。

### 第六步：无效项反驳

不能简单标"无效"，必须给 verify 证据：

```
- issue-X: <描述> → 反驳理由：grep 验证 reducer/schema/launcher 三处全用同一字段名一致；可能是 reviewer 看错。
```

## 修复后是否需要二轮 review

**按风险，不按数量**。任何 P0 修复都至少需要 targeted re-review（针对被改动的代码路径）。

| 修复触及范围 | 需要复审强度 |
|---------|-----------|
| 仅本地 / 单函数内部逻辑 | targeted re-review（review 限定到 diff） |
| 公共接口 / schema 字段 / 数据格式 | full re-review（重跑完整 review） |
| 安全边界 / 认证 / 权限路径 | full re-review |
| 状态机 / 迁移 / 持久化 | full re-review |
| 仅 P1 / P2 修复且无副作用 | 可跳过复审 commit |

**判定原则**：
- 复审决策的输入是"修复改了什么"，不是"修复了几条 P0"
- 一处接口破坏的 P0 修复 > 五处局部 P0 修复在风险上
- 当不确定时，**默认 full re-review**——commit 前多跑一轮的成本远低于回退

## commit message 标准

```
<type>(<scope>): <step 名> Review 协商修复 N 处

- P0 修复 a 处: <要点>
- P1 按用户排版方案修复 b 处: <方案 ID>
- P2 / 无效记录在 issue log

Review: <reviewer 来源, 如 Codex ephemeral 2026-05-12>
```

## 反例

- ❌ review 出 P0 直接改不告诉用户
- ❌ review 全部采纳（包括明显误判）
- ❌ review 没跑 self-test 的代码
- ❌ commit 信息不标 review 来源
- ❌ "无效"项不给反驳理由
