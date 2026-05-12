# chips 设计模式（领域无关）

> 何时用 chips（AskUserQuestion）+ 怎么设计选项 + 反例。

## 何时必须用 chips

| 场景 | 必须 chips？ | 理由 |
|------|-------------|------|
| 不可逆架构决策 | ✅ | 用户必须显式表态 |
| 多个 P1 修复方案 | ✅ | 让用户一次性排版 |
| 协议本身的调整 | ✅ | 元层决策 |
| 默认推进路径有岔路 | ✅ | 防止 AI 单方面定 |
| 单步骤推进确认 | ❌ | 直接干，用户中断你即可 |
| 信息查询 | ❌ | 直接答 |
| 探讨性问题 | ❌ | 简短 2-3 句即可 |

## 通用规则

1. **2-4 个选项**（系统自动加 "Other"）
2. **第一个加 "(Recommended)"** 并说明推荐理由
3. **每个选项 1 句 trade-off**
4. **多个问题打包**（同一 chips 最多 4 个 question）
5. **不要在 chips 里要求长文输入**

## 模式 A：二选一架构决策

适用：spec 中两个等价方案需要用户表态。

```python
AskUserQuestion(questions=[{
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

## 模式 B：批量 P1 修复

```python
AskUserQuestion(questions=[
    {
        "question": "P1-1: <某 schema 字段去留>?",
        "header": "P1-1",
        "options": [
            {"label": "去掉 (Recommended)", "description": "新代码已不使用"},
            {"label": "保留兼容", "description": "向后兼容但冗余"}
        ]
    },
    {
        "question": "P1-2: <某 enum 是否保留>?",
        "header": "P1-2",
        "options": [
            {"label": "保留 + reducer 拒绝 (Recommended)", "description": "schema 宽 + reducer 严"},
            {"label": "移除 enum", "description": "schema 强约束但破坏约定"}
        ]
    }
])
```

## 模式 C：协议调整

```python
AskUserQuestion(questions=[{
    "question": "/loop 报告 3 轮同 task in_progress，调整？",
    "header": "协议调整",
    "options": [
        {"label": "拆细该 task (Recommended)", "description": "可能跨多 commit"},
        {"label": "继续等", "description": "确实在做"},
        {"label": "暂停 /loop", "description": "跟踪意义不大"}
    ]
}])
```

## 模式 D：preview 代码对比

```python
AskUserQuestion(questions=[{
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

## 反例

- ❌ "这个 P1 怎么处理？" — 没给选项
- ❌ 6+ 选项 — 太多
- ❌ "你觉得呢？" — 不是 chips
- ❌ "继续吗？" — 没必要 chips
- ❌ 选项 label 只写技术名词，不写 trade-off

## 用户回 "都行 / 你定"

不要继续追问，按 "(Recommended)" 执行，并在 commit 中标注：

```
注：方案选择基于默认推荐（用户授权 AI 自主选择）
```

## 多 chips 节奏

- 每个 step **最多 1 次** chips（除非协商 P1 批量）
- 协商批量 chips 把所有 P1 一次性问完，不分次
- chips 之间不要插入 "thinking…" 状态消息
