<div align="center">

<h1>🧭 step-to-step-chips</h1>

<p><strong>Protocol-driven execution framework for long-horizon tasks · Let Claude self-drive the 7-stage loop, you only weigh in at architectural decisions</strong></p>

<p>
  <a href="./README.md">中文</a>
  ·
  <a href="./README.en.md"><strong>English</strong></a>
</p>

<p>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/Claude_Code-skill-7c3aed.svg" alt="Claude Code Skill">
  <img src="https://img.shields.io/badge/platform-Linux_|_macOS-success.svg" alt="Linux/macOS">
  <img src="https://img.shields.io/badge/status-stable-green.svg" alt="Status: Stable">
</p>

<p>Downgrade "user babysits the whole process" to "user weighs in only when chips appear" · Stage 0 contract → 7-stage loop → Codex independent review</p>

</div>

---

## 🤔 Why?

Long-horizon engineering tasks (5+ steps, multi-session, architectural decisions) have two common collaboration failure modes:

- 🌫️ **User attention is a scarce resource** — babysitting every step costs far more than weighing in at key decision points
- 🔍 **AI self-review has confirmation bias** — same-context review can't find its own blind spots
- 📚 **Ad-hoc decisions don't survive session compaction** — "why was this designed this way" gets lost

### Before vs After

<table>
<tr>
<th align="left">😩 Before (no protocol)</th>
<th align="left">✨ After (with step-to-step-chips)</th>
</tr>
<tr>
<td>

```
User: "Implement the monitoring system"
AI: writes a chunk → user reviews →
    revise → revise → user fatigue →
    AI decides key trade-offs alone →
    architecture problem found later →
    week of work rolled back
```

</td>
<td>

```
User: "/coop-protocol implement monitoring"
AI: Stage 0 contract chips align scope →
    self-drive Stage 1-2 → Codex review →
    P1 chips batch decisions → user
    weighs in 5 min → Stage 5 fix →
    Stage 6 commit
```

</td>
</tr>
</table>

---

## ✨ Features

- 🧭 **7-stage pipeline** — Stage 0 contract → 1 implement → 2 validation → 3 review → 4 negotiate → 5 fix → 6 checkpoint
- 🎯 **chips feedback** — Architectural decisions via AskUserQuestion structured options, 2-3 sec to judge
- 🔬 **Mandatory independent reviewer** — External process / subagent / annotated self-review; no naked commits without review
- 📊 **P1 three-tier classification** — P1-decision must ask / P1-defaultable proceed-with-rationale / P1-low-impact log
- 🛡️ **Risk-based re-review** — Fixes touching interfaces/schemas/security trigger full re-review, not based on count
- 📋 **Cross-session recovery** — Stage 0 contract + TaskList self-contained snapshot, no dependence on full chat history
- 🎨 **Domain-agnostic** — Works for coding / docs / research / strategy tasks, includes domain validation matrix

---

## 📦 Installation

### Option 1: Clone to Claude Code skill path (recommended)

```bash
git clone https://github.com/dyt27666-oss/step-to-step-chips.git \
  ~/.claude/skills/step-to-step-chips
```

### Option 2: Add as submodule

```bash
cd <your-plugin-project>/skills/
git submodule add https://github.com/dyt27666-oss/step-to-step-chips.git
```

### Option 3: Manual copy

`git clone` then copy `SKILL.md` + `references/` to your skill directory.

---

## 🚀 Usage

### Basic: Have Claude start the protocol

In any session, tell Claude:

```
Start the protocol-driven-execution protocol to implement <your task>
```

Or invoke as a slash command:

```
/protocol-driven-execution
```

Claude will run the startup SOP: assess applicability → break into steps → chips align checkpoint / reviewer / /loop params → enter the loop.

### Advanced: Pre-write Stage 0 contract

You can pre-draft the contract; Claude will extract scope / non-goals / acceptance criteria:

```markdown
## Step 1: <name> — Stage 0 contract

### scope
- <deliverable 1>
- <deliverable 2>

### non-goals
- <explicit exclusions>

### acceptance criteria
- <verifiable acceptance points>

### affected artifacts
- new / modify / delete / protected: <files>

### rollback plan
- <how to roll back>
```

See [`references/stage-0-contract.md`](references/stage-0-contract.md).

---

## 🏗️ How It Works

### 7-stage loop overview

```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│  Stage 0: contract (scope / DoD / rollback / decision points)  │
│       │                                                        │
│       ▼                                                        │
│  Stage 1: implement ──────── ✗ scope changes ──┐               │
│       │                                         │              │
│       ▼                                         │              │
│  Stage 2: domain validation                     │              │
│       │ (coding=tests / docs=outline /          │              │
│       │  research=evidence audit / ...)         │              │
│       │ ✗ FAIL → back to Stage 1                │              │
│       ▼                                         │              │
│  Stage 3: independent review ──┐                │              │
│       │                        │                │              │
│       │ (external proc /       │                │              │
│       │  subagent)             ▼                │              │
│       ▼                ┌─ Cross-cutting ─┐      │              │
│  Stage 4: negotiate    │ • chips         │      │              │
│       │ (P0 must-fix / │ • TaskList      │      │              │
│       │  P1-decision   │ • /loop(optional)│     │              │
│       │  chips ask /   └─────────────────┘     │              │
│       │  P1-defaultable                        │              │
│       │  recommended + log /                   │              │
│       │  P1-low-impact log /                   │              │
│       │  P2 log / invalid w/ evidence)          │              │
│       ▼                                         │              │
│  Stage 5: fix (risk-based re-review)            │              │
│       │ (public interface / schema / security → full)          │
│       │ (single-function local fix → targeted re-review)        │
│       ▼                                         │              │
│  Stage 6: checkpoint                            │              │
│       │ (commit / PR / patch /                  │              │
│       │  doc savepoint / no VCS)                │              │
│       └──────────────── TaskUpdate completed                   │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Key principles

1. **Stage 0 contract freezes scope** — Changing scope mid-flight requires going back to Stage 0; no on-the-fly contract mutation
2. **P1 three-tier downgrade** — Not all P1 needs chips; reversible + with-precedent ones go P1-defaultable auto-advance
3. **Risk-based re-review** — Whether to re-run review depends on "what changed" not "how many P0s fixed"
4. **/loop report turns are read-only** — Report turns forbid TaskUpdate / file changes / commits

---

## 📁 Project Structure

```
step-to-step-chips/
├── SKILL.md                                # Skill entry (Claude Code loads here)
├── references/
│   ├── stage-0-contract.md                 # Stage 0 template + example
│   ├── six-phase-loop.md                   # 7-stage full flow diagram
│   ├── review-mechanism.md                 # Reviewer forms + P1 three-tier
│   ├── chips-design.md                     # AskUserQuestion design patterns
│   ├── decision-points-checklist.md        # 6-dimension judgment + edge cases
│   ├── checkpoint-strategies.md            # 5 checkpoint forms
│   └── loop-progress-template.md           # /loop optional mechanism (read-only)
├── README.md                               # 中文
├── README.en.md                            # English (you are here)
└── LICENSE
```

---

## ❓ FAQ

<details>
<summary><b>How does this relate to GitFlow / PR review / TDD?</b></summary>

step-to-step-chips is an **agent orchestration wrapper**; it **does not replace** existing team quality processes:

- PR review is one form of Stage 3 review (external human reviewer)
- TDD applies to coding-task Stage 2 domain validation
- ADR can be generated from chips decision logs, but ADR is an artifact not a protocol mechanism

The protocol is a workflow framework for AI agents; team processes are upper-level acceptance — complementary, not conflicting.

</details>

<details>
<summary><b>Can it be used without git / for non-coding tasks?</b></summary>

Yes. Stage 6 checkpoint has 5 forms: commit / PR / patch / **doc savepoint** / **no VCS**. Stage 2 domain validation matrix covers coding / docs / research / design / schema / strategy.

Not applicable: **raw LLM API calls** (no TaskList / AskUserQuestion tools), **fully scripted pipelines** (no interactive chips feedback).

</details>

<details>
<summary><b>Won't too many chips fatigue the user?</b></summary>

The protocol designed P1 three-tier downgrade + "Proceed with recommendation (don't ask me)" option:

- P1-decision must ask (irreversible / cross-system)
- P1-defaultable proceed per reviewer recommendation + log (local / with precedent)
- P1-low-impact write to issue log (doesn't block step)

In G1-A v3.3 (12 ISSUEs / 4 review rounds) real-world test, user chip-answering events stayed under 8.

</details>

<details>
<summary><b>Is /loop required?</b></summary>

**No**. Off by default. /loop is an optional dashboard, enabled only when:

- Task spans ≥ 1 working day
- User prefers passive polling over actively running TaskList

Cross-session recovery does **not** depend on /loop (cron doesn't survive sessions); it depends on checkpoint summary + TaskList.

</details>

<details>
<summary><b>Which independent reviewer should I use?</b></summary>

Choose by isolation strength (highest first):

1. **External process reviewer** (highest isolation): `codex exec --ephemeral` / external LLM API
2. **Subagent** (in-session isolation): Claude `Task` / Codex `spawn_agent`
3. **Annotated self-review** (downgrade): For constrained environments, must explicitly label as "self-review"

See [`references/review-mechanism.md`](references/review-mechanism.md).

</details>

<details>
<summary><b>Must I re-run full review after every P0 fix?</b></summary>

**By risk, not count**:

| Fix touches | Re-review intensity |
|------------|---------------------|
| Local / single-function internal | targeted re-review |
| Public interface / schema | full re-review |
| Security / auth / state machine | full re-review |
| Only P1-low-impact / P2 | can skip |

One interface-breaking P0 fix > five local P0 fixes in risk.

</details>

<details>
<summary><b>Can I use it with Codex CLI or other agent platforms?</b></summary>

Core mechanisms depend on:
- Task tracker (TaskCreate / TaskUpdate / TaskList)
- Structured decision prompts (AskUserQuestion or equivalent)
- Skill loading mechanism

Claude Code: fully supported. Codex CLI: partial (via `spawn_agent` + custom tools). **Raw LLM API**: no native task tracker; needs custom implementation.

</details>

---

## 🛡️ Compatibility

| Item | Version |
|------|---------|
| Claude Code | 1.x (validated on G1-A v3.3 in production) |
| Codex CLI | Partial (needs custom task tracker) |
| Other agents | Requires task tracker + structured decision prompts |
| External deps | None |

---

## 🌱 Origin

Distilled from [`gaming_ai_meta_skills`](https://github.com/gamexproject/gaming_ai_meta_skills) G1-A v3.3 monitoring infrastructure implementation (2026-05):

- 12 ISSUEs closed / 4 rounds of Codex adversarial review
- 9 skills refactored / 15 Python modules / 11 schemas
- User proposed distilling into a reusable skill ("plenty of reuse opportunity")

Current version after two-round Codex review negotiation (all 4 P0 / 6 P1 / 3 P2 addressed).

---

## 🤝 Contributing

Issues and PRs welcome!

- 🐛 [Report a bug](https://github.com/dyt27666-oss/step-to-step-chips/issues/new)
- 💡 [Suggest a feature](https://github.com/dyt27666-oss/step-to-step-chips/issues/new)
- 🌍 Translate to other languages

---

## 📄 License

[MIT](./LICENSE) © 2026 dyt27666-oss
