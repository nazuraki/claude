"""Parse a Claude Code session .jsonl into an analyzable timeline.

Session logs are dominated by deferred-tool and skill-listing attachment blobs
on the first several lines (often >100K tokens even for a short session), so
`Read`-ing the raw file wastes context and truncates before the real tool
events. This script strips that noise and prints:

  1. A per-line TIMELINE of tool_use calls (name + compact input summary),
     assistant text/thinking block sizes, and tool_result sizes/status.
  2. SYSTEM/EVENTS — hook summaries, errors, denied tools, parse errors.
  3. USAGE TOTALS — summed message.usage fields, plus the real "fresh" cost
     (output + fresh input + cache creation; cache reads are the cache working).

Notes on the TIMELINE:
  - Claude Code logs each assistant content block as its own JSONL line but
    repeats the same `message.usage` on every one. Usage totals are therefore
    accumulated once per unique `message.id`, and `out_tokens` is attached to a
    single row per message, so summing `out_tokens` across rows equals the true
    total. Do not expect it on every row.
  - Thinking blocks show only `chars` when readable text is present; Claude Code
    logs usually store no replayable thinking text, so those rows are flagged
    `redacted (size not logged)` rather than a misleading `chars: 0`.

Usage:
    python parse_session.py <path-to-session>.jsonl

Run it once per log, including each subagent log under
<session-uuid>/subagents/*.jsonl, and nest subagent timelines under the
parent tool_use that spawned them.
"""
import json
import sys

if len(sys.argv) < 2:
    sys.exit("usage: python parse_session.py <path-to-session>.jsonl")

path = sys.argv[1]
rows = []
usage_tot = {
    "input_tokens": 0,
    "output_tokens": 0,
    "cache_read_input_tokens": 0,
    "cache_creation_input_tokens": 0,
}
seen_msg_ids = set()
events = []

with open(path, "r", encoding="utf-8") as f:
    for lineno, line in enumerate(f, 1):
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except Exception as e:
            events.append((lineno, "PARSE_ERROR", str(e)[:80]))
            continue
        t = o.get("type")
        if t == "assistant":
            msg = o.get("message", {})
            u = msg.get("usage", {}) or {}
            # Each content block is a separate JSONL line repeating the same
            # message.usage, so accumulate usage (and attach out_tokens) only the
            # first time we see a message id. Logs without an id fall back to
            # per-line counting.
            mid = msg.get("id")
            first_of_msg = (mid not in seen_msg_ids) if mid else True
            if first_of_msg:
                for k in usage_tot:
                    usage_tot[k] += u.get(k, 0) or 0
                if mid:
                    seen_msg_ids.add(mid)
            content = msg.get("content", []) or []
            msg_rows = []
            texts = []
            for b in content:
                bt = b.get("type")
                if bt == "tool_use":
                    inp = b.get("input", {})
                    keys = {}
                    for kk, vv in inp.items():
                        s = json.dumps(vv) if not isinstance(vv, str) else vv
                        keys[kk] = (s[:90] + "…") if len(s) > 90 else s
                    msg_rows.append({
                        "line": lineno,
                        "kind": "TOOL_USE",
                        "name": b.get("name"),
                        "input": keys,
                    })
                elif bt == "text":
                    txt = b.get("text", "")
                    if txt.strip():
                        texts.append(len(txt))
                elif bt == "thinking":
                    th = b.get("thinking", "") or ""
                    if th.strip():
                        msg_rows.append({"line": lineno, "kind": "THINKING",
                                         "chars": len(th)})
                    else:
                        # Claude Code logs don't store replayable thinking text,
                        # so size is not recoverable — flag it rather than emit 0.
                        msg_rows.append({"line": lineno, "kind": "THINKING",
                                         "note": "redacted (size not logged)"})
            if texts:
                msg_rows.append({"line": lineno, "kind": "ASSISTANT_TEXT",
                                 "text_chars": sum(texts)})
            # Attach message-level output_tokens once per message (on the first
            # block-line seen for it) so summing out_tokens across rows equals
            # the true total (see USAGE TOTALS).
            if msg_rows and first_of_msg:
                msg_rows[-1]["out_tokens"] = u.get("output_tokens", 0)
            rows.extend(msg_rows)
        elif t == "user":
            tur = o.get("toolUseResult")
            if tur is not None:
                msg = o.get("message", {})
                content = msg.get("content", [])
                size = 0
                status = "ok"
                if isinstance(content, list):
                    for b in content:
                        if isinstance(b, dict) and b.get("type") == "tool_result":
                            c = b.get("content")
                            size += len(json.dumps(c))
                            if b.get("is_error"):
                                status = "ERROR"
                rows.append({"line": lineno, "kind": "TOOL_RESULT",
                             "result_chars": size, "status": status})
        elif t == "system":
            sub = o.get("subtype") or o.get("level") or ""
            cont = o.get("content") or o.get("message") or ""
            if isinstance(cont, dict):
                cont = json.dumps(cont)
            events.append((lineno, "SYSTEM:" + str(sub), str(cont)[:160]))

print("=== TIMELINE ===")
for r in rows:
    print(json.dumps(r, ensure_ascii=False))
print("\n=== SYSTEM/EVENTS ===")
for e in events:
    print(e)
print("\n=== USAGE TOTALS ===")
print(json.dumps(usage_tot, indent=2))
tot = sum(usage_tot.values())
print("SUM_ALL:", tot)
print("FRESH (out+in+cache_create):",
      usage_tot["output_tokens"] + usage_tot["input_tokens"] + usage_tot["cache_creation_input_tokens"])
