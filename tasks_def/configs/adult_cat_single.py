"""Adult categorical SINGLE (grid: Adult · Categorical · Single · No-coamp).

Recover the `occupation` category (14 classes, mode 0.13). Vetted (scratchpad/vet_adult.py) as the
sweet-spot categorical target: HGB classifier recovers ~0.35 acc vs 0.13 majority → skill ~0.25 (medium,
room to spread); offline resolution ~92 levels over [0,1] at n_test 20000. Scored by classification
accuracy vs majority-class (verify.py categorical branch).
"""
from tasks_def.configs import adult as _base

CONFIG: dict = {
    **_base.CONFIG,
    "target_cols":      ["occupation"],
    "categorical_cols": ["occupation"],
    "hints": [
        "The missing cells are a CATEGORY code (one of K classes), not a quantity. Recover the class.",
        "A conditional classifier that exploits the other columns beats always guessing the most common "
        "class; only the originally-missing cells are scored.",
    ],
}
