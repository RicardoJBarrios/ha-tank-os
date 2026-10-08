"""Tests for the local context resolver."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts/context-resolver.py"
SPEC = importlib.util.spec_from_file_location("context_resolver", SCRIPT)
assert SPEC and SPEC.loader
resolver = importlib.util.module_from_spec(SPEC)
sys.modules["context_resolver"] = resolver
SPEC.loader.exec_module(resolver)


def make_root(tmp_path: Path) -> Path:
    (tmp_path / ".context").mkdir()
    (tmp_path / "docs").mkdir()
    for path in [
        "AGENTS.md",
        "docs/vision-y-requisitos.md",
        "docs/metodologia-modelado-sdd.md",
        "docs/agent-tooling.md",
    ]:
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"# {path}\ncontext observation\n", encoding="utf-8")
    registry = {
        "schema_version": 1,
        "resolver_version": "1.0.0",
        "authority_order": ["canonical", "derived", "historical", "local"],
        "mandatory_paths": [
            "AGENTS.md",
            "docs/vision-y-requisitos.md",
            "docs/metodologia-modelado-sdd.md",
            "docs/agent-tooling.md",
        ],
        "excluded_path_fragments": [".context/generated", "artifacts"],
        "artifacts": [
            {
                "id": "instructions",
                "path": "AGENTS.md",
                "kind": "instructions",
                "authority": "canonical",
                "freshness": "tracked",
            },
            {
                "id": "vision",
                "path": "docs/vision-y-requisitos.md",
                "kind": "requirements",
                "authority": "canonical",
                "freshness": "tracked",
            },
            {
                "id": "methodology",
                "path": "docs/metodologia-modelado-sdd.md",
                "kind": "methodology",
                "authority": "canonical",
                "freshness": "tracked",
            },
            {
                "id": "tooling",
                "path": "docs/agent-tooling.md",
                "kind": "tooling",
                "authority": "canonical",
                "freshness": "tracked",
            },
        ],
        "links": [],
    }
    (tmp_path / ".context/registry.json").write_text(json.dumps(registry), encoding="utf-8")
    change = tmp_path / "openspec/changes/demo"
    change.mkdir(parents=True)
    (change / "proposal.md").write_text("# Demo\n", encoding="utf-8")
    return tmp_path


def test_validate_rejects_missing_registered_path(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    registry = json.loads((root / ".context/registry.json").read_text())
    registry["artifacts"].append(
        {"id": "missing", "path": "docs/missing.md", "kind": "doc", "authority": "canonical"}
    )
    (root / ".context/registry.json").write_text(json.dumps(registry))
    with pytest.raises(resolver.ResolverError, match="do not exist"):
        resolver.validate(root)


def test_validate_rejects_sensitive_registered_path(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    (root / ".env").write_text("TOKEN=secret-value\n", encoding="utf-8")
    registry = json.loads((root / ".context/registry.json").read_text())
    registry["artifacts"].append(
        {"id": "secret", "path": ".env", "kind": "local", "authority": "local"}
    )
    (root / ".context/registry.json").write_text(json.dumps(registry))
    with pytest.raises(resolver.ResolverError, match="excluded"):
        resolver.validate(root)


def test_pack_is_reused_until_a_dependency_changes(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    first = resolver.pack(root, "demo", 20_000)
    second = resolver.pack(root, "demo", 20_000)
    assert first["reused"] is False
    assert second["reused"] is True
    (root / "openspec/changes/demo/proposal.md").write_text("# Demo changed\n", encoding="utf-8")
    third = resolver.pack(root, "demo", 20_000)
    assert third["reused"] is False
    assert "openspec/changes/demo/proposal.md" in third["recalculated"]


def test_search_marks_results_as_discovery_only(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    resolver.index(root)
    result = resolver.search(root, "observation")
    assert result["status"] == "discovery"
    assert result["results"]
    assert all(item["discovery_only"] for item in result["results"])
    assert "relationships" in result["results"][0]


def test_pack_records_budget_exclusions_and_explicit_rebuild(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    registry = json.loads((root / ".context/registry.json").read_text())
    (root / "docs/extra.md").write_text("extra context " * 100, encoding="utf-8")
    registry["artifacts"].append(
        {"id": "extra", "path": "docs/extra.md", "kind": "doc", "authority": "derived"}
    )
    registry["links"].append({"from": "tooling", "to": "extra", "relation": "references"})
    (root / ".context/registry.json").write_text(json.dumps(registry), encoding="utf-8")
    first = resolver.pack(root, "demo", 700)
    assert first["excluded"] > 0
    rebuilt = resolver.pack(root, "demo", 20_000, rebuild=True)
    assert rebuilt["reused"] is False
    assert rebuilt["reason"] == "explicit_rebuild"


def test_optional_candidates_remain_discovery_results() -> None:
    candidates = [
        resolver.RetrievalCandidate("semantic", "old.md", "old", 0.99, "historical", "tracked"),
        resolver.RetrievalCandidate(
            "semantic", "current.md", "current", 0.1, "canonical", "tracked"
        ),
    ]
    ranked = resolver.rank_candidates(candidates, ["canonical", "historical"])
    assert [candidate.path for candidate in ranked] == ["current.md"]
