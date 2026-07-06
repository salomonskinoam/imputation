"""Bank categorical co-amputate SINGLE — high-cardinality salvage hedge (grid: Cat·Single·Yes, Bank).

Different-dataset hedge for the occupation salvage. Recover `job` (K=12, mode 0.22) — a high-cardinality,
distributed target — when its correlate `education` is co-amputated on the same rows (job↔education
redundancy per the bank-multi vet). job must then be recovered from the weaker residual (age/balance/
marital/housing/loan). Same thesis as the Adult occupation salvage: high cardinality avoids the floor that
sank the low-card education attempt; risk is CONVERGE, not floor. MEDIUM confidence.
"""
from tasks_def.configs import bank as _base

_T = ["job"]

CONFIG: dict = {
    **_base.CONFIG,
    "mechanism":          "co_amputate",
    "target_cols":        _T,
    "categorical_cols":   _T,
    "reconstructor_cols": ["education"],
    "hints": [
        "The missing cells are a CATEGORY code (one of K classes), not a quantity. On the affected rows a "
        "column that would help predict the target is ALSO missing, so recover the class from whatever "
        "weaker signal remains.",
        "Only the originally-missing target cells are scored, against the true category.",
    ],
}
