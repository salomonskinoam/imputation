"""Adult categorical MULTI (grid: Adult · Categorical · Multi · No-coamp).

Recover three categorical columns: `occupation` (14 classes, medium skill ~0.25) + `relationship`
(6, easy ~0.65) + `marital-status` (7, easy ~0.71). occupation drives the spread; the two easy columns
test whether the multi mean dilutes (like Covertype) or holds. All scored by classification accuracy vs
majority-class, averaged over the three targets (verify.py categorical branch).
"""
from tasks_def.configs import adult as _base

CONFIG: dict = {
    **_base.CONFIG,
    "target_cols":      ["occupation", "relationship", "marital-status"],
    "categorical_cols": ["occupation", "relationship", "marital-status"],
    "hints": [
        "The missing cells are CATEGORY codes (each column is one of K classes), not quantities. "
        "Recover the classes.",
        "A conditional classifier that exploits the other columns beats always guessing the most common "
        "class; only the originally-missing cells are scored.",
    ],
}
