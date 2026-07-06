"""Diabetes categorical MULTI (grid: Diabetes · Categorical · Multi · No-coamp).

Recover four heterogeneous categorical columns (vet: scratchpad/vet_diab_c4.py):
`insulin` (easy, skill ~0.60) + `admission_type_id` (medium ~0.33) + `admission_source_id` (low ~0.14) +
`readmitted` (hard ~0.10, the weakly-predictable anchor). The admission pair is mutually predictive; under
MAR-per-column the other targets are usually observed, so exploiting the redundancy is optional → the
solution space is varied → should spread (clinical analogue of the working Adult-multi). Scored by
classification accuracy vs majority class, averaged over the 4 targets.
"""
from tasks_def.configs import diabetes as _base

_TARGETS = ["insulin", "admission_type_id", "admission_source_id", "readmitted"]

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
