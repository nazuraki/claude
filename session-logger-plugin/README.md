# session-logger — Claude Code plugin

Logs Claude Code session activity to JSONL files in `~/.claude/logs/`.

Each session gets a timestamped log file with events:
- `session_start` / `session_end` (with stats)
- `prompt` — user message text
- `tool_pre` / `tool_post` — every tool call and its outcome

## Install via plugin system

```sh
/plugin install session-logger
```

## Manual install (symlink, for development)

```sh
git clone <this-repo> ~/src/claude
ln -s ~/src/claude/session-logger-plugin/scripts/session-logger.py ~/.claude/hooks/session-logger.py
```

Add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [{ "hooks": [{ "type": "command", "command": "python3 ~/.claude/hooks/session-logger.py prompt" }] }],
    "PreToolUse":       [{ "hooks": [{ "type": "command", "command": "python3 ~/.claude/hooks/session-logger.py pre"    }] }],
    "PostToolUse":      [{ "hooks": [{ "type": "command", "command": "python3 ~/.claude/hooks/session-logger.py tool"   }] }],
    "Stop":             [{ "hooks": [{ "type": "command", "command": "python3 ~/.claude/hooks/session-logger.py stop"   }] }]
  }
}
```

## Log location

`~/.claude/logs/<timestamp>_<session-short-id>.log`
