"""Bank categorical co-amputate MULTI — mild (grid: Bank · Cat · Multi · Yes — re-realization).

Bank-dataset copy of the Cat·Multi·Yes slot (Adult mild = WORKS). Same 4 targets as bank-impute-cat-multi
(month + education + job + marital); mild co-amputation of `day_of_week` (K=31, month's strongest temporal
carrier) on the affected rows → month must be recovered without its carrier, the other 3 targets anchor the
score off the floor (mirrors the Adult mild recipe: co-amp one hard-target predictor, keep an anchor set).
Tests whether the Cat·Multi·Yes WORKS verdict replicates across modality.
"""
from tasks_def.configs import bank as _base

_T = ["month", "education", "job", "marital"]

CONFIG: dict = {
    **_base.CONFIG,
    "mechanism":          "co_amputate",
    "target_cols":        _T,
    "categorical_cols":   _T,
    "reconstructor_cols": ["day_of_week"],
    "hints": [
        "The missing cells are CATEGORY codes (each column is one of K classes), not quantities. On the "
        "affected rows a predictor column is ALSO missing — recover the classes from whatever signal "
        "remains, and note the targets may help predict each other.",
        "Only the originally-missing target cells are scored, against the true categories.",
    ],
}
