#!/usr/bin/env python3
"""CLI entry point for local agent observability."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_platform.observability import cli

if __name__ == "__main__":
    raise SystemExit(cli())
