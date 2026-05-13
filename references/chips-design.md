# chips 设计模式

> 何时用 chips（通过 AskUserQuestion / Codex chips adapter）+ 怎么设计选项 + 反例。


## 平台适配入口

协议中的 `chips` 是逻辑接口，不绑定单一 UI API：

- Claude Code：优先使用 `AskUserQuestion`。
- Codex CLI：必须按 `codex-chips-adapter.md` 选择 backend：`request_user_input` → `omx question` → `scripts/codex_chips.py` → emergency plain text + record。
- fallback 不是免问用户；fallback 只改变呈现方式，仍必须产生结构化 answer 和 `.chips/decisions.jsonl` 日志。

---

## 何时必须用 chips

| 场景 | 必须 chips？ | 理由 |
|------|-------------|------|
| 不可逆架构决策（P1-decision） | ✅ | 用户必须显式表态 |
| 多个 P1-decision 修复方案 | ✅ | 让用户一次性排版 |
| 协议本身调整 | ✅ | 元层决策 |
| Stage 6 checkpoint 形态选择 | ✅ | 启动 SOP 必问 |
| P1-defaultable 修复 | ❌ | 按先例 / 推荐推进 + 标注 |
| P1-low-impact / P2 修复 | ❌ | 写 issue log |
| P0 修复 | ❌ | 必修没排版空间 |
| 单步骤推进确认 | ❌ | 直接干，用户中断你即可 |
| 信息查询 | ❌ | 直接答 |

详见 `decision-points-checklist.md` 中的 6 维度判定表。

---

## 通用规则

1. **2-4 个选项**（系统自动加 "Other"）
2. **第一个加 "(Recommended)"** 并说明推荐理由
3. **每个选项 1 句 trade-off**
4. **多个问题打包**（同一 chips 最多 4 个 question，超过分批）
5. **不要在 chips 里要求长文输入**

---

## 模式 A：二选一架构决策

```python
ask_chips(questions=[{
    "question": "状态机字段是平铺还是嵌套？",
    "header": "schema 决策",
    "options": [
        {
            "label": "平铺 (Recommended)",
            "description": "可直接 schema validate top-level，少一层 nesting"
        },
        {
            "label": "嵌套",
            "description": "结构清晰但 validation 复杂"
        }
    ],
    "multiSelect": False
}])
```

---

## 模式 B：批量 P1-decision

```python
ask_chips(questions=[
    {
        "question": "P1-decision-1: <schema 字段去留>?",
        "header": "P1-1",
        "options": [
            {"label": "去掉 (Recommended)", "description": "新代码已不使用"},
            {"label": "保留兼容", "description": "向后兼容但冗余"},
            {"label": "按推荐推进（不问我）", "description": "降级到 P1-defaultable"}
        ]
    },
    {
        "question": "P1-decision-2: <enum 是否保留>?",
        "header": "P1-2",
        "options": [
            {"label": "保留 + reducer 拒绝 (Recommended)", "description": "schema 宽 + reducer 严"},
            {"label": "移除 enum", "description": "schema 强约束但破坏约定"},
            {"label": "按推荐推进（不问我）", "description": "降级到 P1-defaultable"}
        ]
    }
])
```

**新增第 3 选项 "按推荐推进"**：让用户**一键降级**为 P1-defaultable，减少疲劳。

---

## 模式 C：协议调整

```python
ask_chips(questions=[{
    "question": "/loop 报告 3 轮同 task in_progress，调整？",
    "header": "协议调整",
    "options": [
        {"label": "拆细该 task (Recommended)", "description": "可能跨多 commit"},
        {"label": "继续等", "description": "确实在做"},
        {"label": "暂停 /loop", "description": "跟踪意义不大"}
    ]
}])
```

---

## 模式 D：preview 代码对比

```python
ask_chips(questions=[{
    "question": "选择实现风格",
    "header": "实现",
    "options": [
        {
            "label": "Option A (Recommended)",
            "description": "<trade-off>",
            "preview": "def foo():\n    # A 实现\n    ..."
        },
        {
            "label": "Option B",
            "description": "<trade-off>",
            "preview": "def foo():\n    # B 实现\n    ..."
        }
    ]
}])
```

---

## 反例

- ❌ "这个 P1 怎么处理？" — 没给选项
- ❌ 6+ 选项 — 太多
- ❌ "你觉得呢？" — 不是 chips
- ❌ "继续吗？" — 没必要 chips
- ❌ 选项 label 只写技术名词，不写 trade-off
- ❌ 把 P1-low-impact 也 chips — 过度协议化

---

## 用户回 "都行 / 你定"

不要继续追问，按 "(Recommended)" 执行，并在 checkpoint 中标注：

```
注：方案选择基于默认推荐（用户授权 AI 自主选择）
```

**同时**：把该决策降级写入项目 memory，下次类似决策直接按先例不再 chips。

---

## 多 chips 节奏

- 每个 step **最多 1 次** chips（除非协商 P1-decision 批量）
- 协商批量 chips 把所有 P1-decision 一次性问完，不分次
- chips 之间不要插入 "thinking…" 状态消息
- 一个 chips 最多 4 个 question，超过分批且**间隔至少跨 1 个 step**

---

## chips 设计自检

写完 chips 前自问 3 个问题：

1. **这是 P1-decision 吗？**（不是的话不要 chips）
2. **trade-off 描述里能让用户 3 秒判断选哪个吗？**（不能就重写）
3. **Recommended 选项是否有明确推荐理由？**（没有就重新想）

任一问题答 "否" → chips 设计不合格，重做。
