"""Bank categorical SINGLE (grid: Bank · Categorical · Single · No-coamp — re-realization).

Bank-dataset copy of the Cat·Single·No slot (Adult has occupation = marginal). Recover `job` (K=12, mode
0.22) with all predictors observed (plain MAR, no co-amputation). Second datapoint on the single-no-coamp
slot across modality; also establishes job's baseline recoverability for the co-amp hedge. Scored by
classification accuracy vs majority class.
"""
from tasks_def.configs import bank as _base

_T = ["job"]

CONFIG: dict = {
    **_base.CONFIG,
    "target_cols":      _T,
    "categorical_cols": _T,
    "hints": [
        "The missing cells are a CATEGORY code (one of K classes), not a quantity. Recover the class.",
        "A conditional classifier that exploits the other columns beats always guessing the most common "
        "class; only the originally-missing cells are scored.",
    ],
}
