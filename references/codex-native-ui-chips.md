# Codex native UI chips

This note documents the shortest path to real Codex input-area chips for `protocol-driven-execution`.

## What was enabled

Codex CLI has an under-development feature flag named `default_mode_request_user_input`. When enabled before a session starts, Codex can expose the native `request_user_input` tool in Default mode. That tool maps to the app-server protocol request:

```text
item/tool/requestUserInput
```

The generated app-server schema contains:

- `ToolRequestUserInputParams`
- `ToolRequestUserInputQuestion`
- `ToolRequestUserInputOption`
- `ToolRequestUserInputResponse`

## Enable command

```bash
codex features enable default_mode_request_user_input
```

This writes the feature flag to `~/.codex/config.toml`:

```toml
[features]
default_mode_request_user_input = true
```

Restart Codex after enabling it. Existing sessions normally cannot gain new tools mid-turn.

## Expected runtime behavior

When the native backend is available, protocol chips should be rendered through Codex's structured user-input surface instead of the terminal fallback. The adapter priority is:

```text
request_user_input -> omx question -> scripts/codex_chips.py -> plain-text record
```

A successful native decision should be checkpointed as:

```json
{
  "backend": "request_user_input",
  "source": "explicit_user"
}
```

## Fallback remains required

The feature is under development in Codex CLI 0.130.0. Keep `scripts/codex_chips.py` available for machines, remote sessions, or future CLI builds where the native tool is disabled or hidden.

## Troubleshooting

Check status:

```bash
codex features list | rg 'default_mode_request_user_input|request_user_input'
```

If the flag is true but chips still do not render:

1. fully exit and restart Codex;
2. verify the session is not an older resumed session started before the flag was enabled;
3. fall back to `scripts/codex_chips.py` and record the backend in the checkpoint;
4. only consider a Codex TUI fork/patch if `request_user_input` is unavailable in a fresh session with the flag enabled.
