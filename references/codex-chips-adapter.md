# Codex chips adapter

> Codex-native structured decision adapter for protocol-driven-execution.
> Goal: keep the chips contract stable even when the host UI differs from Claude Code.

## Problem

The original protocol used Claude Code `AskUserQuestion` as the chips surface. Codex may run in several surfaces:

- Codex CLI, Codex App, or VS Code Codex Extension where native `request_user_input` is available;
- Codex CLI with an OMX-attached tmux session where `omx question` can render structured prompts;
- Codex CLI / App / VS Code where native structured input is unavailable in the current session;
- non-interactive execution mode such as `codex exec` / CI-style runs.

The protocol must not silently degrade P1-decision checkpoints into AI-only decisions. Every chips decision must produce a structured answer and a durable decision log.

## Adapter contract

All chips calls use this logical interface:

```text
ask_chips(question_set, context) -> structured_answer + decision_log
```

A `question_set` contains 1-4 questions. Each question has:

- `id`: stable snake_case id;
- `header`: short label;
- `question`: one concrete decision;
- `options`: 2-4 options, first option recommended;
- optional `allow_other`: whether free-form fallback is accepted.

The decision log must include:

- timestamp;
- adapter backend used;
- question ids;
- selected labels or free-form answer;
- whether the result came from recommended default, explicit user choice, or emergency fallback.

## Backend priority

Use the first available backend:

1. **Codex native `request_user_input`**
   - Preferred for Codex CLI / Codex App / VS Code Codex Extension.
   - Requires `default_mode_request_user_input` enabled and a restarted session.

2. **CLI-only OMX structured question**
   - Use only in Codex CLI when `omx` and an attached tmux renderer are available.

3. **CLI/local terminal fallback**
   - Use `scripts/codex_chips.py ask --spec <json>` only when a local terminal prompt can be displayed.

4. **App / VS Code textual fallback**
   - Render numbered options in the conversation body.
   - Parse the user’s explicit reply.
   - Record the answer to `.chips/decisions.jsonl`.

5. **Non-interactive stop**
   - In non-interactive execution mode, do not auto-select P1-decision choices.
   - Emit a `decision_required` record and stop.

## Hard rules

- P1-decision, protocol adjustment, and startup SOP choices must go through this adapter.
- If no structured backend is available, do not let the model choose silently; ask the user in plain text and record the answer.
- If the user says "都行", "你定", or equivalent, choose option 1 and record `source: recommended_default_authorized`.
- Never batch more than 4 questions in one chips call.
- Never use chips for P0 fixes, P1-low-impact, P2, or ordinary continuation prompts.
- If a fallback backend is used, include that fact in the checkpoint summary.

## Codex feature note

Codex CLI 0.130.0 exposes an app-server protocol schema for `item/tool/requestUserInput`, but the feature may be disabled in Default mode. Check:

```bash
codex features list | rg 'request_user_input|default_mode_request_user_input'
```

If `default_mode_request_user_input` is disabled, enable it and restart Codex before expecting input-box UI chips:

```bash
codex features enable default_mode_request_user_input
# then exit and start a new Codex session
```

The feature is under development in Codex CLI 0.130.0, so fallback backends remain required. A running Codex session usually cannot gain the new tool mid-session because the tool list is negotiated at session start.

## Local CLI fallback examples

Create a spec:

```json
{
  "backend": "local_cli",
  "context": "startup_sop",
  "questions": [
    {
      "id": "checkpoint_strategy",
      "header": "checkpoint",
      "question": "checkpoint 形态？",
      "options": [
        {"label": "commit 直推 (Recommended)", "description": "单人 repo，最快闭环"},
        {"label": "PR branch", "description": "团队 repo 或 protected main"},
        {"label": "doc savepoint", "description": "文档类项目"}
      ]
    }
  ]
}
```

Run:

```bash
python3 scripts/codex_chips.py ask --spec /tmp/chips.json
```

The default log path is `.chips/decisions.jsonl` under the current working directory. Override it with `--log <path>`.


## Native chips smoke test

After enabling the feature and restarting Codex, ask the agent to run a protocol decision point. Expected behavior:

1. The agent calls native `request_user_input` for the chips payload.
2. The current Codex client renders structured options:
   - Codex CLI: options appear in the terminal/TUI input area;
   - Codex App: options appear in the app conversation/input area;
   - VS Code Extension: options appear in the extension conversation/input area.
3. The selected answer returns as structured data.
4. The checkpoint summary records:
   - `backend: request_user_input`
   - `client_surface: cli | app | vscode`
   - `source: explicit_user_choice`.

If the tool is still unavailable after restart, run:

```bash
codex features list | rg 'default_mode_request_user_input'
```

Then use the local fallback while keeping the decision log durable:

```bash
python3 scripts/codex_chips.py ask --spec /tmp/chips.json
```
