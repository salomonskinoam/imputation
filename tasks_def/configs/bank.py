"""Bank Marketing identity base (finance/marketing; natively categorical). Complete (tools/vendor_bank.py),
45,211 rows, 16 features; native "unknown" kept as a category. `labels` = subscription y (0/1) for the
split. Amputation: MAR on `age`, rate 0.5. Per-task files set target_cols / categorical_cols.
"""

CONFIG: dict = {
    "data_rel":         "bank",
    "npz_name":         "bank.npz",
    "task_description": "a tabular dataset of bank telemarketing campaign contacts",
    "n_classes":        2,
    "n_features":       16,
    "class_names":      ["no", "yes"],
    "n_train":    5000,
    "n_test":     20000,
    "split_seed": 0,
    "mechanism":   "MAR",
    "driver_col":  "age",
    "rate":        0.5,
    "ampute_seed": 0,
    "scoring_mode":  "direct",
    "best_observed": 1.0,
}
