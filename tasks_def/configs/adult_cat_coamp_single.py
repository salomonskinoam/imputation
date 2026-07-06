"""Adult categorical co-amputate SINGLE (grid: Cat·Single·Yes, best-shot).

Recover `relationship` (6 classes) when its near-duplicate `marital-status` AND the `sex` axis are
co-amputated on the same rows → the easy path is gone; recovery falls on a fragile weak-signal combination
(age/income/capital-gain/hours/occupation/education-num) = the California spread pattern. Base
recoverability ~0.65 gives headroom (not floor). Scored: classification accuracy on relationship only.
"""
from tasks_def.configs import adult as _base

_T = ["relationship"]

CONFIG: dict = {
    **_base.CONFIG,
    "mechanism":         "co_amputate",
    "target_cols":       _T,
    "categorical_cols":  _T,
    "reconstructor_cols": ["marital-status", "sex"],
    "hints": [
        "The missing cells are a CATEGORY code (one of K classes), not a quantity. On the affected rows "
        "some columns that would help predict the target are ALSO missing, so obvious correlations are "
        "unavailable — recover the class from whatever signal remains.",
        "Only the originally-missing target cells are scored, against the true category.",
    ],
}
