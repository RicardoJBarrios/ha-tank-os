#!/usr/bin/env python3
"""Run non-mutating, redacted readiness checks for the local agent runtime."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_EVENTS = {
    "SessionStart",
    "PreToolUse",
    "PostToolUse",
    "PermissionRequest",
    "SubagentStart",
    "SubagentStop",
    "Stop",
}
DEFAULT_SONAR_HOST_URL = "http://127.0.0.1:9000"


def check_hooks() -> tuple[str, str]:
    native = json.loads((ROOT / ".codex/hooks.json").read_text(encoding="utf-8"))
    events = set(native.get("hooks", {}))
    if events != EXPECTED_EVENTS:
        return "fail", f"native hook coverage is {sorted(events)}"
    for event, entries in native.get("hooks", {}).items():
        for group in entries:
            for hook in group.get("hooks", []):
                if hook.get("type") == "command" and not hook.get("command_windows"):
                    return "fail", f"Windows launcher is missing for {event}"
    config = (ROOT / ".codex/config.toml").read_text(encoding="utf-8")
    if (
        '[plugins."ha-tank-os-codex-runtime@ha-tank-os"]' not in config
        or "enabled = false" not in config
    ):
        return "fail", "plugin hook source is not explicitly disabled"
    marketplace = json.loads(
        (ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8")
    )
    plugin_path = marketplace["plugins"][0]["source"]["path"]
    if plugin_path != ".":
        return "fail", "marketplace does not point to the canonical portable plugin root"
    return "pass", "native hooks are canonical; plugin package is disabled"


def check_mcp() -> tuple[str, str]:
    token = os.environ.get("HA_TEST_TOKEN")
    if not token:
        return "fail", "HA_TEST_TOKEN is missing"
    url = os.environ.get("HA_MCP_URL", "http://127.0.0.1:8123/api/mcp/assist")
    request = urllib.request.Request(
        url,
        data=json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "ha-tank-os-health", "version": "0.0.0"},
                },
            }
        ).encode(),
        headers={
            "Accept": "application/json, text/event-stream",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            payload = json.loads(response.read())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as error:
        return "fail", f"MCP initialize failed: {type(error).__name__}"
    server = payload.get("result", {}).get("serverInfo", {})
    if not server.get("name") or not server.get("version"):
        return "fail", "MCP initialize returned no server information"
    return "pass", f"Home Assistant MCP ready: {server['name']} {server['version']}"


def check_sonar() -> tuple[str, str]:
    configured_url = os.environ.get("SONAR_HOST_URL")
    url = configured_url or DEFAULT_SONAR_HOST_URL
    request = urllib.request.Request(f"{url.rstrip('/')}/api/system/status")
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            payload = json.loads(response.read())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as error:
        if not configured_url:
            return (
                "not_configured",
                "local SonarQube is not running; set SONAR_HOST_URL for a remote server",
            )
        return "unavailable", f"SonarQube check failed: {type(error).__name__}"
    if payload.get("status") != "UP":
        return "unavailable", f"SonarQube status is {payload.get('status', 'unknown')}"
    scope = "local SonarQube" if not configured_url else "SonarQube"
    return "pass", f"{scope} ready: {payload.get('version', 'version unknown')}"


def main() -> int:
    checks = {"hooks": check_hooks(), "home_assistant_mcp": check_mcp(), "sonarqube": check_sonar()}
    for name, (status, message) in checks.items():
        print(f"{name}: {status} - {message}")
    return 0 if all(status in {"pass", "not_configured"} for status, _ in checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
