#!/usr/bin/env python3
"""Enforce the repository's product and bounded-change readiness gates."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "_bmad-output" / "planning-artifacts" / "product-baseline.yaml"
REQUIRED_CHANGE_FILES = ("proposal.md", "design.md", "tasks.md")
PLACEHOLDER = re.compile(r"\b(?:TODO|TBD)\b|<[^>]+>")


def _yaml_scalars(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^([A-Za-z_][\w-]*):\s*(.*?)\s*$", line)
        if match:
            values[match.group(1)] = match.group(2).strip("\"'")
    return values


def _result(status: str, message: str, **details: Any) -> dict[str, Any]:
    return {"status": status, "message": message, **details}


def product_baseline(root: Path = ROOT) -> dict[str, Any]:
    manifest = root / "_bmad-output" / "planning-artifacts" / "product-baseline.yaml"
    if not manifest.exists():
        return _result("not_started", "no product baseline manifest exists")
    values = _yaml_scalars(manifest)
    required = {"status": "ready", "owner_approval": "approved"}
    failures = [
        f"{key}={values.get(key)!r}, expected {expected!r}"
        for key, expected in required.items()
        if values.get(key) != expected
    ]
    for key in ("prd", "capability_map", "architecture"):
        target = values.get(key)
        if not target or not (root / target).is_file():
            failures.append(f"missing linked artifact: {key}")
    if failures:
        return _result("blocked", "product baseline is not ready", failures=failures)
    return _result("ready", "product baseline is ready")


def change_readiness(change_id: str, root: Path = ROOT) -> dict[str, Any]:
    baseline = product_baseline(root)
    if baseline["status"] != "ready":
        return _result("blocked", "product baseline must be ready first", baseline=baseline)
    change = root / "openspec" / "changes" / change_id
    if not change.is_dir():
        return _result("blocked", "OpenSpec change does not exist", change=change_id)
    metadata = _yaml_scalars(change / ".openspec.yaml")
    failures: list[str] = []
    for key, expected in (
        ("status", "ready"),
        ("owner_approval", "approved"),
        ("product_baseline", "ready"),
    ):
        if metadata.get(key) != expected:
            failures.append(f"{key}={metadata.get(key)!r}, expected {expected!r}")
    for filename in REQUIRED_CHANGE_FILES:
        path = change / filename
        if not path.is_file() or not path.read_text(encoding="utf-8").strip():
            failures.append(f"missing or empty artifact: {filename}")
    specs = list((change / "specs").glob("*/spec.md")) if (change / "specs").is_dir() else []
    if not specs:
        failures.append("no specification delta exists")
    for path in [change / filename for filename in REQUIRED_CHANGE_FILES] + specs:
        if PLACEHOLDER.search(path.read_text(encoding="utf-8")):
            failures.append(f"unresolved placeholder in {path.relative_to(change)}")
    if failures:
        return _result(
            "blocked", "OpenSpec change is not ready", change=change_id, failures=failures
        )
    return _result("ready", "OpenSpec change is ready", change=change_id)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--change", help="Require readiness for this OpenSpec change")
    args = parser.parse_args()
    result = change_readiness(args.change) if args.change else product_baseline()
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.change:
        return 0 if result["status"] == "ready" else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
