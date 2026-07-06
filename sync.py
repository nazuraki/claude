#!/usr/bin/env python
"""Re-sync locally-installed plugins from this repo after editing them.

The marketplace ``nazuraki-claude-plugins`` is a *directory* source pointing at
this repo, but installed plugins are pinned snapshot copies under
``~/.claude/plugins/cache/`` — edits here don't take effect until re-synced.

`claude plugin update` only applies when the marketplace advertises a NEWER
version, and uninstall/reinstall is unreliable non-interactively. Since the
install is just a snapshot copy at a registered ``installPath``, the dependable
sync is to mirror each plugin's repo folder into that path. Persistent plugin
data (``~/.claude/plugins/data/``) is untouched.

Run after changing any plugin, then restart Claude Code to apply.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

MARKET = "nazuraki-claude-plugins"
ROOT = Path(__file__).resolve().parent
HOME = Path.home()
INSTALLED = HOME / ".claude" / "plugins" / "installed_plugins.json"


def main() -> int:
    manifest = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
    installed = json.loads(INSTALLED.read_text()).get("plugins", {})

    synced = 0
    for plugin in manifest["plugins"]:
        name = plugin["name"]
        src = (ROOT / plugin["source"]).resolve()
        entries = installed.get(f"{name}@{MARKET}")
        if not entries:
            print(f"--  {name}: not installed, skipping")
            continue

        for entry in entries:
            dest = Path(entry["installPath"])
            # Guard: only ever touch paths inside the plugin cache.
            if "plugins" not in dest.parts or "cache" not in dest.parts:
                print(f"!!  {name}: refusing to sync suspicious path {dest}")
                continue
            print(f"==> {name}: {src}  ->  {dest}")
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(src, dest)
            synced += 1

    print(f"\nSynced {synced} plugin path(s). Restart Claude Code to apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
