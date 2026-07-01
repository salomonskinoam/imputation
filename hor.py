"""Repo CLI entry: register this repo's tasks, then run the generic SDK CLI.

Usage: python hor.py <materialize|validate|push|create> <task-name> [opts]

Puts the repo root on sys.path and imports tasks_def so every task instance self-registers, then
delegates to sdk.cli.main. The bootstrap-then-import order is the sanctioned exception to
"imports at the top" (an entrypoint must set the path first).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import tasks_def  # noqa: E402,F401  importing registers every task instance
from sdk.cli.main import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
