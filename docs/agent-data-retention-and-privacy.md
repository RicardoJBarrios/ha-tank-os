# Agent Data Retention and Privacy

Retention currently targets only local `operational_trace` data. Canonical documentation, Git history, product persistence, and Home Assistant Recorder are never eligible targets.

The API is dry-run by default:

```python
from agent_platform.retention import RetentionPolicy, purge_trace

preview = purge_trace(store, RetentionPolicy("2027-01-01T00:00:00Z"))
confirmed = purge_trace(store, RetentionPolicy("2027-01-01T00:00:00Z"), confirm=True)
```

No automatic retention schedule is enabled until the product owner chooses a retention window. Export evidence before confirmed deletion. Purge is transactional and idempotent; reports contain counts and policy metadata, not payloads or secrets.
