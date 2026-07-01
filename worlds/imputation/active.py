"""Resolve the merged config for the task named by $IMPUTATION_TASK (build + prehook contexts).

setup_data and prehook run as bare `python -m` processes with no task instance in hand, so they
re-resolve the config from the registry via the env var the Dockerfile bakes (ENV IMPUTATION_TASK)
and setup.sh exports. Grade time instead reads the side-channel (CONTAINER_ACTIVE_CONFIG).
"""
from __future__ import annotations

import functools
import os


@functools.lru_cache(maxsize=None)
def active_config():
    name = os.environ["IMPUTATION_TASK"]
    import tasks_def  # noqa: F401  importing registers every task instance
    from sdk.hor_task_registry import HorTaskRegistry
    return HorTaskRegistry.get(name).config
