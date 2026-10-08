"""Tests for the Codex runtime adapter."""

import json
from pathlib import Path

from agent_platform.codex_runtime import handle_event
from agent_platform.trace import TraceStore


def test_audit_session_and_known_tool_are_traced(tmp_path: Path, monkeypatch: object) -> None:
    state = tmp_path / "session.json"
    monkeypatch.setenv("CODEX_RUNTIME_MODE", "audit")
    store = TraceStore(tmp_path / "trace.sqlite3")
    result = handle_event(
        "SessionStart", {"cwd": str(tmp_path), "session_id": "audit-session"}, store=store
    )
    assert result["decision"] == "allow"
    monkeypatch.setattr("agent_platform.codex_runtime.STATE_FILE", state)
    state.write_text(json.dumps({"run_id": result["run_id"], "mode": "audit"}))
    tool = handle_event(
        "PreToolUse", {"tool_name": "read_file", "session_id": "audit-session"}, store=store
    )
    assert tool["decision"] == "allow"


def test_strict_mode_blocks_unknown_tool(tmp_path: Path, monkeypatch: object) -> None:
    state = tmp_path / "session.json"
    monkeypatch.setenv("CODEX_RUNTIME_MODE", "strict")
    monkeypatch.setattr("agent_platform.codex_runtime.STATE_FILE", state)
    store = TraceStore(tmp_path / "trace.sqlite3")
    session = handle_event("SessionStart", {"session_id": "strict-session"}, store=store)
    state.write_text(json.dumps({"run_id": session["run_id"], "mode": "strict"}))
    result = handle_event(
        "PreToolUse", {"tool_name": "unknown_tool", "session_id": "strict-session"}, store=store
    )
    assert result["decision"] == "block"


def test_runtime_records_child_and_blocks_incomplete_stop(
    tmp_path: Path, monkeypatch: object
) -> None:
    state = tmp_path / "session.json"
    monkeypatch.setenv("CODEX_RUNTIME_MODE", "strict")
    monkeypatch.setattr("agent_platform.codex_runtime.STATE_FILE", state)
    store = TraceStore(tmp_path / "trace.sqlite3")
    session = handle_event("SessionStart", {"session_id": "parent-session"}, store=store)
    state.write_text(json.dumps({"run_id": session["run_id"], "mode": "strict"}))
    child = handle_event(
        "SubagentStart",
        {
            "agent": "python-specialist",
            "scope": "tests",
            "session_id": "parent-session",
        },
        store=store,
    )
    assert child["child_run_id"]
    stop = handle_event("Stop", {"session_id": "parent-session"}, store=store)
    assert stop["decision"] == "block"


def test_strict_mode_defers_approval_required_tools_to_codex_host(
    tmp_path: Path, monkeypatch: object
) -> None:
    state = tmp_path / "session.json"
    monkeypatch.setenv("CODEX_RUNTIME_MODE", "strict")
    monkeypatch.setattr("agent_platform.codex_runtime.STATE_FILE", state)
    store = TraceStore(tmp_path / "trace.sqlite3")
    session = handle_event("SessionStart", {"session_id": "approval-session"}, store=store)
    state.write_text(json.dumps({"run_id": session["run_id"], "mode": "strict"}))
    result = handle_event(
        "PreToolUse",
        {"tool_name": "Bash", "session_id": "approval-session"},
        store=store,
    )
    assert result["decision"] == "require_approval"
    request = handle_event(
        "PermissionRequest",
        {"tool_name": "Bash", "session_id": "approval-session", "secret": "redact-me"},
        store=store,
    )
    assert request["decision"] == "allow"
    assert request["policy_decision"] == "require_approval"


def test_sessions_do_not_share_state(tmp_path: Path, monkeypatch: object) -> None:
    monkeypatch.setenv("CODEX_RUNTIME_MODE", "audit")
    store = TraceStore(tmp_path / "trace.sqlite3")
    first = handle_event("SessionStart", {"session_id": "first"}, store=store)
    second = handle_event("SessionStart", {"session_id": "second"}, store=store)
    assert first["run_id"] != second["run_id"]
    first_tool = handle_event(
        "PreToolUse", {"session_id": "first", "tool_name": "read_file"}, store=store
    )
    second_tool = handle_event(
        "PreToolUse", {"session_id": "second", "tool_name": "read_file"}, store=store
    )
    assert first_tool["run_id"] == first["run_id"]
    assert second_tool["run_id"] == second["run_id"]
