# claude
Collection of Claude Code plugins and skills

## Marketplace

Add this marketplace to Claude Code:

```sh
claude plugin marketplace add nazuraki/claude
```

## Skills

Symlink a skill directory into `~/.claude/skills/<name>` to use it.

| Skill | Description |
|-------|-------------|
| [project-standards](project-standards-skill/) | Audit a project against project standards (docs, .gitignore, Justfile, CI, GitHub settings) and fix gaps |
| [project-docs](project-docs-skill/) | The documents a project should have and how they are organized, for single projects and monorepos |
| [justfile](justfile-skill/) | Write or audit a Justfile against the standard recipe set |
| [work-on](work-on-skill/) | End-to-end GitHub issue workflow: branch, plan, implement, validate, open PR |
| [analyze-session](analyze-session-skill/) | Analyze a session log for inefficient tool usage |

## Plugins

| Plugin | Description |
|--------|-------------|
| [session-logger](session-logger-plugin/) | Logs session activity (prompts, tool calls) to JSONL files in `~/.claude/logs/` |

### Install a plugin

```sh
claude plugin install session-logger@nazuraki-claude-plugins
```
