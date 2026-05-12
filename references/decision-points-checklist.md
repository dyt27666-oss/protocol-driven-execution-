# 决策点判定清单（含 P1 三层）

> chips 触发条件 + P1 分层 + 边界 case。

## P1 三层分类

不是所有 P1 都需要 chips。按"决策是否可逆 + 影响范围"分三层：

| 层级 | 判定 | 处理 |
|------|------|------|
| **P1-decision** | 不可逆 / 破坏接口 / 跨多系统影响 | **必须 chips** 让用户排版 |
| **P1-defaultable** | 可逆 / 局部 / 已有先例 / 有明显推荐方向 | **按先例 / 推荐推进** + commit/PR 中标注 |
| **P1-low-impact** | 仅命名 / 局部行为 / 不阻塞 step | **写 issue log**，下次再说 |

---

## chips 触发维度（按"破坏什么"判定）

不再用"是否架构"这种模糊词，按以下 6 维度判定：

| 维度 | P1-decision | P1-defaultable | P1-low-impact |
|------|------------|---------------|--------------|
| **irreversibility** | 决策做了改不回（schema migration / 数据丢失） | 可改回（重命名 / 重构内部接口） | 完全可逆 |
| **user-visible behavior** | 改变外部用户能观察到的行为 | 仅日志 / 内部信号 | 不可见 |
| **external contract** | 破坏 API / schema / 协议 | 内部模块接口 | 单函数内部 |
| **cost / risk increase** | 显著增加运行成本 / 资源消耗 | 小幅增加（< 20%） | 无 |
| **security / privacy / compliance** | 任何触及 | — | — |
| **schedule trade-off** | 影响关键交付时间 | 影响子任务时间 | 无 |

**判定规则**：
- 任一维度命中 P1-decision → 是 P1-decision
- 全部维度仅 P1-defaultable / low-impact → 取最高级
- 不确定时**默认 P1-decision**（chips 一下不会错，漏问可能错）

---

## 必须 chips（用户排版）

### 1. 不可逆架构决策

- 数据 schema 字段去留
- 状态机阶段切分
- 接口 / 协议形态
- 安全边界
- 持久化格式
- **成本承诺 / 时间预算变更**（Codex 补的盲区）
- **数据保留 / 隐私 / 许可**（Codex 补的盲区）
- **依赖引入**（新增 third-party lib）
- **向后兼容性破坏**

**判定**：决策后若想反悔需要 migration / 兼容层 / 重新跑数据。

### 2. P1-decision 修复方案

review 出的 P1-decision 必须 chips（多个修复方向都符合 spec，AI 无法单方面排序）。

### 3. 协议本身调整

- 更换 reviewer
- 修改 /loop 间隔
- 暂停协议
- 修改 commit / checkpoint 规则

**判定**：影响元层流程的决策。

---

## 不需要 chips（默认推进）

### 1. 实施细节（变量名、函数名、文件名）

不影响外部接口的内部细节。

### 2. P0 修复

P0 是 must-fix，没排版空间。

### 3. P1-defaultable

按先例 / 默认推荐推进，commit 中标注：

```
注：方案选择基于默认推荐（用户授权 AI 自主选择 P1-defaultable）
```

### 4. P1-low-impact

写 issue log。

### 5. P2

写 issue log。

### 6. self-test / validation 实现细节

测试用例的具体值、临时目录管理等——属于实现细节。

### 7. checkpoint message 措辞

按模板填，措辞细节不需要排版。

### 8. 重复性已有先例的操作

同类决策在前面 step 已经做过且用户认可，直接复用先例。

---

## 边界 case

### Case 1：spec 模糊但只有一个合理解释

→ 不 chips。按合理解释执行，commit 中标注理解。
如用户后来发现误解，再回退。

### Case 2：spec 清晰但实施时发现实战风险

→ chips。这是新问题，需要用户排版（如 G1-A v3.3 conservative_auto Tier 3 改正案）。

### Case 3：用户给过类似决策的指导

→ 不 chips + commit 中标注引用了哪条历史决策。

### Case 4：reviewer 找到 P0 但 AI 强烈怀疑误判

→ 不直接采纳。先 verify（grep / 读代码 / 跑测试）。verify 通过 → 标"无效" + 反驳理由；不通过 → 按 P0 修。

### Case 5：context 接近压缩阈值

→ 主动启动 step 收尾 + 短 summary commit。不要硬撑。

### Case 6：同一决策反复出现

→ 不再 chips。把先例写入 memory / project doc，跨会话生效。

---

## 决策点失效信号

观察到以下信号说明 chips 设计有问题：

| 信号 | 原因 | 调整 |
|------|------|------|
| 用户回 "都行 / 你定" | 选项区分度不足 | 简化或合并 |
| 用户回选 "Other" + 长文 | 选项没覆盖真实需求 | 重做或承认 chips 不适用 |
| 用户回 "为什么需要问？" | 触发条件错误 | 降级到 P1-defaultable |
| 同一决策反复 chips | 协议未记录用户偏好 | 写入 memory |
| chips 一回合超 4 个 question | 协议过密集 | 分批 / 提升到 P1-defaultable |
