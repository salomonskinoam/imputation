"""Adult categorical co-amputate SINGLE — HIGH-CARDINALITY salvage (grid: Cat·Single·Yes, best-shot v2).

The first Cat·Single·Yes attempts (relationship K=6, education K=4) FLOORED because each low-card target
had a single carrier: remove it → collapse to naive. Fix: use the HIGH-cardinality, distributed target
`occupation` (K=14, mode 0.13) — recoverable from many weak predictors, no single carrier, so removing its
strongest signal degrades but does not floor it. Co-amputate `education` + `education-num` (occupation's
strongest, mutually-redundant carrier) → occupation must be recovered from the distributed weak residual
(workclass/hours/sex/age/capital) where estimator/skill choice can diverge = the spread bet. Note:
co-amputating only education-num would be a non-op (deterministic from education), so both must go. Risk
shifts from FLOOR to CONVERGE (single categoricals tend to converge; no-coamp occupation was ~0.24
marginal). MEDIUM confidence.
"""
from tasks_def.configs import adult as _base

_T = ["occupation"]

CONFIG: dict = {
    **_base.CONFIG,
    "mechanism":          "co_amputate",
    "target_cols":        _T,
    "categorical_cols":   _T,
    "reconstructor_cols": ["education", "education-num"],
    "hints": [
        "The missing cells are a CATEGORY code (one of K classes), not a quantity. On the affected rows the "
        "columns that would most obviously predict the target are ALSO missing, so recover the class from "
        "whatever weaker signal remains.",
        "Only the originally-missing target cells are scored, against the true category.",
    ],
}
