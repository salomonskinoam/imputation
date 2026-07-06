"""Build-time checks. Run inside Docker before any heavy steps (data download, etc.).

Add new checks as zero-argument callables to CHECKS. Each must raise on failure.
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path("/root/src")


def check_prompt_injected() -> None:
    yaml = SRC / "task.yaml"
    content = yaml.read_text()
    assert "<PLACEHOLDER>" not in content, (
        f"{yaml} still contains <PLACEHOLDER> — inject the prompt before pushing:\n"
        "  python3 -m src.pre_push.prompt_builder"
    )
    print("[check_build] prompt injected: OK")


CHECKS = [
    check_prompt_injected,
]


def main() -> None:
    failures = []
    for check in CHECKS:
        try:
            check()
        except Exception as e:
            print(f"[check_build] FAILED {check.__name__}: {e}")
            failures.append(check.__name__)
    if failures:
        print(f"[check_build] {len(failures)} check(s) failed — aborting build.")
        sys.exit(1)
    print("[check_build] all checks passed.")


if __name__ == "__main__":
    main()
