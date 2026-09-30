#!/usr/bin/env python3
"""CLI entry point for the local agent trace store."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_platform.trace import cli

if __name__ == "__main__":
    raise SystemExit(cli())
