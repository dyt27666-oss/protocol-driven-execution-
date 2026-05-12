# 决策点判定清单

> 何时必须 chips 让用户排版 vs 何时可以默认推进。

## 必须 chips（用户排版）

### 1. 不可逆架构决策

- 数据 schema 字段去留
- 状态机阶段切分
- 接口 / 协议形态
- 安全边界（路径 A vs 路径 B）
- 持久化格式选择

**判定**：决策后若想反悔，需要 migration / 兼容层 / 重新跑数据。

### 2. P1 修复方案

review 出的 P1（行为差异但都自洽 / trade-off / 接口设计偏好）必须 chips。

**判定**：多个修复方向都符合 spec，AI 无法单方面排序。

### 3. 协议本身调整

- 更换 reviewer
- 修改 /loop 间隔
- 暂停协议
- 修改 commit 规则

**判定**：影响元层流程的决策。

### 4. step 拆细 / 合并

- 单 step 跨多个 commit
- 多个相似 step 是否合并
- step 之间的依赖顺序

**判定**：影响 TaskList 结构的决策。

---

## 可以默认推进（不需要 chips）

### 1. 实施细节（变量名、函数名、文件名）

不影响外部接口的内部细节，AI 按业内常规起名即可。

### 2. P0 修复

review 出的 P0 是 must-fix，没排版空间，直接改。

### 3. P2 修复

P2 是 nice-to-have，记录到 issue log 留待下次，无需现在排版。

### 4. self-test 实现细节

测试用例的具体值、临时目录管理、mock 数据等——属于实现细节。

### 5. commit message 措辞

按 commit 模板填，措辞细节不需要排版。

### 6. 重复性已有先例的操作

如果同类决策在前面 step 已经做过且用户认可，直接复用先例。

---

## 边界 case

### Case 1：spec 描述模糊但只有一个合理解释

→ 不 chips。按合理解释执行，commit message 中标注理解。
如果用户后来发现误解，再回退。

### Case 2：spec 描述清晰但实施时发现实战风险

→ chips。这是发现新问题，需要用户排版（如 G1-A v3.3 conservative_auto Tier 3 改正案）。

### Case 3：用户之前给过类似决策的指导

→ 不 chips（首选）+ commit message 标注引用了哪条历史决策。

### Case 4：reviewer 找到 P0 但 AI 强烈怀疑误判

→ 不直接采纳，先 verify（grep / 读代码 / 跑测试），verify 通过后标"无效"+ 反驳理由。
如果 verify 不通过，按 P0 修。

### Case 5：context 接近压缩阈值

→ 主动启动 step 收尾 + 短 summary commit。
不要硬撑到压缩——上下文丢失成本大于一次 commit 成本。

---

## 决策点的"无效信号"

如果观察到以下信号，说明 chips 设计有问题：

| 信号 | 原因 | 调整 |
|------|------|------|
| 用户回 "都行 / 你定" | 选项区分度不足 | 简化或合并选项 |
| 用户回选 "Other" 且写长文 | chips 选项没覆盖真实需求 | 重做 chips 或承认 chips 不适用 |
| 用户回 "为什么需要问？" | chips 触发条件错误 | 该决策本该默认推进 |
| 同一决策反复 chips | 协议未记录用户偏好 | 把先例写入 memory / CLAUDE.md |
