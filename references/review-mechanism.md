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

## 协商分类标准

| 级别 | 标准 | 处理 |
|------|------|------|
| **P0** | 数据正确性 / 安全边界 / 协议违反 / 接口不兼容 | 必修，不修不 commit |
| **P1** | 行为差异但都自洽 / 性能 trade-off / 接口设计偏好 | chips 让用户排版 |
| **P2** | 注释 / 命名 / 不影响功能 | 写 issue log，下 step 再说 |
| **无效** | reviewer 误判 | 给反驳理由（必须 verify 过），不修 |

## 协商流程

### 第一步：分类（AI 主动）

读完 review 报告后，按上述标准给每条 issue 打标签。

### 第二步：P0 直接修

不需要用户排版。修完跑 self-test。

### 第三步：P1 批量 chips

把所有 P1 一起 chips：

```
question: "review 出 N 个 P1，请逐一排版"

P1-1: <描述> → 选项 A / B / C
P1-2: <描述> → 选项 A / B
...
```

### 第四步：P2 记录

写入 issue log（如 `docs/issues/` 或项目 markdown 文档）。

### 第五步：无效项反驳

不能简单标"无效"，必须给 verify 证据：

```
- issue-X: <描述> → 反驳理由：grep 验证 reducer/schema/launcher 三处全用同一字段名一致；可能是 reviewer 看错。
```

## 修复后是否需要二轮 review

| 修复规模 | 需要二轮？ |
|---------|-----------|
| < 5 处 P0 | 否，commit |
| ≥ 5 处 P0 | 是，再跑一轮 review 确认 |
| 触及核心架构（如 schema / 状态机） | 是，无论多少处 |
| 仅 P2 修复 | 否 |

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
