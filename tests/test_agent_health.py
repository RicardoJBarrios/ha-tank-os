"""Tests for non-mutating agent health checks."""

import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_MODULE_SPEC = spec_from_file_location(
    "agent_health", Path(__file__).parents[1] / "scripts/agent-health.py"
)
assert _MODULE_SPEC and _MODULE_SPEC.loader
_MODULE = module_from_spec(_MODULE_SPEC)
_MODULE_SPEC.loader.exec_module(_MODULE)


class FakeResponse:
    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps({"status": "UP", "version": "test"}).encode()


def test_detects_local_sonarqube_without_environment_override(monkeypatch: object) -> None:
    monkeypatch.delenv("SONAR_HOST_URL", raising=False)
    monkeypatch.setattr(_MODULE.urllib.request, "urlopen", lambda request, timeout: FakeResponse())

    status, message = _MODULE.check_sonar()

    assert status == "pass"
    assert message == "local SonarQube ready: test"
