#!/usr/bin/env python3
"""Installed-plugin entry point using the active workspace as the code root."""

import argparse
import os
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--event", required=True)
args = parser.parse_args()

os.environ.setdefault("CODEX_RUNTIME_MODE", "strict")
workspace = Path(os.environ.get("CODEX_WORKSPACE_ROOT", Path.cwd()))
sys.path.insert(0, str(workspace))

from agent_platform.codex_runtime import hook_cli  # noqa: E402

raise SystemExit(hook_cli(args.event, sys.stdin.read()))
