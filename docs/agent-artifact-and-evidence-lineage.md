# Agent Artifact and Evidence Lineage

Lineage manifests describe derived reports, test results, decisions, and other agent outputs without copying their contents into the trace. A manifest records its locator, SHA-256 digest when readable, producer run, source references, and explicit verification state.

```python
from agent_platform.lineage import create_manifest, verify_manifest

manifest = create_manifest(
    "report-1",
    "test-report",
    "artifacts/report.json",
    producer_run_id="run-id",
    source_references=("context-pack-id",),
)
verified = verify_manifest(manifest)
```

`verified`, `changed`, and `missing` are distinct states. A digest proves byte integrity only; it does not promote the artifact to canonical requirements, architecture, or product authority.
