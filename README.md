# claude
Collection of Claude Code plugins and skills

## Marketplace

Add this marketplace to Claude Code:

```sh
claude plugin marketplace add nazuraki/claude
```

## Plugins

| Plugin | Description |
|--------|-------------|
| [session-logger](session-logger-plugin/) | Logs session activity (prompts, tool calls) to JSONL files in `~/.claude/logs/` |

### Install a plugin

```sh
claude plugin install session-logger@nazuraki-claude-plugins
```

## Local development

When this repo is added as a **directory** marketplace, installed plugins are
pinned snapshot copies under `~/.claude/plugins/cache/` — editing a plugin here
does **not** update the installed copy. `claude plugin update` only applies when
a newer version is advertised, so for a same-version directory source it's a
no-op.

After editing a plugin, re-sync the installed copies with:

```sh
python sync.py
```

It mirrors each plugin's folder into its registered cache path (auto-discovered
from `.claude-plugin/marketplace.json` and `installed_plugins.json`), leaving
persistent plugin data untouched. Restart Claude Code afterward to apply.
