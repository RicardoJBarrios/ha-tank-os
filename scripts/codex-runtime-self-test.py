#!/usr/bin/env python3
"""Validate the repository Codex hook adapter and its local fixtures."""

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_platform.codex_runtime import TOOL_OPERATIONS, handle_event, mode
from agent_platform.trace import TraceStore


def main() -> int:
    hook_file = Path(".codex/hooks.json")
    hooks = json.loads(hook_file.read_text(encoding="utf-8"))
    expected = {
        "SessionStart",
        "PreToolUse",
        "PostToolUse",
        "PermissionRequest",
        "SubagentStart",
        "SubagentStop",
        "Stop",
    }
    actual = set(hooks.get("hooks", {}))
    if actual != expected:
        raise SystemExit(
            f"hook coverage mismatch: expected {sorted(expected)}, got {sorted(actual)}"
        )
    for event, entries in hooks["hooks"].items():
        for group in entries:
            for hook in group.get("hooks", [group]):
                if hook.get("type") == "command" and not hook.get("command_windows"):
                    raise SystemExit(f"missing Windows hook command for {event}")
    with TemporaryDirectory(prefix="ha-tank-os-codex-self-test-") as temporary_directory:
        store = TraceStore(Path(temporary_directory) / "trace.sqlite3")
        session = handle_event(
            "SessionStart", {"self_test": True, "session_id": "codex-self-test"}, store=store
        )
        if session["decision"] != "allow" or not session.get("run_id"):
            raise SystemExit("session initialization failed")
        store.finish(session["run_id"], "succeeded", reason="self-test complete")
    if not TOOL_OPERATIONS:
        raise SystemExit("controlled tool registry is empty")
    print(
        json.dumps(
            {
                "status": "valid",
                "hook_events": sorted(actual),
                "controlled_tools": sorted(TOOL_OPERATIONS),
                "mode": mode(),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
