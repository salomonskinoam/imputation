"""Bank Marketing categorical MULTI (grid: Bank · Categorical · Multi · No-coamp).

Recover four heterogeneous categorical columns (vet): `month` (12 classes, easy ~0.63) + `education`
(4, medium ~0.33) + `job` (12, medium ~0.29) + `marital` (3, low ~0.18). Redundancy: job↔education,
marital↔age, month↔campaign timing. Different modality (finance/marketing telemarketing) from the
clinical/census tasks. Scored by classification accuracy vs majority class, averaged over the 4 targets.
"""
from tasks_def.configs import bank as _base

_TARGETS = ["month", "education", "job", "marital"]

CONFIG: dict = {
    **_base.CONFIG,
    "target_cols":      _TARGETS,
    "categorical_cols": _TARGETS,
    "hints": [
        "The missing cells are CATEGORY codes (each column is one of K classes), not quantities. "
        "Recover the classes.",
        "A conditional classifier that exploits the other columns beats always guessing the most common "
        "class; only the originally-missing cells are scored.",
    ],
}
