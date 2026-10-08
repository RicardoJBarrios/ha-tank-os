"""Codex lifecycle adapter for the provider-neutral agent platform."""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .evaluation import EvaluationCase, evaluate
from .governance import CHECKS, evaluate_governance
from .lineage import create_manifest
from .policy import Policy, Rule
from .reliability import FailureClass, ReliabilityPolicy
from .trace import TraceError, TraceStore, redact

DEFAULT_MODE = "audit"
STATE_FILE = Path(".agent-state") / "codex-session.json"
STATE_DIRECTORY = Path(".agent-state") / "sessions"
TOOL_OPERATIONS: dict[str, tuple[str, str]] = {
    "Bash": ("repository.shell", "workspace"),
    "apply_patch": ("repository.write", "workspace"),
    "read_file": ("repository.read", "workspace"),
    "search": ("repository.read", "workspace"),
    "run_tests": ("repository.verify", "workspace"),
    "shell": ("repository.shell", "workspace"),
    "mcp__homeAssistantLocal": ("ha.local", "disposable"),
}


def mode() -> str:
    """Return the configured audit or strict mode."""
    value = os.environ.get("CODEX_RUNTIME_MODE", DEFAULT_MODE).lower()
    return value if value in {"audit", "strict"} else DEFAULT_MODE


def _policy() -> Policy:
    return Policy(
        [
            Rule("repository-read", "repository.read", "workspace", "allow"),
            Rule("repository-verify", "repository.verify", "workspace", "allow"),
            Rule("ha-disposable", "ha.local", "disposable", "allow"),
            Rule("repository-write", "repository.write", "workspace", "require_approval"),
            Rule("repository-shell", "repository.shell", "workspace", "require_approval"),
        ],
        version="codex-runtime-v1",
    )


def _session_identity(payload: Mapping[str, Any]) -> str | None:
    for key in ("session_id", "conversation_id", "thread_id"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _state_path(payload: Mapping[str, Any]) -> Path:
    # STATE_FILE remains injectable for isolated unit tests and migration.
    if Path(".agent-state") / "codex-session.json" != STATE_FILE:
        return STATE_FILE
    identity = _session_identity(payload)
    if not identity:
        return STATE_DIRECTORY / "missing-session.json"
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:24]
    return STATE_DIRECTORY / f"{digest}.json"


def _load_state(path: Path = STATE_FILE) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None


def _save_state(state: Mapping[str, Any], path: Path = STATE_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(state), sort_keys=True), encoding="utf-8")


def _start_session(payload: Mapping[str, Any], store: TraceStore) -> dict[str, Any]:
    run = store.start_run(
        agent_id="codex",
        provider="codex",
        provenance={"hook_event": "SessionStart", "workspace": payload.get("cwd")},
    )
    state = {
        "run_id": run["run_id"],
        "mode": mode(),
        "hook_schema": "codex-runtime/v1",
        "session_id": _session_identity(payload),
    }
    _save_state(state, _state_path(payload))
    return {
        "decision": "allow",
        "runtime_mode": mode(),
        "run_id": state["run_id"],
        "reason": "trace initialized",
    }


def handle_event(
    event: str, payload: Mapping[str, Any], *, store: TraceStore | None = None
) -> dict[str, Any]:
    """Handle a normalized Codex hook event and return a stable adapter result."""
    trace = store or TraceStore()
    if event == "SessionStart":
        return _start_session(payload, trace)
    identity = _session_identity(payload)
    if not identity:
        return {
            "decision": "block" if mode() == "strict" else "allow",
            "runtime_mode": mode(),
            "reason": "session identity is not available",
        }
    state = _load_state(_state_path(payload))
    if not state or not state.get("run_id"):
        return {
            "decision": "block" if mode() == "strict" else "allow",
            "runtime_mode": mode(),
            "reason": "trace is not initialized",
        }
    run_id = str(state["run_id"])
    if event in {"PreToolUse", "PermissionRequest"}:
        tool_name = str(payload.get("tool_name", ""))
        mapping = next(
            (
                (operation, resource)
                for name, (operation, resource) in TOOL_OPERATIONS.items()
                if tool_name == name or tool_name.startswith(f"{name}.")
            ),
            None,
        )
        if mapping is None:
            trace.append_event(
                run_id, "codex.tool.uncontrolled", {"tool_name": tool_name, "mode": mode()}
            )
            return {
                "decision": "block" if mode() == "strict" else "allow",
                "runtime_mode": mode(),
                "reason": "unknown Codex tool",
            }
        result = _policy().evaluate(mapping[0], mapping[1], run_id=run_id, trace=trace)
        if event == "PermissionRequest":
            clean, redactions = redact(dict(payload))
            trace.append_event(
                run_id,
                "codex.permission.request",
                {
                    "policy_decision": result["decision"],
                    "payload": clean,
                    "redactions": redactions,
                },
            )
            if result["decision"] == "deny":
                return {
                    **result,
                    "runtime_mode": mode(),
                    "run_id": run_id,
                }
            return {
                "decision": "allow",
                "policy_decision": result["decision"],
                "runtime_mode": mode(),
                "run_id": run_id,
                "reason": "approval deferred to Codex host",
            }
        if mode() == "audit" and result["decision"] != "allow":
            result["decision"] = "allow"
            result["reason"] = f"audit-only: {result['reason']}"
        elif mode() == "strict" and result["decision"] != "allow":
            if result["decision"] == "require_approval":
                result["reason"] = "approval deferred to Codex host"
            else:
                result["decision"] = "block"
                result["reason"] = f"strict: {result['reason']}"
        return {**result, "runtime_mode": mode(), "run_id": run_id}
    if event in {"PostToolUse", "SubagentStop"}:
        clean, redactions = redact(dict(payload))
        trace.append_event(
            run_id, f"codex.{event.lower()}", {"payload": clean, "redactions": redactions}
        )
        if event == "PostToolUse" and payload.get("success") is False:
            reliability = ReliabilityPolicy().decide(
                FailureClass.TRANSIENT
                if payload.get("transient") is True
                else FailureClass.PERMANENT,
                attempt=int(payload.get("attempt", 1)),
                idempotent=payload.get("idempotent") is True,
            )
            trace.append_event(run_id, "codex.reliability.decision", reliability)
        return {
            "decision": "allow",
            "runtime_mode": mode(),
            "run_id": run_id,
            "reason": "event recorded",
        }
    if event == "SubagentStart":
        child = trace.start_run(
            parent_run_id=run_id,
            agent_id=str(payload.get("agent", "unknown")),
            provider="codex",
            provenance={"hook_event": event, "scope": payload.get("scope")},
        )
        return {
            "decision": "allow",
            "runtime_mode": mode(),
            "run_id": run_id,
            "child_run_id": child["run_id"],
            "reason": "child run recorded",
        }
    if event == "Stop":
        evaluation = evaluate(
            EvaluationCase("codex-completion", "1"),
            status=str(payload.get("status", "failed")),
            summary=str(payload.get("summary", "")),
            duration_seconds=float(payload.get("duration_seconds", 0)),
            run_id=run_id,
        )
        checks = {check.evidence_key: payload.get(check.evidence_key) is True for check in CHECKS}
        governance = evaluate_governance(checks, run_id=run_id)
        verification = trace.verify(run_id).as_dict()
        artifact_path = payload.get("artifact_path")
        lineage = None
        if isinstance(artifact_path, str):
            manifest = create_manifest(
                "codex-completion", "codex-evidence", artifact_path, producer_run_id=run_id
            )
            lineage = manifest.as_dict()
            trace.add_reference(
                run_id,
                "codex-evidence",
                artifact_path,
                digest=manifest.digest,
                verification_status=manifest.status,
            )
        complete = (
            verification["valid"]
            and governance["status"] == "pass"
            and evaluation["status"] == "pass"
        )
        if complete:
            trace.finish(run_id, "succeeded", reason="Codex runtime evidence complete")
        decision = "allow" if complete or mode() == "audit" else "block"
        return {
            "decision": decision,
            "runtime_mode": mode(),
            "run_id": run_id,
            "trace_valid": verification["valid"],
            "governance": governance["status"],
            "evaluation": evaluation["status"],
            "lineage": lineage,
            "reason": (
                "completion evidence valid"
                if complete
                else "audit-only: completion evidence incomplete"
                if mode() == "audit"
                else "completion evidence incomplete"
            ),
        }
    trace.append_event(run_id, "codex.unknown_event", {"event": event})
    return {
        "decision": "allow" if mode() == "audit" else "block",
        "runtime_mode": mode(),
        "run_id": run_id,
        "reason": "unknown hook event",
    }


def hook_cli(event: str, raw: str) -> int:
    """Read a Codex hook payload and write a stable JSON decision."""
    try:
        payload = json.loads(raw or "{}")
        if not isinstance(payload, dict):
            raise ValueError("hook payload must be a JSON object")
        result = handle_event(event, payload)
    except (ValueError, TraceError, OSError) as error:
        result = {
            "decision": "block" if mode() == "strict" else "allow",
            "runtime_mode": mode(),
            "reason": f"runtime error: {error}",
        }
    decision = result.get("decision", "allow")
    if decision == "block" and event in {"PreToolUse", "PermissionRequest"}:
        output = {
            "hookSpecificOutput": {
                "hookEventName": event,
                "permissionDecision": "deny",
                "permissionDecisionReason": result.get("reason", "Blocked by policy"),
            }
        }
    elif decision == "block" and event == "Stop":
        output = {
            "continue": False,
            "stopReason": result.get("reason", "Completion evidence is incomplete"),
        }
    elif decision == "block" and event in {"SubagentStop", "PostToolUse"}:
        output = {"decision": "block", "reason": result.get("reason", "Blocked by policy")}
    elif event in {
        "SessionStart",
        "SubagentStart",
        "PreToolUse",
        "PermissionRequest",
        "PostToolUse",
        "Stop",
    }:
        output = {}
    else:
        output = {"decision": decision, "reason": result.get("reason", "")}
    print(json.dumps(output, sort_keys=True))
    return 0
