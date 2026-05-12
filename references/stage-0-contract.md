# Stage 0: step contract

> 每个 step 实施前的范围冻结 + 验收 + 回滚 + 决策点预报。

## 为什么需要 Stage 0

直接从"实施"开始的协议有三个失败模式：
1. **Scope creep**：边做边扩大范围，review 时无法判断是否兑现目标
2. **DoD 模糊**：完成标准不清，stage 2 validation 无基准
3. **回滚困难**：失败后不知道改了什么，难以恢复

Stage 0 把这些前置到实施前，让 review 和验证有标尺。

---

## Contract 模板（5 项必填 + 1 项可选）

```markdown
## Step <N>: <名称> — Stage 0 contract

### scope（要交付什么）
- <产物 1>
- <产物 2>

### non-goals（不解决什么）
- <显式排除项 1>
- <显式排除项 2>

### acceptance criteria（怎么知道完成了）
- <验收点 1，必须可验证>
- <验收点 2>

### affected artifacts（允许修改 / 新增 / 删除）
- new: <files>
- modify: <files>
- delete: <files>
- protected: <不许碰的文件，列在这里防误操作>

### rollback plan（失败如何回退）
- branch 删除点 / patch 撤销点 / doc 版本恢复点
- 估计回退耗时

### decision points forecast（预判 chips 位置，可选）
- <预判 1: 哪个设计 / 接口 / 命名可能需要用户排版>
- <预判 2>
```

---

## 实例（来自 G1-A v3.3 Step 3）

```markdown
## Step 3: pipeline-launcher Phase 2.6 重构 — Stage 0 contract

### scope
- 重构 utterance 分片 → 关键词分类 → atom 处置流水线
- 新增 utterance_splitter.py / classifier.py / launcher_ops.py
- 修改 SKILL.md 的 Phase 2.6 章节描述

### non-goals
- 不修改 capability_taxonomy.json schema
- 不改 raw_user_statements 的字段定义
- 不动 stage 1 出口外的任何流程

### acceptance criteria
- 三个 .py 模块 self-test PASS
- 三级关键词命中 / 否定模式 / 英文 word boundary 全部用例覆盖
- Stage 1 hard gate 可代码层验证（verify_stage1_exit 函数）

### affected artifacts
- new: scripts/utterance_splitter.py / classifier.py / launcher_ops.py
- modify: SKILL.md (Phase 2.6 section only)
- protected: capability_taxonomy.json / raw_user_statements schema

### rollback plan
- 新文件 delete + SKILL.md git revert（最近 1 commit）
- 估计回退 < 5 min

### decision points forecast
- conservative_auto 下 Tier 3 atom 处理（保持 unhandled vs 强制升 hard）
- batch_id 幂等是否覆盖 retry 场景
```

---

## Stage 0 何时回退重做

实施过程中如发现：
- **scope 需要扩大** → 必须停下，回 Stage 0 加项 + 重跑 decision points forecast
- **non-goals 边界打破** → 必须停下，重新评估是否拆分 step
- **acceptance criteria 不可验证** → 重写 criteria 让它可验证

**铁律**：边做边改 contract = 没有 contract。

---

## Stage 0 与 chips

Stage 0 本身**不必**触发 chips（除非用户启动协议时明确要求 review 每个 contract）。

但 contract 中的 **decision points forecast** 可以提前告知用户：
"本 step 预期会出现 X 个 chips，分别在 <位置>"。

用户提前热身后，到时候选择会更快。

---

## 跨会话恢复时的 Stage 0

Context 压缩或换会话后，下个会话恢复时**先读最近的 Stage 0 contract**（写在 TaskList description 或单独 markdown）。

这是协议设计的关键弹性：contract 是 step 的"自洽快照"，不依赖完整对话历史。
