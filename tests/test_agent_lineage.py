"""Tests for artifact provenance and integrity."""

from pathlib import Path

from agent_platform.lineage import create_manifest, verify_manifest


def test_manifest_tracks_sources_and_verifies_content(tmp_path: Path) -> None:
    artifact = tmp_path / "report.json"
    artifact.write_text('{"ok":true}\n')
    manifest = create_manifest(
        "report-1",
        "test-report",
        str(artifact),
        producer_run_id="run-1",
        source_references=("context-pack-1",),
    )
    verified = verify_manifest(manifest)
    assert verified.status == "verified"
    assert verified.derived is True
    assert verified.source_references == ("context-pack-1",)


def test_manifest_detects_change_and_missing_locator(tmp_path: Path) -> None:
    artifact = tmp_path / "report.txt"
    artifact.write_text("one")
    manifest = create_manifest("report-1", "report", str(artifact))
    artifact.write_text("two")
    assert verify_manifest(manifest).status == "changed"
    artifact.unlink()
    assert verify_manifest(manifest).status == "missing"
