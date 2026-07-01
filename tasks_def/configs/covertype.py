"""Per-task config for the Covertype imputation instance (pure data; overrides config_world).

All values are calibrated/measured this session (see readmes/README_building_the_world.md §2-§3):
MAR on Slope at rate 0.5 over the top-3 mutual-information columns, scored by the frozen raw logistic
on macro-F1, with a small train (keeps the band) and a large test (resolution).
"""

CONFIG: dict = {
    # ── Identity ────────────────────────────────────────────────────────────────
    "data_rel":         "covertype",
    "npz_name":         "covertype.npz",
    "task_description": "predict the 7-class forest cover type from cartographic features",
    "n_classes":        7,
    "n_features":       54,
    "class_names": [
        "Spruce/Fir", "Lodgepole Pine", "Ponderosa Pine", "Cottonwood/Willow",
        "Aspen", "Douglas-fir", "Krummholz",
    ],

    # ── Split sizes ─────────────────────────────────────────────────────────────
    "n_train":    5000,    # small on purpose: keeps the weak model from routing around
    "n_test":     30000,   # large: sets resolution (separable tiers ∝ √N_test)
    "split_seed": 0,

    # ── Amputation (the band lever) ─────────────────────────────────────────────
    "mechanism":   "MAR",                # P(missing) ∝ rank of the observed driver column
    "driver_col":  "Slope",
    "target_cols": [
        "Elevation",
        "Horizontal_Distance_To_Roadways",
        "Horizontal_Distance_To_Fire_Points",
    ],
    "rate":        0.5,
    "ampute_seed": 0,

    # ── Scoring ─────────────────────────────────────────────────────────────────
    "objective":     "macro_f1",
    "best_observed": 1.0,    # no normalization: score = raw macro-F1. Spread is read from real eval runs.

    # ── Prompt hints (neutral; do NOT reveal missingness) ───────────────────────
    "hints": [
        "Some feature values may need cleaning before they are model-ready.",
        "The held-out rows are scored with a fixed linear classifier; engineer features accordingly.",
    ],
}
