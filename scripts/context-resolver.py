#!/usr/bin/env python3
"""Build authoritative, incremental context packs for repository agents."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess  # nosec B404 - fixed read-only Git metadata command
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

RESOLVER_VERSION = "1.0.0"
REGISTRY_PATH = Path(".context/registry.json")
DB_PATH = Path(".context/generated/index.sqlite3")
PACK_DIR = Path(".context/generated/packs")
FORBIDDEN_NAMES = {".env", "secrets.yaml", "credentials.json"}
TEXT_SUFFIXES = {".md", ".py", ".js", ".mjs", ".ts", ".tsx", ".json", ".yaml", ".yml", ".toml"}
SENSITIVE_VALUE = re.compile(
    r"(?i)(\b(?:password|token|secret|api[_-]?key)\b\s*[:=]\s*[\"']?)([^\s\"']+)"
)


class ResolverError(RuntimeError):
    """Raised for invalid context input or an incomplete context pack."""


@dataclass(frozen=True)
class Artifact:
    identifier: str
    path: str
    kind: str
    authority: str
    freshness: str
    tags: tuple[str, ...]


@dataclass(frozen=True)
class RetrievalCandidate:
    """Provider-neutral discovery result; never an authority decision."""

    provider: str
    path: str
    excerpt: str
    score: float
    authority: str
    freshness: str
    relationship: str | None = None


def rank_candidates(
    candidates: Iterable[RetrievalCandidate],
    authority_order: Iterable[str],
    include_historical: bool = False,
) -> list[RetrievalCandidate]:
    """Rank optional provider results without allowing them to become authority."""

    ranks = {name: number for number, name in enumerate(authority_order)}
    eligible = [
        candidate
        for candidate in candidates
        if include_historical or candidate.authority not in {"historical", "local"}
    ]
    return sorted(
        eligible,
        key=lambda candidate: (
            ranks.get(candidate.authority, len(ranks)),
            -candidate.score,
            candidate.path,
        ),
    )


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: str | bytes) -> str:
    raw = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(raw).hexdigest()


def sanitize_content(content: str) -> str:
    """Redact obvious inline secret assignments before indexing or packing."""

    return SENSITIVE_VALUE.sub(r"\1<REDACTED>", content)


def load_registry(root: Path) -> dict[str, Any]:
    path = root / REGISTRY_PATH
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ResolverError(f"Cannot read {REGISTRY_PATH}: {error}") from error


def relative_safe(root: Path, value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ResolverError(f"Path must stay inside the repository: {value}")
    resolved = (root / candidate).resolve()
    if resolved != root and root not in resolved.parents:
        raise ResolverError(f"Path escapes the repository: {value}")
    return candidate


def is_excluded(relative_path: str, fragments: Iterable[str]) -> bool:
    normalized = relative_path.replace(os.sep, "/")
    parts = set(Path(normalized).parts)
    if parts & FORBIDDEN_NAMES:
        return True
    for fragment in fragments:
        if fragment in parts:
            return True
        if "/" in fragment and normalized.startswith(fragment.rstrip("/") + "/"):
            return True
    return False


def registry_artifacts(root: Path, registry: dict[str, Any]) -> dict[str, Artifact]:
    authority_order = set(registry.get("authority_order", []))
    artifacts: dict[str, Artifact] = {}
    for raw in registry.get("artifacts", []):
        identifier = raw.get("id")
        path = raw.get("path")
        if not isinstance(identifier, str) or not isinstance(path, str):
            raise ResolverError("Every registry artifact requires string id and path")
        if identifier in artifacts:
            raise ResolverError(f"Duplicate artifact id: {identifier}")
        relative_safe(root, path)
        authority = raw.get("authority")
        if authority not in authority_order:
            raise ResolverError(f"Unknown authority for {identifier}: {authority}")
        artifacts[identifier] = Artifact(
            identifier=identifier,
            path=path,
            kind=str(raw.get("kind", "document")),
            authority=authority,
            freshness=str(raw.get("freshness", "tracked")),
            tags=tuple(str(tag) for tag in raw.get("tags", [])),
        )
    known_ids = set(artifacts)
    for link in registry.get("links", []):
        if link.get("from") not in known_ids or link.get("to") not in known_ids:
            raise ResolverError(f"Link references an unknown artifact: {link}")
        if not isinstance(link.get("relation"), str) or not link["relation"]:
            raise ResolverError(f"Link requires a relation: {link}")
    return artifacts


def reachable_artifact_ids(registry: dict[str, Any], artifacts: dict[str, Artifact]) -> set[str]:
    """Return mandatory artifacts and their explicit outgoing relationships."""

    mandatory_paths = set(registry.get("mandatory_paths", []))
    reachable = {
        artifact.identifier for artifact in artifacts.values() if artifact.path in mandatory_paths
    }
    changed = True
    while changed:
        changed = False
        for link in registry.get("links", []):
            if link["from"] in reachable and link["to"] not in reachable:
                reachable.add(link["to"])
                changed = True
    return reachable


def validate(root: Path) -> dict[str, Any]:
    registry = load_registry(root)
    artifacts = registry_artifacts(root, registry)
    exclusions = registry.get("excluded_path_fragments", [])
    missing: list[str] = []
    forbidden: list[str] = []
    for artifact in artifacts.values():
        path = relative_safe(root, artifact.path)
        if is_excluded(artifact.path, exclusions):
            forbidden.append(artifact.path)
        if not (root / path).is_file():
            missing.append(artifact.path)
    for path in registry.get("mandatory_paths", []):
        relative_safe(root, path)
        if not (root / path).is_file():
            missing.append(path)
    if forbidden:
        raise ResolverError(f"Registered paths are excluded by policy: {', '.join(forbidden)}")
    if missing:
        raise ResolverError(f"Registered paths do not exist: {', '.join(sorted(set(missing)))}")
    return {"status": "valid", "artifact_count": len(artifacts), "registry": str(REGISTRY_PATH)}


def git_revision(root: Path) -> str | None:
    git = shutil.which("git")
    if git is None:
        return None
    try:
        result = subprocess.run(
            [git, "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            shell=False,  # nosec B603 - fixed executable and arguments, no shell
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def source_record(
    root: Path, artifact: Artifact, metadata: dict[str, Any] | None = None
) -> dict[str, Any]:
    path = relative_safe(root, artifact.path)
    content = (root / path).read_bytes()
    return {
        "id": artifact.identifier,
        "path": artifact.path,
        "kind": artifact.kind,
        "authority": artifact.authority,
        "freshness": artifact.freshness,
        "tags": list(artifact.tags),
        "hash": digest(content),
        "metadata_hash": digest(canonical_json(metadata or {})),
        "size": len(content),
    }


def dynamic_change_files(root: Path, change: str) -> list[dict[str, Any]]:
    change_root = relative_safe(root, f"openspec/changes/{change}")
    absolute = root / change_root
    if not absolute.is_dir():
        raise ResolverError(f"Unknown OpenSpec change: {change}")
    records: list[dict[str, Any]] = []
    for file_path in sorted(path for path in absolute.rglob("*") if path.is_file()):
        relative = file_path.relative_to(root).as_posix()
        if is_excluded(relative, [".context/generated", "artifacts"]):
            continue
        content = file_path.read_bytes()
        records.append(
            {
                "id": f"change:{relative}",
                "path": relative,
                "kind": "active-change",
                "authority": "canonical",
                "freshness": "tracked",
                "tags": ["active-change", change],
                "hash": digest(content),
                "metadata_hash": digest(change),
                "size": len(content),
            }
        )
    return records


def all_sources(
    root: Path, registry: dict[str, Any], change: str | None = None
) -> list[dict[str, Any]]:
    artifacts = registry_artifacts(root, registry)
    reachable = reachable_artifact_ids(registry, artifacts)
    sources = [
        source_record(root, artifact, {"tags": artifact.tags})
        for artifact in artifacts.values()
        if artifact.identifier in reachable
    ]
    if change:
        sources.extend(dynamic_change_files(root, change))
    return sorted(sources, key=lambda source: (source["authority"], source["path"], source["id"]))


def open_database(root: Path) -> sqlite3.Connection:
    path = root / DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS artifacts (
            id TEXT PRIMARY KEY, path TEXT NOT NULL, kind TEXT NOT NULL,
            authority TEXT NOT NULL, freshness TEXT NOT NULL, tags TEXT NOT NULL,
            content_hash TEXT NOT NULL, metadata_hash TEXT NOT NULL,
            size INTEGER NOT NULL, content TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS artifacts_path ON artifacts(path);
        """
    )
    try:
        connection.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS artifact_search USING fts5(id, path, content)"
        )
        connection.execute(
            "INSERT OR REPLACE INTO metadata(key, value) VALUES ('search_backend', 'fts5')"
        )
    except sqlite3.OperationalError:
        connection.execute(
            "INSERT OR REPLACE INTO metadata(key, value) VALUES ('search_backend', 'like')"
        )
    connection.commit()
    return connection


def index(root: Path, change: str | None = None, rebuild: bool = False) -> dict[str, Any]:
    validate(root)
    registry = load_registry(root)
    sources = all_sources(root, registry, change)
    registry_hash = digest(canonical_json(registry))
    connection = open_database(root)
    previous_registry = connection.execute(
        "SELECT value FROM metadata WHERE key = 'registry_hash'"
    ).fetchone()
    registry_changed = previous_registry is not None and previous_registry[0] != registry_hash
    if rebuild:
        connection.execute("DELETE FROM artifacts")
        with contextlib.suppress(sqlite3.OperationalError):
            connection.execute("DELETE FROM artifact_search")
    old = {row["id"]: row for row in connection.execute("SELECT * FROM artifacts")}
    reused = 0
    refreshed = 0
    current_ids = set()
    for source in sources:
        current_ids.add(source["id"])
        previous = old.get(source["id"])
        content = sanitize_content(
            (root / source["path"]).read_text(encoding="utf-8", errors="replace")
        )
        if (
            not registry_changed
            and previous
            and previous["content_hash"] == source["hash"]
            and previous["metadata_hash"] == source["metadata_hash"]
        ):
            reused += 1
            continue
        refreshed += 1
        connection.execute(
            """INSERT OR REPLACE INTO artifacts
            (id, path, kind, authority, freshness, tags, content_hash, metadata_hash, size, content)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                source["id"],
                source["path"],
                source["kind"],
                source["authority"],
                source["freshness"],
                canonical_json(source["tags"]),
                source["hash"],
                source["metadata_hash"],
                source["size"],
                content,
            ),
        )
        try:
            connection.execute("DELETE FROM artifact_search WHERE id = ?", (source["id"],))
            connection.execute(
                "INSERT INTO artifact_search(id, path, content) VALUES (?, ?, ?)",
                (source["id"], source["path"], content),
            )
        except sqlite3.OperationalError:
            pass
    stale_ids = set(old) - current_ids
    for stale_id in stale_ids:
        connection.execute("DELETE FROM artifacts WHERE id = ?", (stale_id,))
        with contextlib.suppress(sqlite3.OperationalError):
            connection.execute("DELETE FROM artifact_search WHERE id = ?", (stale_id,))
    connection.execute(
        "INSERT OR REPLACE INTO metadata(key, value) VALUES ('registry_hash', ?)", (registry_hash,)
    )
    connection.execute(
        "INSERT OR REPLACE INTO metadata(key, value) VALUES ('resolver_version', ?)",
        (RESOLVER_VERSION,),
    )
    connection.commit()
    backend = connection.execute(
        "SELECT value FROM metadata WHERE key = 'search_backend'"
    ).fetchone()[0]
    connection.close()
    return {
        "status": "indexed",
        "database": str(DB_PATH),
        "search_backend": backend,
        "sources": len(sources),
        "reused": reused,
        "refreshed": refreshed,
        "removed": len(stale_ids),
        "full_rebuild": rebuild,
        "registry_changed": registry_changed,
    }


def search(
    root: Path, query: str, include_historical: bool = False, limit: int = 10
) -> dict[str, Any]:
    validate(root)
    index(root)
    registry = load_registry(root)
    relationships = {
        artifact_id: [
            {"relation": link["relation"], "target": link["to"]}
            for link in registry.get("links", [])
            if link["from"] == artifact_id
        ]
        for artifact_id in registry_artifacts(root, registry)
    }
    connection = open_database(root)
    backend = connection.execute(
        "SELECT value FROM metadata WHERE key = 'search_backend'"
    ).fetchone()
    rows: list[sqlite3.Row]
    if backend and backend[0] == "fts5":
        safe_query = " ".join(re.findall(r"[\w-]+", query))
        rows = (
            list(
                connection.execute(
                    """SELECT a.* FROM artifact_search
            JOIN artifacts a ON a.id = artifact_search.id
            WHERE artifact_search MATCH ? ORDER BY rank LIMIT ?""",
                    (safe_query, limit * 3),
                )
            )
            if safe_query
            else []
        )
    else:
        pattern = f"%{query}%"
        rows = list(
            connection.execute(
                "SELECT * FROM artifacts WHERE content LIKE ? OR path LIKE ? LIMIT ?",
                (pattern, pattern, limit * 3),
            )
        )
    results = []
    for row in rows:
        if not include_historical and row["authority"] in {"historical", "local"}:
            continue
        content = row["content"]
        position = content.lower().find(query.lower())
        excerpt = (
            content[max(0, position - 100) : position + 240] if position >= 0 else content[:340]
        )
        results.append(
            {
                "id": row["id"],
                "path": row["path"],
                "authority": row["authority"],
                "freshness": row["freshness"],
                "excerpt": excerpt,
                "relationships": relationships.get(row["id"], []),
                "discovery_only": True,
            }
        )
        if len(results) >= limit:
            break
    connection.close()
    return {"status": "discovery", "query": query, "results": results}


def cache_key(
    root: Path, sources: list[dict[str, Any]], change: str, registry: dict[str, Any], budget: int
) -> str:
    payload = {
        "change": change,
        "sources": [
            (source["path"], source["hash"], source["metadata_hash"]) for source in sources
        ],
        "registry_hash": digest(canonical_json(registry)),
        "resolver_version": RESOLVER_VERSION,
        "budget": budget,
        "revision": git_revision(root),
    }
    return digest(canonical_json(payload))


def pack(root: Path, change: str, budget: int, rebuild: bool = False) -> dict[str, Any]:
    validate(root)
    registry = load_registry(root)
    index_result = index(root, change, rebuild)
    sources = all_sources(root, registry, change)
    key = cache_key(root, sources, change, registry, budget)
    pack_dir = root / PACK_DIR
    pack_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = pack_dir / f"{change}.json"
    markdown_path = pack_dir / f"{change}.md"
    previous: dict[str, Any] | None = None
    if manifest_path.is_file():
        try:
            previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            previous = None
    if not rebuild and previous and previous.get("cache_key") == key and markdown_path.is_file():
        return {
            "status": "fresh",
            "reused": True,
            "reason": "cache_key_unchanged",
            "cache_key": key,
            "manifest": str(manifest_path),
            "pack": str(markdown_path),
            "index": index_result,
        }
    previous_inputs = {item["path"]: item for item in (previous or {}).get("inputs", [])}
    changed = [
        source["path"]
        for source in sources
        if previous_inputs.get(source["path"], {}).get("hash") != source["hash"]
    ]
    content_parts: list[str] = []
    included: list[dict[str, Any]] = []
    excluded: list[dict[str, str]] = []
    used = 0
    authority_rank = {name: number for number, name in enumerate(registry["authority_order"])}
    ordered = sorted(
        sources, key=lambda source: (authority_rank[source["authority"]], source["path"])
    )
    mandatory = set(registry["mandatory_paths"])
    for source in ordered:
        content = sanitize_content(
            (root / source["path"]).read_text(encoding="utf-8", errors="replace")
        )
        block = f"\n\n## {source['path']}\n\n{content}\n"
        if source["path"] not in mandatory and used + len(block) > budget:
            excluded.append({"path": source["path"], "reason": "context_budget"})
            continue
        if source["path"] in mandatory and used + len(block) > budget:
            raise ResolverError(f"Mandatory context exceeds budget: {source['path']}")
        content_parts.append(block)
        used += len(block)
        included.append(
            {"path": source["path"], "hash": source["hash"], "authority": source["authority"]}
        )
    status = "fresh"
    reason = (
        "explicit_rebuild" if rebuild else ("changed_inputs" if previous else "initial_generation")
    )
    manifest = {
        "schema_version": 1,
        "resolver_version": RESOLVER_VERSION,
        "generated_at": utc_now(),
        "status": status,
        "cache_key": key,
        "change": change,
        "repository_revision": git_revision(root),
        "inputs": sources,
        "included": included,
        "excluded": excluded,
        "reused": []
        if not previous
        else [
            source["path"]
            for source in sources
            if source["path"] not in changed and source["path"] in previous_inputs
        ],
        "recalculated": changed,
        "refresh_reason": reason,
        "index": index_result,
        "policy": {
            "mandatory_paths": registry["mandatory_paths"],
            "excluded_path_fragments": registry["excluded_path_fragments"],
            "discovery_is_not_authority": True,
        },
    }
    markdown = "# Context Pack\n\n" + "\n".join(content_parts)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    markdown_path.write_text(markdown, encoding="utf-8")
    return {
        "status": status,
        "reused": False,
        "reason": reason,
        "cache_key": key,
        "manifest": str(manifest_path),
        "pack": str(markdown_path),
        "included": len(included),
        "excluded": len(excluded),
        "recalculated": changed,
        "index": index_result,
    }


def command_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate")
    index_parser = subparsers.add_parser("index")
    index_parser.add_argument("--change")
    index_parser.add_argument("--rebuild", action="store_true")
    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("query", nargs="+")
    search_parser.add_argument("--historical", action="store_true")
    search_parser.add_argument("--limit", type=int, default=10)
    pack_parser = subparsers.add_parser("pack")
    pack_parser.add_argument("--change", required=True)
    pack_parser.add_argument("--budget", type=int, default=120_000)
    pack_parser.add_argument("--rebuild", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = command_parser().parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command == "validate":
            result = validate(root)
        elif args.command == "index":
            result = index(root, args.change, args.rebuild)
        elif args.command == "search":
            result = search(root, " ".join(args.query), args.historical, args.limit)
        else:
            result = pack(root, args.change, args.budget, args.rebuild)
    except ResolverError as error:
        print(json.dumps({"status": "invalid", "error": str(error)}), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
