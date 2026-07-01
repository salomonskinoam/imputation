"""Shared base config for the imputation world (plain dict, no imports).

What every imputation task shares: the deliverable/artifact layout, the FROZEN downstream model the
grader scores with (the student does NOT pick it — this is what makes imputation instrumental, see
readmes/README_building_the_world.md), and methodology defaults. Per-task layers (dataset, amputation
mechanism/rate/columns, metric) live in tasks_def/configs/<task>.py and override these.
"""

CONFIG: dict = {
    # ── World-generic IO ────────────────────────────────────────────────────────
    # The student's deliverable is a script that writes IMPUTED FEATURE MATRICES (not predictions):
    "script_rel":        "solution/solution.py",        # student deliverable; grader may run it
    "train_imputed_rel": "solution/train_imputed.npy",  # produced artifact: imputed train features
    "test_imputed_rel":  "solution/test_imputed.npy",   # produced artifact: imputed test features

    # ── Data-handling axis (mirrors fusion) ─────────────────────────────────────
    # Handshake (decided §12): CODE-only, test hidden. Deferred mode — the student writes a pipeline
    # that the grader RE-RUNS on the full held-out test at grade time; the student never sees the
    # real test. Per-split peek: full corrupted TRAIN during rollout, test hidden (0 rows).
    "train_at_grade": True,
    "peek_train":     None,    # None = full corrupted train visible during rollout
    "peek_test":      0,       # 0 = test hidden during rollout (shape-only); revealed at grade

    # ── The FROZEN downstream model (grader-owned, weak on purpose) ──────────────
    # Weak + raw (unscaled) features is what keeps the model from routing around the amputed feature,
    # so imputation quality propagates to the score (measured: this maximizes separable tiers).
    "downstream_model":  "logistic",
    "logistic_C":        1.0,
    "logistic_max_iter": 3000,
    "standardize":       False,   # raw features on purpose (standardizing collapses the band)

    # ── Scoring ─────────────────────────────────────────────────────────────────
    "metric":    "macro_f1",
    "objective": "macro_f1",
}
