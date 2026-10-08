#!/usr/bin/env python3
"""Portable Codex hook launcher resolved from the session working directory."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def repository_root() -> Path:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=Path.cwd(),
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"Unable to resolve repository root: {error}") from error
    return Path(result.stdout.strip()).resolve()


parser = argparse.ArgumentParser()
parser.add_argument("--event", required=True)
args = parser.parse_args()
root = repository_root()
os.environ.setdefault("CODEX_RUNTIME_MODE", "strict")
sys.path.insert(0, str(root))

from agent_platform.codex_runtime import hook_cli  # noqa: E402

raise SystemExit(hook_cli(args.event, sys.stdin.read()))
