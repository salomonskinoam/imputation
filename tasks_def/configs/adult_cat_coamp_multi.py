"""Adult categorical co-amputate MULTI (grid: Cat·Multi·Yes, best-shot).

Recover `occupation` + `relationship` + `marital-status` while co-amputating only the HARD target's
(occupation's) top predictors `education-num` + `education` on the same rows. Keep `sex`/`age`/`workclass`/
`hours-per-week` observed as anchors for the easy targets (floor insurance). occupation must then be
recovered indirectly (+ optional chaining from the imputed relationship/marital) = the skill-dependent
variance source. Note: co_amputate nulls all targets on the SAME rows, so the sibling-redundancy that made
the no-coamp multi spread is gone; spread here rides on the anchor + chaining path (LOW–MED confidence).
"""
from tasks_def.configs import adult as _base

_T = ["occupation", "relationship", "marital-status"]

CONFIG: dict = {
    **_base.CONFIG,
    "mechanism":         "co_amputate",
    "target_cols":       _T,
    "categorical_cols":  _T,
    "reconstructor_cols": ["education-num", "education"],
    "hints": [
        "The missing cells are CATEGORY codes (each column is one of K classes), not quantities. On the "
        "affected rows some predictor columns are ALSO missing — recover the classes from whatever signal "
        "remains, and note the targets may help predict each other.",
        "Only the originally-missing target cells are scored, against the true categories.",
    ],
}
