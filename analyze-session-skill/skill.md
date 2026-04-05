---
name: analyze-session
description: "Analyze a Claude Code chat session log for inefficient or incorrect tool usage and recommend skill/plugin/config updates. Examples: \"Analyze this session\", \"What was inefficient in my last chat?\", \"Review tool usage patterns\""
---

# Session Tool-Use Analyzer

Analyze a Claude Code session log to identify inefficient, redundant, or misrouted tool usage and recommend actionable config/skill/plugin improvements.

## Invocation

The user may provide:
- A session UUID or log file path
- "last session" or "current session" (resolve from `~/.claude/projects/`)
- No argument (default to most recent completed session)

## Step 1 — Locate the log

Session logs live at:
```
~/.claude/projects/<encoded-project-path>/<session-uuid>.jsonl
```

If the user said "last session", find the most recent `.jsonl` by modification time in the project directory matching the current working directory. Exclude the current session ID if still active.

Also check for subagent logs in `<session-uuid>/subagents/*.jsonl`.

## Step 2 — Parse and extract tool events

Read the JSONL file. For each line, extract:
- **assistant messages** (`type: "assistant"`): look at `message.content[]` for blocks where `type == "tool_use"` — capture `name`, `input`, and the `message.usage` token counts
- **user messages** (`type: "user"`): when `toolUseResult` is present, capture the tool result status and content length
- **system messages** (`type: "system"`): capture hook summaries, errors, denied tools

Build a timeline of: `[turn_number, tool_name, input_summary, output_size, tokens_used, status]`

Process subagent logs the same way and nest them under their parent tool call.

## Step 3 — Analyze for inefficiencies

Check each pattern below. For every finding, record the turn number(s), what happened, and what should have happened.

### Routing violations
- **Read for analysis**: Read tool used on a file that was never subsequently edited → should have used `ctx_execute_file` (context-mode) or `get_file_outline`/`get_symbol_source` (jCodeMunch)
- **Grep flood**: Grep returning >50 lines of content output → should have used `ctx_execute` with shell grep, or `search_symbols` (jCodeMunch), or GitNexus query
- **Bash for search**: Bash running `grep`, `rg`, `find`, `cat`, `head`, `tail` → should have used dedicated tools
- **WebFetch used**: Should have been `ctx_fetch_and_index`
- **Raw curl/wget in Bash**: Should have been `ctx_fetch_and_index` or `ctx_execute`
- **Read on large file without offset/limit**: Files >500 lines read in full when only a portion was needed

### Redundant work
- **Same file read multiple times**: without edits in between
- **Repeated similar Grep/Glob**: patterns that overlap or could be combined
- **Agent spawned for simple lookup**: single Grep/Glob would have sufficed
- **Sequential tool calls that could batch**: multiple `ctx_execute` or `ctx_search` calls that could have been one `ctx_batch_execute`

### Missed opportunities
- **Impact analysis not done before edit**: Edit on a function/class without prior `get_blast_radius` (GitNexus or jCodeMunch) when the change touched shared code
- **No outline before deep-dive**: Jumped straight to reading full files without `get_file_outline` or `get_repo_outline`
- **Token-heavy context assembly**: Multiple Read calls to build context that `get_ranked_context` (jCodeMunch) could have done in one call with a token budget
- **Dead code left untouched**: Deleted or refactored code without checking for dead references via `find_dead_code`

### Token waste
- **Large tool outputs**: any single tool result >10KB entering context
- **Thinking tokens disproportionate**: thinking tokens >3x output tokens on simple tasks
- **Cache miss patterns**: low `cache_read_input_tokens` relative to `cache_creation_input_tokens` across turns

### Hook/enforcement failures
- **Denied tool calls**: tools the user rejected — why, and should the permission config change?
- **Hook errors**: any hook failures in system messages

## Step 4 — Generate report

Write the report to a file: `session-analysis-<short-uuid>.md` in the current working directory.

Structure:

```markdown
# Session Analysis: <session-id>

**Date**: <timestamp>
**Turns**: <count> | **Tool calls**: <count> | **Total tokens**: <sum>

## Summary
<2-3 sentence overview of the session's efficiency>

## Findings

### Critical (config changes needed)
<findings that would save significant tokens or prevent errors — each with turn reference, what happened, what should happen, and specific config/skill change>

### Moderate (workflow improvements)
<findings that would improve efficiency>

### Minor (nice-to-have)
<small optimizations>

## Recommended Changes

### CLAUDE.md updates
<specific additions/edits to routing rules>

### Skill updates
<new skills or skill modifications>

### Plugin/hook updates
<hook changes, permission changes>

### Settings changes
<settings.json modifications>

## Token Budget
| Category | Tokens | % of Total |
|----------|--------|------------|
| Tool I/O | | |
| Thinking | | |
| Cache creation | | |
| Cache reads | | |
| Output | | |
```

## Step 5 — Present to user

After writing the file, present:
1. The file path
2. The Summary section inline
3. Count of findings per severity
4. The top 3 most impactful recommended changes

Do NOT present the full report inline — it's in the file.
