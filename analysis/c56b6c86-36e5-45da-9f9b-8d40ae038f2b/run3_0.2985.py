"""
Imputation pipeline for Covertype dataset.

Missing values only appear in 3 continuous columns:
  0 = Elevation
  5 = Horizontal_Distance_To_Roadways
  9 = Horizontal_Distance_To_Fire_Points

Strategy: iterative (MICE-style) imputation using HistGradientBoostingRegressor.
We fit on the concatenation of train and test features (semi-supervised) since
the models only use feature columns to predict a missing feature column, no
labels are needed. This gives more data (~35k rows at grade time) which
improves accuracy noticeably.
"""

import os
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor

DATA_DIR = "/data_agent/covertype"
OUT_DIR = "/workdir/solution"
os.makedirs(OUT_DIR, exist_ok=True)


def main():
    train = np.load(os.path.join(DATA_DIR, "train_features.npy")).astype(np.float64)
    test = np.load(os.path.join(DATA_DIR, "test_features.npy")).astype(np.float64)

    n_train, n_feat = train.shape
    n_test = test.shape[0]
    assert n_feat == 54

    # Identify columns that actually contain any NaN in train (or test if non-empty).
    nan_mask_train = np.isnan(train)
    if n_test > 0:
        nan_mask_test = np.isnan(test)
        nan_any = nan_mask_train.any(axis=0) | nan_mask_test.any(axis=0)
    else:
        nan_any = nan_mask_train.any(axis=0)
    target_cols = [int(c) for c in np.where(nan_any)[0]]

    # Combine train + test for imputation (features only; no labels used).
    if n_test > 0:
        X_all = np.vstack([train, test])
    else:
        X_all = train.copy()

    # Mask of which cells were originally missing (so we know what to overwrite
    # at the end and what to leave observed).
    original_nan = np.isnan(X_all)

    # Initial fill with per-column mean of observed values.
    X_filled = X_all.copy()
    col_means = {}
    for c in target_cols:
        col = X_all[:, c]
        m = np.nanmean(col) if np.isfinite(np.nanmean(col)) else 0.0
        col_means[c] = m
        X_filled[np.isnan(col), c] = m

    # For non-target columns, if they somehow contain NaN (shouldn't, but just
    # in case), mean-fill them too so regressors see finite features.
    for c in range(n_feat):
        if c in target_cols:
            continue
        col = X_filled[:, c]
        if np.isnan(col).any():
            m = np.nanmean(col)
            if not np.isfinite(m):
                m = 0.0
            col[np.isnan(col)] = m
            X_filled[:, c] = col

    hgb_params = dict(
        max_iter=1000,
        learning_rate=0.03,
        max_depth=8,
        min_samples_leaf=10,
        l2_regularization=0.0,
        early_stopping=True,
        validation_fraction=0.15,
        n_iter_no_change=30,
        random_state=0,
    )

    # MICE-style iterations. Refit each target column using currently filled
    # values of the other columns (including other target columns).
    n_iters = 5
    for it in range(n_iters):
        for c in target_cols:
            observed = ~np.isnan(X_all[:, c])
            missing = ~observed
            if missing.sum() == 0:
                continue
            others = [i for i in range(n_feat) if i != c]
            X_train_c = X_filled[observed][:, others]
            y_train_c = X_all[observed, c]
            model = HistGradientBoostingRegressor(**hgb_params)
            model.fit(X_train_c, y_train_c)
            X_pred = X_filled[missing][:, others]
            preds = model.predict(X_pred)
            X_filled[missing, c] = preds

    # Split back into train / test.
    train_imputed = X_filled[:n_train].copy()
    if n_test > 0:
        test_imputed = X_filled[n_train:].copy()
    else:
        test_imputed = np.zeros((0, n_feat), dtype=np.float64)

    # Sanity: no NaN, correct shapes.
    assert train_imputed.shape == (n_train, n_feat)
    assert test_imputed.shape == (n_test, n_feat)
    assert np.isfinite(train_imputed).all()
    assert np.isfinite(test_imputed).all() or n_test == 0

    np.save(os.path.join(OUT_DIR, "train_imputed.npy"), train_imputed)
    np.save(os.path.join(OUT_DIR, "test_imputed.npy"), test_imputed)


if __name__ == "__main__":
    main()

