"""Portable provenance manifests for derived agent artifacts."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .trace import utc_now

LINEAGE_SCHEMA = "agent-lineage/v1"


@dataclass(frozen=True)
class ArtifactManifest:
    artifact_id: str
    artifact_type: str
    locator: str
    producer_run_id: str | None
    source_references: tuple[str, ...]
    digest: str | None
    created_at: str
    status: str
    derived: bool = True

    def as_dict(self) -> dict[str, Any]:
        return {"schema": LINEAGE_SCHEMA, **asdict(self)}


def _digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            hasher.update(chunk)
    return hasher.hexdigest()


def create_manifest(
    artifact_id: str,
    artifact_type: str,
    locator: str,
    *,
    producer_run_id: str | None = None,
    source_references: tuple[str, ...] = (),
) -> ArtifactManifest:
    path = Path(locator)
    digest = _digest(path) if path.is_file() else None
    return ArtifactManifest(
        artifact_id,
        artifact_type,
        locator,
        producer_run_id,
        source_references,
        digest,
        utc_now(),
        "unverified" if digest else "missing",
    )


def verify_manifest(manifest: ArtifactManifest) -> ArtifactManifest:
    path = Path(manifest.locator)
    if not path.is_file() or manifest.digest is None:
        return ArtifactManifest(**{**asdict(manifest), "status": "missing"})
    status = "verified" if _digest(path) == manifest.digest else "changed"
    return ArtifactManifest(**{**asdict(manifest), "status": status})
