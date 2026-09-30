#!/usr/bin/env python3
"""Codex hook entry point."""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_platform.codex_runtime import hook_cli

parser = argparse.ArgumentParser()
parser.add_argument("--event", required=True)
args = parser.parse_args()
os.environ.setdefault("CODEX_RUNTIME_MODE", "strict")
raise SystemExit(hook_cli(args.event, sys.stdin.read()))
