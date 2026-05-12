# 7-stage 循环详解

> 每个 step 必经的 Stage 0-6（共 7 stage），缺一不可。
> （文件名保留历史 six-phase-loop.md，内容已升级到 7 stage 含 Stage 0 contract。）

## 流程图

```
┌─────────────────────────────────────────────────────┐
│  Stage 0: contract（scope / DoD / 回滚 / 决策点）   │
│  - 5 项必填: scope / non-goals / acceptance /       │
│             affected artifacts / rollback           │
│  - 写入 TaskList description 或 markdown            │
│  ✗ contract 不冻结不能进 Stage 1                    │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│  Stage 1: 实施                                      │
│  - 严格按 contract.scope / affected_artifacts 执行  │
│  - TaskUpdate status=in_progress                    │
│  ✗ 需修改 scope → 回 Stage 0 重新冻结              │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│  Stage 2: domain validation                         │
│  - 按任务类型选验证形态（见下表）                   │
│  - 必须有可验证产物（PASS / FAIL 信号）             │
│  ✗ FAIL → 退回 Stage 1                              │
└──────────────────┬──────────────────────────────────┘
                   ↓ PASS
┌─────────────────────────────────────────────────────┐
│  Stage 3: 独立 review                               │
│  - 派外部进程 / subagent / Task                     │
│  - 不论结论跑完                                     │
│  - 输出 issue 列表                                  │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│  Stage 4: 协商                                      │
│  - 分类: P0 / P1-decision / P1-defaultable /        │
│         P1-low-impact / P2 / 无效                   │
│  - P0 直接修                                        │
│  - P1-decision 批量 chips 给用户                    │
│  - P1-defaultable 按先例 / 推荐推进 + 标注         │
│  - P1-low-impact / P2 写 issue log                  │
│  - 无效给 verify 证据 + 反驳理由                    │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│  Stage 5: 修复                                      │
│  - 按协商结论改                                     │
│  - Stage 2 validation 必须再 PASS                   │
│  - 按风险决定复审强度（见下表）                     │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│  Stage 6: checkpoint                                │
│  - 按项目政策选形态: commit / PR / patch /          │
│                     doc savepoint / no VCS          │
│  - 必含: review 来源 + 修复来源 + 回滚锚点          │
│  - TaskUpdate status=completed                      │
└─────────────────────────────────────────────────────┘
```

---

## Stage 0 输出标准

见 `stage-0-contract.md`。

---

## Stage 2 domain validation 矩阵

按任务类型选验证形态：

| 任务类型 | Stage 2 形态 | PASS 信号 |
|---------|-------------|-----------|
| 代码实施 | 单元测试 / self-test 函数 / 类型检查 | `pytest -q` 0 exit / "self-test PASS" |
| 文档 / 报告 | outline 一致性 + 引用源校验 + 结构 checklist | checklist 全勾 + 引用 grep 命中 |
| 研究 / 调研 | source/evidence audit | 每条声明有可追溯来源 |
| 设计文档 | constraint traceability | 每条结论可反查需求 ID |
| schema 设计 | jsonschema validate + 反例 case | validate 通过 + 反例 reject |
| 策略制定 | 决策回溯 | 每个选择有 trade-off 文档 |

**通用要求**：必须有可验证产物（PASS / FAIL 信号），不接受"我自己检查过没问题"。

---

## Stage 5 复审强度（按风险）

| 修复触及范围 | 复审强度 |
|------------|---------|
| 仅本地 / 单函数内部 | targeted re-review |
| 公共接口 / schema / 数据格式 | full re-review |
| 安全 / 认证 / 权限 | full re-review |
| 状态机 / 迁移 / 持久化 | full re-review |
| 仅 P1-low-impact / P2 修复 | 可跳过复审 |

**默认**：不确定时跑 full re-review。

---

## Stage 6 checkpoint 形态

见 `checkpoint-strategies.md`。

---

## 每 stage 输出标准（汇总）

| Stage | 输出 | 通过条件 |
|-------|------|---------|
| 0 contract | 5 项 + 可选预报 | 5 项必填齐全 |
| 1 实施 | 符合 contract 的产物 | scope 内 + 不超 non-goals |
| 2 validation | PASS / FAIL 信号 | 必须 PASS |
| 3 review | issue 列表 | 跑完即可（不论结论） |
| 4 协商 | 分类表 + 反驳证据 | P0 全标 / P1 分层 / 无效有证据 |
| 5 修复 | 修复 diff + 复审结果 | validation 再 PASS + 复审通过 |
| 6 checkpoint | 持久化产物 | 含 review 来源 + 修复来源 + 回滚锚点 |

---

## 反例：不要这样做

- ❌ 跳过 Stage 0 直接实施
- ❌ Stage 2 验证用"我自己看过"代替可验证产物
- ❌ Stage 3 review 全部采纳（包括明显误判）
- ❌ 带 P0 进 Stage 6
- ❌ Stage 6 不标 review 来源
- ❌ Stage 5 修复后不跑 Stage 2 直接进 Stage 6
