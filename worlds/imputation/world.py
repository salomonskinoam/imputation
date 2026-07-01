"""ImputationWorld: the imputation world's HorTask subclass.

Fills HorTask's override points. The grade orchestration (produce -> gate -> benchmark -> score)
lives in HorTask; this supplies the task-specific pieces and the agent-time/grader-time axis
(_produce + stage_inputs), mirroring fusion. The deliverable is imputed FEATURE matrices (train +
test); verify.py fits the frozen model and scores.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

from sdk.hor_task import HorTask
from sdk.path_mappings import CONTAINER_DATA_AGENT, CONTAINER_DATA_ROOT

from worlds.imputation import config_world
from worlds.imputation.paths import (
    SOLUTION_SCRIPT, TRAIN_IMPUTED, TEST_IMPUTED, VERIFY_FILE, BENCH_RESULT,
    PYTEST_REPORT, TASK_LOG,
)
from worlds.imputation.prompt_builder import PromptBuilder


class ImputationWorld(HorTask):
    WORLD_CONFIG = config_world.CONFIG
    INJECTED_PACKAGES = ("worlds", "tasks_def")

    def build_prompt(self) -> str:
        return PromptBuilder(self.config, self.source_dir).build()

    def dockerfile_template(self) -> Path:
        return Path(__file__).resolve().parent / "Dockerfile"

    def _produce(self) -> dict:
        """Agent-time (static, default): the agent already wrote the imputed-feature artifacts in its
        rollout — score them as-is, no grade-time run. Grader-time (train_at_grade): re-run the
        deliverable on the full revealed data within the grade cap."""
        if self.config.train_at_grade:
            return super()._produce()
        if self.produced_artifact_path().exists() and TRAIN_IMPUTED.exists():
            return {"returncode": 0, "timed_out": False, "duration_s": 0.0,
                    "stdout": "static mode: scoring the agent-produced imputed features", "stderr": ""}
        return super()._produce()

    def stage_inputs(self) -> None:
        """Deferred mode only: reveal the full corrupted student view via the SAME Amputator the
        prehook uses, then re-assert student perms. No-op in static mode. Imported lazily so the host
        never needs numpy."""
        if not self.config.train_at_grade:
            return
        from worlds.imputation.amputate import Amputator
        data_rel = self.config.data_rel
        agent_dir = Path(CONTAINER_DATA_AGENT) / data_rel
        Amputator(self.config).write(Path(CONTAINER_DATA_ROOT) / data_rel, agent_dir,
                                     peek_train=None, peek_test=None)  # reveal full test at grade
        subprocess.run(["chmod", "-R", "755", str(agent_dir)], check=True)

    # ── path overrides ───────────────────────────────────────────────────────────
    def deliverable_path(self) -> Path: return SOLUTION_SCRIPT
    def produced_artifact_path(self) -> Path: return TEST_IMPUTED   # sentinel; verify checks both
    def verify_file(self) -> Path: return VERIFY_FILE
    def bench_result_path(self) -> Path: return BENCH_RESULT
    def pytest_report_path(self) -> Path: return PYTEST_REPORT
    def task_log_path(self) -> Path: return TASK_LOG
    def upload_probe_file(self) -> Optional[Path]: return None
