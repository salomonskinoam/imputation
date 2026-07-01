"""Covertype DIRECT-recovery task config (Direction A): score imputation quality vs truth.

Reuses the Covertype dataset + amputation from the downstream config, but flips scoring_mode to
"direct" (the grader compares recovered cells to the truth) and uses the recovery-framed prompt.
Immune to the downstream route-around problem (§12), so imputation skill separates by construction.
"""
from tasks_def.configs import covertype as _base

CONFIG: dict = {
    **_base.CONFIG,
    "scoring_mode": "direct",
    "task_description": "a tabular dataset of cartographic features (forest cover type)",
    "hints": [
        "Missing cells are NaN; fill them as accurately as you can.",
        "Only the originally-missing cells are scored, against the true values — exploit the "
        "correlations with the other columns; a conditional model beats a column mean.",
    ],
}
