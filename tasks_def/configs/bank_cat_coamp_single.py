"""Bank categorical co-amputate SINGLE (grid: Cat·Single·Yes, hedge — different dataset).

Recover `education` (primary/secondary/tertiary/unknown) when its dominant predictor `job` is co-amputated
on the same rows. Base recoverability ~0.33, majority ~0.51 (a real naive floor to beat), only 3–4 stable
classes. Floor risk (education is job-carried). Scored: classification accuracy on education only.
"""
from tasks_def.configs import bank as _base

_T = ["education"]

CONFIG: dict = {
    **_base.CONFIG,
    "mechanism":         "co_amputate",
    "target_cols":       _T,
    "categorical_cols":  _T,
    "reconstructor_cols": ["job"],
    "hints": [
        "The missing cells are a CATEGORY code (one of K classes), not a quantity. On the affected rows "
        "some columns that would help predict the target are ALSO missing, so obvious correlations are "
        "unavailable — recover the class from whatever signal remains.",
        "Only the originally-missing target cells are scored, against the true category.",
    ],
}
