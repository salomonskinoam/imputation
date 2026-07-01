"""Impute missing cells in the covertype tabular dataset."""
import os
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor

DATA_DIR = "/data_agent/covertype"
OUT_DIR = "/workdir/solution"
os.makedirs(OUT_DIR, exist_ok=True)


def build_features(X, labels):
    """Feature matrix used to predict missing cells:
    the raw 54 columns (with NaN kept – HistGradientBoosting handles NaN natively)
    plus the label as an extra column when available."""
    if labels is None:
        # No labels for the test rows – append a NaN column so the model
        # simply treats "unknown label" as missing.
        extra = np.full((X.shape[0], 1), np.nan, dtype=np.float64)
    else:
        extra = labels.reshape(-1, 1).astype(np.float64)
    return np.concatenate([X.astype(np.float64), extra], axis=1)


def main():
    train = np.load(os.path.join(DATA_DIR, "train_features.npy")).astype(np.float64)
    test = np.load(os.path.join(DATA_DIR, "test_features.npy")).astype(np.float64)
    labels = np.load(os.path.join(DATA_DIR, "train_labels.npy"))

    n_train, n_feat = train.shape
    n_test = test.shape[0]
    print(f"train {train.shape}, test {test.shape}")

    # Identify which columns actually have missing values in train.
    nan_per_col = np.isnan(train).sum(axis=0)
    miss_cols = [c for c in range(n_feat) if nan_per_col[c] > 0]
    print("columns with missing:", miss_cols)

    # Column means (of the observed values) – used to fill any column that
    # somehow only has missing values in the test set but not train.
    col_means = np.nanmean(train, axis=0)

    train_out = train.copy()
    test_out = test.copy()

    if len(miss_cols) == 0:
        np.save(os.path.join(OUT_DIR, "train_imputed.npy"),
                train_out.astype(np.float32))
        np.save(os.path.join(OUT_DIR, "test_imputed.npy"),
                test_out.astype(np.float32))
        return

    # Stack train + test features for prediction.  Train uses true labels;
    # test contributes an "unknown label" column filled with NaN.
    X_train_full = build_features(train, labels)  # (n_train, n_feat+1)
    if n_test > 0:
        X_test_full = build_features(test, None)  # (n_test, n_feat+1)

    n_feat_ext = X_train_full.shape[1]

    for c in miss_cols:
        other_cols = [i for i in range(n_feat_ext) if i != c]

        # Training rows: those where the target column is observed.
        obs_mask_train = ~np.isnan(train[:, c])
        Xtr = X_train_full[obs_mask_train][:, other_cols]
        ytr = train[obs_mask_train, c]

        # Ensemble of gradient boosters with different seeds.
        preds_train_missing = None
        preds_test_missing = None

        # rows we need to predict for
        train_missing_mask = np.isnan(train[:, c])
        Xtr_missing = X_train_full[train_missing_mask][:, other_cols]

        if n_test > 0:
            test_missing_mask = np.isnan(test[:, c])
            Xte_missing = X_test_full[test_missing_mask][:, other_cols]
        else:
            test_missing_mask = None
            Xte_missing = None

        n_seeds = 5
        preds_train_list = []
        preds_test_list = []
        for seed in range(n_seeds):
            reg = HistGradientBoostingRegressor(
                max_iter=1000,
                learning_rate=0.03,
                max_leaf_nodes=31,
                min_samples_leaf=20,
                random_state=seed,
                early_stopping=True,
                validation_fraction=0.15,
                n_iter_no_change=30,
            )
            reg.fit(Xtr, ytr)
            if Xtr_missing.shape[0] > 0:
                preds_train_list.append(reg.predict(Xtr_missing))
            if Xte_missing is not None and Xte_missing.shape[0] > 0:
                preds_test_list.append(reg.predict(Xte_missing))

        if preds_train_list:
            preds_train_missing = np.mean(preds_train_list, axis=0)
            train_out[train_missing_mask, c] = preds_train_missing

        if preds_test_list:
            preds_test_missing = np.mean(preds_test_list, axis=0)
            test_out[test_missing_mask, c] = preds_test_missing

        print(f"col {c}: filled {train_missing_mask.sum()} train, "
              f"{0 if n_test == 0 else test_missing_mask.sum()} test")

    # Safety net: fill any remaining NaN (e.g. columns that only turned out to
    # be missing in test) with the training-column mean.
    for c in range(n_feat):
        nan_tr = np.isnan(train_out[:, c])
        if nan_tr.any():
            train_out[nan_tr, c] = col_means[c] if not np.isnan(col_means[c]) else 0.0
        if n_test > 0:
            nan_te = np.isnan(test_out[:, c])
            if nan_te.any():
                test_out[nan_te, c] = col_means[c] if not np.isnan(col_means[c]) else 0.0

    assert not np.isnan(train_out).any(), "train still has NaN"
    if n_test > 0:
        assert not np.isnan(test_out).any(), "test still has NaN"

    np.save(os.path.join(OUT_DIR, "train_imputed.npy"),
            train_out.astype(np.float32))
    np.save(os.path.join(OUT_DIR, "test_imputed.npy"),
            test_out.astype(np.float32))
    print("Saved outputs.")


if __name__ == "__main__":
    main()

