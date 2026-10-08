"""Local, provider-neutral trace storage for agent executions."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import uuid
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
TRACE_SCHEMA = "agent-run-trace/v1"
REDACTED = "[REDACTED]"
TERMINAL_STATUSES = frozenset({"succeeded", "failed", "cancelled", "abandoned"})
SECRET_KEY = re.compile(
    r"(?i)(authorization|api[_-]?key|access[_-]?token|auth[_-]?token|token|password|secret|credential)"
)
SECRET_VALUE = re.compile(
    r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+|(?:ghp|github_pat|sk|xox[baprs])_[A-Za-z0-9_-]{8,}"
)


class TraceError(RuntimeError):
    """Raised when a trace operation cannot be completed safely."""


@dataclass(frozen=True)
class Verification:
    """Integrity verification result."""

    valid: bool
    run_id: str
    event_count: int
    terminal_status: str
    first_error: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "run_id": self.run_id,
            "event_count": self.event_count,
            "terminal_status": self.terminal_status,
            "first_error": self.first_error,
        }


def utc_now() -> str:
    """Return an RFC3339 UTC timestamp."""
    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    """Serialize JSON deterministically for hashing and exports."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _redact(value: Any, redacted: list[str], key: str = "") -> Any:
    if SECRET_KEY.search(key):
        redacted.append(key or "sensitive_field")
        return REDACTED
    if isinstance(value, Mapping):
        return {str(k): _redact(v, redacted, str(k)) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact(item, redacted, key) for item in value]
    if isinstance(value, tuple):
        return [_redact(item, redacted, key) for item in value]
    if isinstance(value, str) and SECRET_VALUE.search(value):
        redacted.append(key or "sensitive_value")
        return SECRET_VALUE.sub(
            lambda match: match.group(1) + REDACTED if match.group(1) else REDACTED, value
        )
    return value


def redact(value: Any) -> tuple[Any, list[str]]:
    """Redact sensitive keys and common token forms before persistence."""
    fields: list[str] = []
    return _redact(value, fields), sorted(set(fields))


def default_store_path() -> Path:
    """Return the ignored local store path."""
    configured = os.environ.get("AGENT_TRACE_STORE")
    if configured:
        return Path(configured).expanduser()
    return Path(".agent-state") / "trace.sqlite3"


def repository_revision() -> str | None:
    """Read the current revision without invoking a shell."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() or None


class TraceStore:
    """Transactional SQLite store for local agent execution traces."""

    def __init__(self, path: Path | str | None = None, *, timeout: float = 2.0) -> None:
        self.path = Path(path) if path is not None else default_store_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=self.timeout)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 2000")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS schema_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    parent_run_id TEXT REFERENCES runs(run_id),
                    status TEXT NOT NULL CHECK(status IN ('running', 'succeeded', 'failed', 'cancelled', 'abandoned')),
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    agent_id TEXT,
                    provider TEXT,
                    model TEXT,
                    provenance_json TEXT NOT NULL,
                    redactions_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL REFERENCES runs(run_id),
                    sequence INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    redactions_json TEXT NOT NULL,
                    previous_hash TEXT,
                    integrity_hash TEXT NOT NULL,
                    UNIQUE(run_id, sequence)
                );
                CREATE TABLE IF NOT EXISTS trace_references (
                    reference_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL REFERENCES runs(run_id),
                    kind TEXT NOT NULL,
                    locator TEXT NOT NULL,
                    digest TEXT,
                    created_by_event_id TEXT REFERENCES events(event_id),
                    verification_status TEXT NOT NULL,
                    metadata_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS events_by_run ON events(run_id, sequence);
                CREATE INDEX IF NOT EXISTS references_by_run ON trace_references(run_id);
                INSERT OR IGNORE INTO schema_meta(key, value) VALUES ('schema_version', '1');
                """
            )

    def start_run(
        self,
        *,
        parent_run_id: str | None = None,
        agent_id: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        provenance: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a running trace and its initial event."""
        run_id = str(uuid.uuid4())
        if parent_run_id is not None and not self._exists(parent_run_id):
            raise TraceError(f"parent run not found: {parent_run_id}")
        raw_provenance = dict(provenance or {})
        raw_provenance.setdefault("repository_revision", repository_revision())
        clean_provenance, run_redactions = redact(raw_provenance)
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO runs VALUES (?, ?, 'running', ?, NULL, ?, ?, ?, ?, ?)",
                (
                    run_id,
                    parent_run_id,
                    created_at,
                    agent_id,
                    provider,
                    model,
                    canonical_json(clean_provenance),
                    canonical_json(run_redactions),
                ),
            )
        self.append_event(run_id, "run.started", {"status": "running"})
        return self.inspect(run_id)

    def append_event(
        self, run_id: str, event_type: str, payload: Mapping[str, Any] | None = None
    ) -> dict[str, Any]:
        """Append one redacted event transactionally."""
        event_id = str(uuid.uuid4())
        occurred_at = utc_now()
        clean_payload, redactions = redact(dict(payload or {}))
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            run = connection.execute(
                "SELECT status FROM runs WHERE run_id = ?", (run_id,)
            ).fetchone()
            if run is None:
                raise TraceError(f"run not found: {run_id}")
            if run["status"] in TERMINAL_STATUSES:
                raise TraceError(f"run is terminal: {run_id}")
            previous = connection.execute(
                "SELECT sequence, integrity_hash FROM events WHERE run_id = ? ORDER BY sequence DESC LIMIT 1",
                (run_id,),
            ).fetchone()
            sequence = int(previous["sequence"]) + 1 if previous else 1
            previous_hash = previous["integrity_hash"] if previous else None
            body = {
                "event_id": event_id,
                "run_id": run_id,
                "sequence": sequence,
                "event_type": event_type,
                "occurred_at": occurred_at,
                "payload": clean_payload,
                "previous_hash": previous_hash,
            }
            integrity_hash = hashlib.sha256(canonical_json(body).encode("utf-8")).hexdigest()
            connection.execute(
                "INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    event_id,
                    run_id,
                    sequence,
                    event_type,
                    occurred_at,
                    canonical_json(clean_payload),
                    canonical_json(redactions),
                    previous_hash,
                    integrity_hash,
                ),
            )
        return {**body, "redactions": redactions, "integrity_hash": integrity_hash}

    def finish(self, run_id: str, status: str, *, reason: str | None = None) -> dict[str, Any]:
        """Finish a run exactly once and append its terminal event."""
        if status not in TERMINAL_STATUSES:
            raise TraceError(f"invalid terminal status: {status}")
        current = self._run_status(run_id)
        if current is None:
            raise TraceError(f"run not found: {run_id}")
        if current in TERMINAL_STATUSES:
            raise TraceError(f"run is already terminal: {run_id}")
        event = self.append_event(run_id, "run.finished", {"status": status, "reason": reason})
        completed_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                "UPDATE runs SET status = ?, completed_at = ? WHERE run_id = ?",
                (status, completed_at, run_id),
            )
        return self.inspect(run_id) | {"terminal_event_id": event["event_id"]}

    def add_reference(
        self,
        run_id: str,
        kind: str,
        locator: str,
        *,
        digest: str | None = None,
        created_by_event_id: str | None = None,
        verification_status: str = "unverified",
        metadata: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Attach a non-content reference to a run."""
        if self._run_status(run_id) is None:
            raise TraceError(f"run not found: {run_id}")
        reference = {
            "reference_id": str(uuid.uuid4()),
            "run_id": run_id,
            "kind": kind,
            "locator": locator,
            "digest": digest,
            "created_by_event_id": created_by_event_id,
            "verification_status": verification_status,
            "metadata": redact(dict(metadata or {}))[0],
        }
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO trace_references VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    reference["reference_id"],
                    run_id,
                    kind,
                    locator,
                    digest,
                    created_by_event_id,
                    verification_status,
                    canonical_json(reference["metadata"]),
                ),
            )
        return reference

    def inspect(self, run_id: str) -> dict[str, Any]:
        """Return a run summary, ordered events, references, and integrity status."""
        with self._connect() as connection:
            run = connection.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
            if run is None:
                raise TraceError(f"run not found: {run_id}")
            events = connection.execute(
                "SELECT * FROM events WHERE run_id = ? ORDER BY sequence", (run_id,)
            ).fetchall()
            references = connection.execute(
                "SELECT * FROM trace_references WHERE run_id = ?", (run_id,)
            ).fetchall()
        verification = self.verify(run_id)
        return {
            "schema": TRACE_SCHEMA,
            "run_id": run["run_id"],
            "parent_run_id": run["parent_run_id"],
            "status": run["status"],
            "created_at": run["created_at"],
            "completed_at": run["completed_at"],
            "agent_id": run["agent_id"],
            "provider": run["provider"],
            "model": run["model"],
            "provenance": json.loads(run["provenance_json"]),
            "events": [self._event_dict(row) for row in events],
            "references": [self._reference_dict(row) for row in references],
            "integrity": verification.as_dict(),
        }

    def verify(self, run_id: str) -> Verification:
        """Recompute the event chain and report the first inconsistency."""
        with self._connect() as connection:
            run = connection.execute(
                "SELECT status FROM runs WHERE run_id = ?", (run_id,)
            ).fetchone()
            if run is None:
                raise TraceError(f"run not found: {run_id}")
            rows = connection.execute(
                "SELECT * FROM events WHERE run_id = ? ORDER BY sequence", (run_id,)
            ).fetchall()
        previous_hash: str | None = None
        for expected_sequence, row in enumerate(rows, start=1):
            body = {
                "event_id": row["event_id"],
                "run_id": row["run_id"],
                "sequence": row["sequence"],
                "event_type": row["event_type"],
                "occurred_at": row["occurred_at"],
                "payload": json.loads(row["payload_json"]),
                "previous_hash": row["previous_hash"],
            }
            expected_hash = hashlib.sha256(canonical_json(body).encode("utf-8")).hexdigest()
            if (
                row["sequence"] != expected_sequence
                or row["previous_hash"] != previous_hash
                or row["integrity_hash"] != expected_hash
            ):
                return Verification(
                    False,
                    run_id,
                    len(rows),
                    run["status"],
                    {"sequence": row["sequence"], "expected_sequence": expected_sequence},
                )
            previous_hash = row["integrity_hash"]
        return Verification(True, run_id, len(rows), run["status"])

    def export(self, run_id: str) -> dict[str, Any]:
        """Return a portable redacted representation of a run."""
        result = self.inspect(run_id)
        result["exported_at"] = utc_now()
        result["export_schema"] = TRACE_SCHEMA
        return result

    def recover(self, run_id: str, *, stale_after: timedelta, reason: str) -> dict[str, Any]:
        """Explicitly abandon a stale running trace without deleting evidence."""
        result = self.inspect(run_id)
        if result["status"] != "running":
            raise TraceError(f"run is not recoverable: {run_id}")
        created = datetime.fromisoformat(result["created_at"].replace("Z", "+00:00"))
        if datetime.now(UTC) - created < stale_after:
            raise TraceError(f"run is not stale: {run_id}")
        event = self.append_event(
            run_id,
            "run.recovered",
            {
                "status": "abandoned",
                "reason": reason,
                "stale_after_seconds": stale_after.total_seconds(),
            },
        )
        with self._connect() as connection:
            connection.execute(
                "UPDATE runs SET status = 'abandoned', completed_at = ? WHERE run_id = ?",
                (utc_now(), run_id),
            )
        return self.inspect(run_id) | {"recovery_event_id": event["event_id"]}

    def _exists(self, run_id: str) -> bool:
        return self._run_status(run_id) is not None

    def _run_status(self, run_id: str) -> str | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT status FROM runs WHERE run_id = ?", (run_id,)
            ).fetchone()
        return str(row["status"]) if row else None

    @staticmethod
    def _event_dict(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "event_id": row["event_id"],
            "run_id": row["run_id"],
            "sequence": row["sequence"],
            "event_type": row["event_type"],
            "occurred_at": row["occurred_at"],
            "payload": json.loads(row["payload_json"]),
            "redactions": json.loads(row["redactions_json"]),
            "previous_hash": row["previous_hash"],
            "integrity_hash": row["integrity_hash"],
        }

    @staticmethod
    def _reference_dict(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "reference_id": row["reference_id"],
            "run_id": row["run_id"],
            "kind": row["kind"],
            "locator": row["locator"],
            "digest": row["digest"],
            "created_by_event_id": row["created_by_event_id"],
            "verification_status": row["verification_status"],
            "metadata": json.loads(row["metadata_json"]),
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect local agent execution traces")
    parser.add_argument("--store", type=Path, default=None, help="SQLite store path")
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("start")
    start.add_argument("--parent-run-id")
    start.add_argument("--agent-id")
    start.add_argument("--provider")
    start.add_argument("--model")
    start.add_argument("--change-id")
    start.add_argument("--task-id")
    event = sub.add_parser("event")
    event.add_argument("run_id")
    event.add_argument("event_type")
    event.add_argument("--payload", default="{}")
    finish = sub.add_parser("finish")
    finish.add_argument("run_id")
    finish.add_argument("status", choices=sorted(TERMINAL_STATUSES))
    finish.add_argument("--reason")
    for command in ("inspect", "export", "verify"):
        item = sub.add_parser(command)
        item.add_argument("run_id")
    reference = sub.add_parser("reference")
    reference.add_argument("run_id")
    reference.add_argument("kind")
    reference.add_argument("locator")
    reference.add_argument("--digest")
    reference.add_argument("--verification-status", default="unverified")
    recover = sub.add_parser("recover")
    recover.add_argument("run_id")
    recover.add_argument("--stale-after-seconds", type=float, required=True)
    recover.add_argument("--reason", required=True)
    return parser


def cli(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    store = TraceStore(args.store)
    try:
        if args.command == "start":
            data = store.start_run(
                parent_run_id=args.parent_run_id,
                agent_id=args.agent_id,
                provider=args.provider,
                model=args.model,
                provenance={"openspec_change": args.change_id, "task_id": args.task_id},
            )
        elif args.command == "event":
            data = store.append_event(args.run_id, args.event_type, json.loads(args.payload))
        elif args.command == "finish":
            data = store.finish(args.run_id, args.status, reason=args.reason)
        elif args.command == "inspect":
            data = store.inspect(args.run_id)
        elif args.command == "export":
            data = store.export(args.run_id)
        elif args.command == "verify":
            data = store.verify(args.run_id).as_dict()
        elif args.command == "reference":
            data = store.add_reference(
                args.run_id,
                args.kind,
                args.locator,
                digest=args.digest,
                verification_status=args.verification_status,
            )
        else:
            data = store.recover(
                args.run_id,
                stale_after=timedelta(seconds=args.stale_after_seconds),
                reason=args.reason,
            )
    except (TraceError, json.JSONDecodeError) as error:
        parser.error(str(error))
    print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
