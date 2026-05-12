# step-to-step-chips

> 长周期工程任务的协议化推进框架（Claude Code skill）。

把"用户全程盯流程"降级为"只在架构决策点排版反馈"，让 AI 在确定性 step 上自驱动，在不可逆决策点和审查发现处主动暂停等用户。

## 核心机制

1. **6 阶段循环**：Step → self-test → 独立 review → 协商 P0/P1/P2 → fix → commit
2. **chips 反馈**：架构决策 / 修复方案以 AskUserQuestion 结构化选项形式回馈
3. **周期 /loop 进度报告**：颜色分明的 🟢🔵⚪🔴 进度概要
4. **TaskList 全程维护**：跨会话执行状态可恢复
5. **commit 协议**：启动时约定 push 范围 / amend 规则

## 适用场景

满足任一条件：
- step 数 ≥ 5 且有顺序依赖
- 任意 step 涉及不可逆决策（schema / 架构 / 接口 / 安全边界）
- 预期 ≥ 2 个用户排版判断点
- 跨多个会话

## 不适用

- 单 step 改动
- 本地实验
- 没有独立 review 价值的零碎修复

## 文件结构

```
SKILL.md                                    # skill 入口
references/
  six-phase-loop.md                         # 6 阶段循环详解
  chips-design.md                           # chips 设计模式
  decision-points-checklist.md              # 决策点判定清单
  review-mechanism.md                       # 独立 reviewer 机制
  loop-progress-template.md                 # /loop 进度报告模板
```

## 安装为 Claude Code skill

clone 后放入 Claude Code skill 加载路径，或作为子模块嵌入 plugin 项目：

```bash
git clone https://github.com/dyt27666-oss/step-to-step-chips.git \
  ~/.claude/skills/step-to-step-chips
```

## 起源

源自 [`gaming_ai_meta_skills`](https://github.com/gamexproject/gaming_ai_meta_skills) G1-A v3.3 监控基础设施实施过程沉淀（2026-05）：
- 12 个 ISSUE / 4 轮 Codex review / 9 个 skill 改造
- 用户提议沉淀为可复用 skill（"复用的机会很多"）

## License

参照源 repo。
