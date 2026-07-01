"""Pre-agent setup. Runs as root via setup.sh (`python -m worlds.imputation.prehook`, under
model_venv for numpy) before the agent starts.

setup_data vendored the full CLEAN dataset to /data_root. This hook asserts that, then projects the
corrupted student view into /data_agent via Amputator (the single source of truth, shared with
world.stage_inputs), writes the student-facing meta, sets permissions, and runs a leak-guard so test
labels / un-amputated truth never reach the student.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from sdk.path_mappings import CONTAINER_DATA_AGENT, CONTAINER_DATA_ROOT, CONTAINER_WORKDIR
from sdk.hor_logger import log
from worlds.imputation.active import active_config
from worlds.imputation.amputate import Amputator

_CFG = active_config()
DATA_REL = _CFG.data_rel
ROOT_DIR = Path(CONTAINER_DATA_ROOT) / DATA_REL
AGENT_DIR = Path(CONTAINER_DATA_AGENT) / DATA_REL
SOLUTION = Path(CONTAINER_WORKDIR) / "solution"


def assert_world_state() -> None:
    for f in ("train_features.npy", "train_labels.npy", "test_features.npy", "test_labels.npy", "meta.json"):
        assert (ROOT_DIR / f).exists(), f"missing {ROOT_DIR / f}"
    log("prehook", "world-state OK (full clean vendor in /data_root)")


def project_student_view() -> None:
    # Deferred (code-only, test hidden): full corrupted train, test hidden (peek_test rows) during
    # rollout; stage_inputs reveals the full test at grade. Static: full both.
    if _CFG.train_at_grade:
        pk_train = getattr(_CFG, "peek_train", None)
        pk_test = getattr(_CFG, "peek_test", 0)
    else:
        pk_train = pk_test = None
    info = Amputator(_CFG).write(ROOT_DIR, AGENT_DIR, peek_train=pk_train, peek_test=pk_test)
    log("prehook", f"amputated student view -> /data_agent (train_at_grade={_CFG.train_at_grade}, "
                   f"mechanism={info['mechanism']}, rows_written={info['rows_written']}, "
                   f"missing_frac={info['missing_frac']})")


def set_permissions() -> None:
    subprocess.run(["chmod", "-R", "700", str(Path(CONTAINER_DATA_ROOT))], check=True)
    subprocess.run(["chmod", "-R", "755", str(Path(CONTAINER_DATA_AGENT))], check=True)
    SOLUTION.mkdir(parents=True, exist_ok=True)
    subprocess.run(["chown", "-R", "model:model", str(SOLUTION)], check=True)
    subprocess.run(["chmod", "-R", "755", str(SOLUTION)], check=True)
    log("prehook", "permissions set")


def leak_guard() -> None:
    forbidden = {"test_labels.npy"}
    leaked = sorted(forbidden & {p.name for p in AGENT_DIR.iterdir()})
    assert not leaked, f"prehook leaked into /data_agent: {leaked}"
    log("prehook", "leak-guard OK (no test labels / truth in /data_agent)")


def main() -> None:
    assert_world_state()
    project_student_view()
    set_permissions()
    leak_guard()
    log("prehook", "all checks passed")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log("prehook", f"FAILED: {e}")
        sys.exit(1)
