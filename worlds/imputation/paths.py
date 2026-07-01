"""Grade-time paths for the imputation world (world-generic; no per-task data dependency).

The data dir (<base>/<data_rel>) is per-task, so consumers that hold the active config compute it
themselves (prehook from active_config, verify from the side-channel). Grading always runs
containerized, so the bases are the literal container locations.
"""
from pathlib import Path

from sdk.path_mappings import CONTAINER_WORKDIR, CONTAINER_ROOT, CONTAINER_TASK_LOG
from worlds.imputation.config_world import CONFIG

WORKDIR_PATH: Path = Path(CONTAINER_WORKDIR)
ROOT_PATH: Path = Path(CONTAINER_ROOT)

# The student's deliverable + the two produced artifacts (imputed feature matrices).
SOLUTION_SCRIPT: Path = WORKDIR_PATH / CONFIG["script_rel"]
TRAIN_IMPUTED:   Path = WORKDIR_PATH / CONFIG["train_imputed_rel"]
TEST_IMPUTED:    Path = WORKDIR_PATH / CONFIG["test_imputed_rel"]   # sentinel artifact for grade()

# Grader-only world files (under /root/src, 700, student-invisible).
_WORLD_DIR = Path(__file__).resolve().parent
VERIFY_FILE:   Path = _WORLD_DIR / "verify.py"
PYTEST_REPORT: Path = ROOT_PATH / "pytest_report.json"
BENCH_RESULT:  Path = ROOT_PATH / "benchmark_result.json"
TASK_LOG:      Path = Path(CONTAINER_TASK_LOG)
