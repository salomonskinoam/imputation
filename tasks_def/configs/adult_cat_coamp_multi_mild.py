"""Adult categorical co-amputate MULTI — MILD dial-back (grid: Cat·Multi·Yes, hedge).

Same targets as adult_cat_coamp_multi (occupation + relationship + marital-status) but co-amputate ONLY
`education-num` (keep `education` observed) → milder hardening, less floor risk. Isolates whether removing
a single strong reconstructor already injects enough indirect-signal variance to spread.
"""
from tasks_def.configs import adult as _base

_T = ["occupation", "relationship", "marital-status"]

CONFIG: dict = {
    **_base.CONFIG,
    "mechanism":         "co_amputate",
    "target_cols":       _T,
    "categorical_cols":  _T,
    "reconstructor_cols": ["education-num"],
    "hints": [
        "The missing cells are CATEGORY codes (each column is one of K classes), not quantities. On the "
        "affected rows some predictor columns are ALSO missing — recover the classes from whatever signal "
        "remains, and note the targets may help predict each other.",
        "Only the originally-missing target cells are scored, against the true categories.",
    ],
}
