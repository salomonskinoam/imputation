"""Diabetes 130-US Hospitals identity base (clinical; natively categorical). Complete carve-out from
tools/vendor_diabetes.py: 98,053 rows, 43 features. `labels` = `readmitted` (3 classes) for the split.
Amputation: MAR on `num_medications`, rate 0.5. Per-task files set target_cols / categorical_cols.
"""

CONFIG: dict = {
    "data_rel":         "diabetes",
    "npz_name":         "diabetes.npz",
    "task_description": "a tabular dataset of hospital inpatient diabetes encounters",
    "n_classes":        3,
    "n_features":       43,
    "class_names":      ["readmit_<30", "readmit_>30", "readmit_NO"],
    "n_train":    5000,
    "n_test":     20000,
    "split_seed": 0,
    "mechanism":   "MAR",
    "driver_col":  "num_medications",
    "rate":        0.5,
    "ampute_seed": 0,
    "scoring_mode":  "direct",
    "best_observed": 1.0,
}
