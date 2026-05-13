# Stage 6: checkpoint 形态

> 不是所有项目都"每 step commit + push"。本文档列 5 种 checkpoint 形态 + 选择决策树。

## 为什么不是 commit 一种形态

"每 step commit + push" 在以下场景不合适：
- 团队 repo + protected main → 应走 PR
- 实验性分支 / 个人探索 → 草稿 patch / 不入 VCS
- 文档项目 / 报告 → versioned file / 备份点
- 一次性脚本 → 无需 VCS

把 commit 写死成协议规定会与现实工程流程冲突。

---

## 5 种 checkpoint 形态

### 形态 1：commit 直推

```bash
git add <files> && git commit -m "..." && git push <remote> <branch>
```

适用：
- 单人 repo / 个人项目
- 写权限直推 main / unprotected branch
- 用户明确要求实时同步

不适用：
- 团队 repo（应走 PR）
- protected branch（push 会被 reject）

### 形态 2：PR branch + review

```bash
git checkout -b feature/<step>
git add <files> && git commit -m "..."
git push -u <remote> feature/<step>
gh pr create --title "..." --body "..." --base main
```

适用：
- 团队 repo
- protected main
- 需要 PR review 流程（与 stage 3 review 互补不互斥）

### 形态 3：patch file / 草稿

```bash
git diff > /tmp/<step>.patch
# 或
git stash save "<step> draft"
```

适用：
- 实验性 / 不确定是否保留
- 跨多 step 累积成大改动后一次性入 VCS

### 形态 4：doc savepoint

```bash
cp <doc>.md <doc>.v<N>.md.bak
# 或：项目用 versioned 文件系统
```

适用：
- 文档项目
- 无 git 但需要版本回退能力

### 形态 5：no VCS

适用：
- 一次性脚本
- 本地探索
- nuke-on-completion 类任务

---

## 选择决策树

```
项目有 VCS（git / svn 等）？
├── 否 → no VCS 或 doc savepoint
└── 是 → 
    repo 是否团队共享？
    ├── 是 → PR branch + review
    └── 否 → 
        是否实验性？
        ├── 是 → patch file / 草稿
        └── 否 → commit 直推
```

---

## 启动协议时的 chips（已在 SKILL.md 步骤 3）

```python
ask_chips(questions=[{
    "question": "checkpoint 形态？",
    "options": [
        {"label": "commit 直推 (Recommended)", "description": "单人 repo / unprotected branch"},
        {"label": "PR branch", "description": "团队 repo / protected main"},
        {"label": "doc savepoint", "description": "文档类项目"},
        {"label": "no VCS / patch file", "description": "实验性 / 一次性脚本"}
    ]
}])
```

---

## checkpoint 内容标准

不论形态，checkpoint **必须包含**：

1. **review 来源标注**：commit message / PR description / patch 注释里标 "Review: <reviewer + 日期>"
2. **修复来源标注**：P0 修复 a 处 / P1 按用户排版方案修复 b 处 / P2 推迟
3. **回滚锚点**：commit hash / PR 号 / patch 文件名，写入 Stage 0 contract 的 rollback plan 字段供下一 step 使用

---

## 跨 step checkpoint 链

每个 step 的 Stage 6 checkpoint 应能 chain 起来形成回退序列：

```
Step 1: commit abc123 (or PR #42)
Step 2: commit def456 — based on abc123
Step 3: ...
```

回退时可定位到任意 step 的 checkpoint 重新开始，不必从头来。
