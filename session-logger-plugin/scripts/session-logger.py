#!/usr/bin/env python3
"""
Claude Code session logger hook.

Called by Claude Code hooks:
  session-logger.py prompt — UserPromptSubmit
  session-logger.py pre    — PreToolUse
  session-logger.py tool   — PostToolUse
  session-logger.py stop   — Stop
"""
import json
import os
import pathlib
import sys
from datetime import datetime

# fcntl is POSIX-only (macOS, Linux). On Windows it raises ImportError,
# which crashes the hook before any logging occurs. The shim below
# provides no-op locking on platforms that don't support fcntl so the
# logger degrades gracefully. The only risk is a rare race condition on
# the session map when multiple Claude Code sessions start simultaneously.
try:
    import fcntl

    def _lock_ex(f):
        fcntl.flock(f, fcntl.LOCK_EX)

    def _unlock(f):
        fcntl.flock(f, fcntl.LOCK_UN)

except ImportError:
    def _lock_ex(f):
        pass

    def _unlock(f):
        pass


LOG_DIR = pathlib.Path.home() / ".claude" / "logs"
SESSION_MAP = LOG_DIR / ".session_map.json"
SESSION_MAP_LOCK = LOG_DIR / ".session_map.lock"
MAX_AGE_DAYS = 30


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# Session map — exclusive-locked read/modify/write
# ---------------------------------------------------------------------------

def _update_session_map(fn):
    """Call fn(map) -> map under an exclusive lock, then persist."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(SESSION_MAP_LOCK, "w") as lf:
        _lock_ex(lf)
        try:
            m = {}
            if SESSION_MAP.exists():
                try:
                    m = json.loads(SESSION_MAP.read_text())
                except Exception:
                    pass
            m = fn(m)
            SESSION_MAP.write_text(json.dumps(m, indent=2))
        finally:
            _unlock(lf)


def _prune(m: dict) -> dict:
    """Remove entries that are malformed, missing, or older than MAX_AGE_DAYS."""
    cutoff = datetime.now().timestamp() - MAX_AGE_DAYS * 86400
    out = {}
    for sid, info in m.items():
        if not isinstance(info, dict) or "path" not in info:
            continue  # drop malformed entries (e.g. from old string-value format)
        p = pathlib.Path(info["path"])
        if p.exists() and p.stat().st_mtime > cutoff:
            out[sid] = info
    return out


def get_or_create_log(session_id: str) -> pathlib.Path:
    """
    Return the log file path for session_id.
    On first encounter, register it in the map and write a session_start record.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    result: dict = {}
    is_new: list = []  # mutable flag for closure

    def update(m: dict) -> dict:
        m = _prune(m)
        if session_id not in m:
            ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            short = session_id[:8] if len(session_id) >= 8 else session_id
            path = str(LOG_DIR / f"{ts}_{short}.log")
            m[session_id] = {"path": path}
            is_new.append(True)
        result.update(m[session_id])
        return m

    _update_session_map(update)
    log = pathlib.Path(result["path"])

    if is_new:
        _append(log, {
            "event": "session_start",
            "session_id": session_id,
            "cwd": os.getcwd(),
        })

    return log


def get_existing_log(session_id: str) -> "pathlib.Path | None":
    """Return log path for session_id if it already exists in the map."""
    if not SESSION_MAP.exists():
        return None
    try:
        m = json.loads(SESSION_MAP.read_text())
    except Exception:
        return None
    entry = m.get(session_id)
    if not entry:
        return None
    return pathlib.Path(entry["path"])


# ---------------------------------------------------------------------------
# JSONL append — locked per file
# ---------------------------------------------------------------------------

def _append(log: pathlib.Path, record: dict) -> None:
    record.setdefault("ts", now_iso())
    line = json.dumps(record) + "\n"
    with open(log, "a") as f:
        _lock_ex(f)
        try:
            f.write(line)
        finally:
            _unlock(f)


# ---------------------------------------------------------------------------
# Tool name helpers
# ---------------------------------------------------------------------------

def display_tool(tool_name: str) -> str:
    """Human-readable tool name. Strips mcp__ prefix."""
    if tool_name.startswith("mcp__"):
        # mcp__server__method  ->  server.method
        parts = tool_name.split("__", 2)
        return f"{parts[1]}.{parts[2]}" if len(parts) == 3 else tool_name[5:]
    return tool_name


def tool_detail(tool_name: str, inp: dict) -> str:
    """Brief detail for what the tool was asked to do."""
    if tool_name.startswith("mcp__"):
        return ""  # display_tool already captures server.method
    if tool_name == "Skill":
        return inp.get("skill", "?")
    if tool_name == "Agent":
        return inp.get("description", "")[:80]
    if tool_name in ("Read", "Write", "Edit"):
        return inp.get("file_path", "")
    if tool_name == "Bash":
        return inp.get("command", "").replace("\n", " ").strip()[:80]
    if tool_name in ("Glob", "Grep"):
        return inp.get("pattern", inp.get("query", ""))
    return ""


# ---------------------------------------------------------------------------
# Error detection
# ---------------------------------------------------------------------------

def is_error(tool_response) -> bool:
    if not isinstance(tool_response, dict):
        return False
    if tool_response.get("is_error") is True:
        return True
    err = tool_response.get("error")
    if err is not None and err is not False and err != "":
        return True
    return False


# ---------------------------------------------------------------------------
# Event handlers
# ---------------------------------------------------------------------------

def handle_prompt(data: dict) -> None:
    session_id = data.get("session_id", "unknown")
    prompt = data.get("prompt", "").strip()
    log = get_or_create_log(session_id)
    _append(log, {
        "event": "prompt",
        "session_id": session_id,
        "text": prompt,
    })


def handle_pre(data: dict) -> None:
    session_id = data.get("session_id", "unknown")
    tool_name = data.get("tool_name", "unknown")
    inp = data.get("tool_input", {})
    log = get_or_create_log(session_id)
    _append(log, {
        "event": "tool_pre",
        "session_id": session_id,
        "tool": display_tool(tool_name),
        "detail": tool_detail(tool_name, inp),
    })


def handle_tool(data: dict) -> None:
    session_id = data.get("session_id", "unknown")
    tool_name = data.get("tool_name", "unknown")
    inp = data.get("tool_input", {})
    resp = data.get("tool_response", {})
    log = get_or_create_log(session_id)
    _append(log, {
        "event": "tool_post",
        "session_id": session_id,
        "tool": display_tool(tool_name),
        "detail": tool_detail(tool_name, inp),
        "status": "error" if is_error(resp) else "ok",
    })


def handle_stop(data: dict) -> None:
    session_id = data.get("session_id", "unknown")
    log = get_existing_log(session_id) or get_or_create_log(session_id)

    pre_count = post_count = errors = prompts = 0
    if log.exists():
        for raw in log.read_text().splitlines():
            try:
                r = json.loads(raw)
            except Exception:
                continue
            ev = r.get("event", "")
            if ev == "tool_pre":
                pre_count += 1
            elif ev == "tool_post":
                post_count += 1
                if r.get("status") == "error":
                    errors += 1
            elif ev == "prompt":
                prompts += 1

    _append(log, {
        "event": "session_end",
        "session_id": session_id,
        "stats": {
            "prompts": prompts,
            "tools_completed": post_count,
            "tools_errored": errors,
            "tools_denied": max(0, pre_count - post_count),
        },
    })


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    event = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # never block Claude on a parse failure

    if event == "prompt":
        handle_prompt(data)
    elif event == "pre":
        handle_pre(data)
    elif event == "tool":
        handle_tool(data)
    elif event == "stop":
        handle_stop(data)


if __name__ == "__main__":
    main()
