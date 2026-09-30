"""Tests for product and OpenSpec readiness gates."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_MODULE_SPEC = spec_from_file_location(
    "process_readiness", Path(__file__).parents[1] / "scripts/process-readiness.py"
)
assert _MODULE_SPEC and _MODULE_SPEC.loader
_MODULE = module_from_spec(_MODULE_SPEC)
_MODULE_SPEC.loader.exec_module(_MODULE)
change_readiness = _MODULE.change_readiness
product_baseline = _MODULE.product_baseline


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_missing_baseline_is_explicitly_not_started(tmp_path: Path) -> None:
    result = product_baseline(tmp_path)
    assert result["status"] == "not_started"


def test_baseline_requires_explicit_owner_approval(tmp_path: Path) -> None:
    write(
        tmp_path / "_bmad-output/planning-artifacts/product-baseline.yaml",
        "status: draft\nowner_approval: pending\n",
    )
    result = product_baseline(tmp_path)
    assert result["status"] == "blocked"


def test_change_requires_baseline_and_ready_metadata(tmp_path: Path) -> None:
    planning = tmp_path / "_bmad-output/planning-artifacts"
    write(
        planning / "product-baseline.yaml",
        "status: ready\nowner_approval: approved\n"
        "prd: _bmad-output/planning-artifacts/prds/prd.md\n"
        "capability_map: _bmad-output/planning-artifacts/capability-map.md\n"
        "architecture: _bmad-output/planning-artifacts/architecture.md\n",
    )
    for filename in ("prds/prd.md", "capability-map.md", "architecture.md"):
        write(planning / filename, "approved\n")
    change = tmp_path / "openspec/changes/example"
    write(change / ".openspec.yaml", "status: draft\n")
    write(change / "proposal.md", "# Proposal\n")
    write(change / "design.md", "# Design\n")
    write(change / "tasks.md", "# Tasks\n- [ ] Implement\n")
    write(change / "specs/example/spec.md", "# Spec\n\n## ADDED Requirements\n")

    result = change_readiness("example", tmp_path)
    assert result["status"] == "blocked"
    assert any("status=" in failure for failure in result["failures"])
