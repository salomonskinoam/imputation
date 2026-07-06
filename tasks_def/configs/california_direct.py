"""California housing DIRECT-recovery task config (Direction A): score imputation quality vs truth.

Second dataset (proves the engine generalizes past Covertype). Raw StatLib California housing
(1990 census block groups, OpenML 537). Amputate `median_income` under MAR and grade recovered TEST
cells against the truth: skill = 1 - RMSE(method)/RMSE(naive mean-fill), 0 = mean-fill, 1 = perfect.

Calibration (scratchpad/vet_california.py): median_income reconstructs from the other features at
R^2 ~0.68 (no label) -> squarely in the 0.5-0.9 sweet spot: recoverable by a good conditional model,
hopeless for naive fill. A strong imputer lands ~0.43 skill, so a real band separates by construction.
Single target on purpose (population/rooms are near-trivially recoverable and would only dilute); the
band's resolution comes from a large n_test instead.
"""

CONFIG: dict = {
    # ── Identity ────────────────────────────────────────────────────────────────
    "data_rel":         "california",
    "npz_name":         "california.npz",
    "task_description": "a tabular dataset of California housing blocks (1990 census)",
    "n_classes":        5,
    "n_features":       8,
    "class_names": [
        "value_tier_0", "value_tier_1", "value_tier_2", "value_tier_3", "value_tier_4",
    ],

    # ── Split sizes ─────────────────────────────────────────────────────────────
    "n_train":    3000,     # enough to fit a conditional imputer
    "n_test":     17000,    # large: sets resolution (separable tiers ∝ √N_test); 20000 total of 20640
    "split_seed": 0,

    # ── Amputation (the band lever) ─────────────────────────────────────────────
    "mechanism":   "MAR",              # P(missing) ∝ rank of the observed driver column
    "driver_col":  "latitude",         # geography drives missingness; income stays recoverable
    "target_cols": ["median_income"],
    "rate":        0.5,
    "ampute_seed": 0,

    # ── Scoring ─────────────────────────────────────────────────────────────────
    "scoring_mode":  "direct",
    "best_observed": 1.0,    # raw score; spread is read from real eval runs

    # ── Prompt hints (recovery-framed) ──────────────────────────────────────────
    "hints": [
        "Missing cells are NaN; fill them as accurately as you can.",
        "Only the originally-missing cells are scored, against the true values — exploit the "
        "correlations with the other columns; a conditional model beats a column mean.",
    ],
}
