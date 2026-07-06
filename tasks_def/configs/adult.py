"""Adult identity base config (US census income; natively categorical). Numeric identity + amputation
defaults shared by the categorical Adult tasks. Per-task files set target_cols / categorical_cols.

Vendored complete carve-out (tools/vendor_adult.py): 45,222 rows, 14 features (6 numeric + 8 integer-coded
categorical). `labels` = income >50K (0/1) for the stratified split only. Amputation: MAR on `age`,
rate 0.5. Categorical targets are recovered as classes (verify.py categorical branch).
"""

CONFIG: dict = {
    # ── Identity ────────────────────────────────────────────────────────────────
    "data_rel":         "adult",
    "npz_name":         "adult.npz",
    "task_description": "a tabular dataset of US census records (adult income)",
    "n_classes":        2,                       # the income LABEL (split only)
    "n_features":       14,
    "class_names":      ["<=50K", ">50K"],

    # ── Split sizes ─────────────────────────────────────────────────────────────
    "n_train":    5000,
    "n_test":     20000,
    "split_seed": 0,

    # ── Amputation ──────────────────────────────────────────────────────────────
    "mechanism":   "MAR",
    "driver_col":  "age",       # observed numeric driver
    "rate":        0.5,
    "ampute_seed": 0,

    # ── Scoring ─────────────────────────────────────────────────────────────────
    "scoring_mode":  "direct",
    "best_observed": 1.0,
}
