"""
Impute the missing values in the covertype cartographic dataset.

Approach
--------
Iterative multivariate imputation with HistGradientBoostingRegressor.
For each column that contains NaN we build a regression model that predicts
the missing entries from all other columns (which have themselves already
been imputed in previous rounds).  Train labels are known and are useful,
especially for Elevation, so we also feed a class-probability vector as an
extra block of predictors: for training rows we use the one-hot label,
for test rows we use predicted probabilities from a classifier fitted on
the currently imputed training data.
"""
import os
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor, HistGradientBoostingClassifier

DATA_DIR = "/data_agent/covertype"
OUT_DIR = "/workdir/solution"
os.makedirs(OUT_DIR, exist_ok=True)


def main():
    train = np.load(os.path.join(DATA_DIR, "train_features.npy")).astype(np.float32)
    labels = np.load(os.path.join(DATA_DIR, "train_labels.npy")).astype(np.int64)
    test = np.load(os.path.join(DATA_DIR, "test_features.npy")).astype(np.float32)

    n_train = train.shape[0]
    n_test = test.shape[0]
    n_features = train.shape[1]
    assert n_features == 54
    n_classes = max(int(labels.max()) + 1 if len(labels) > 0 else 7, 7)

    # Combine train and test so imputation is done jointly.
    if n_test > 0:
        X = np.concatenate([train, test], axis=0)
    else:
        X = train.copy()

    nan_mask = np.isnan(X)
    nan_per_col = nan_mask.sum(axis=0)
    miss_cols = [c for c in range(n_features) if nan_per_col[c] > 0]

    if not miss_cols:
        np.save(os.path.join(OUT_DIR, "train_imputed.npy"),
                X[:n_train].astype(np.float32))
        np.save(os.path.join(OUT_DIR, "test_imputed.npy"),
                X[n_train:].astype(np.float32))
        return

    # Initial mean fill for the missing columns.
    col_means = np.nanmean(X, axis=0)
    col_means = np.where(np.isnan(col_means), 0.0, col_means)
    X_filled = X.copy()
    for c in miss_cols:
        X_filled[nan_mask[:, c], c] = col_means[c]

    # One-hot for training labels.
    train_oh = np.zeros((n_train, n_classes), dtype=np.float32)
    train_oh[np.arange(n_train), labels[:n_train]] = 1.0

    reg_kwargs = dict(
        max_iter=1000,
        learning_rate=0.03,
        max_leaf_nodes=63,
        min_samples_leaf=10,
        random_state=0,
        early_stopping=False,
    )
    clf_kwargs = dict(
        max_iter=300,
        learning_rate=0.1,
        random_state=0,
    )

    n_iters = 6
    for it in range(n_iters):
        # Predicted class probabilities for the test block (once we have a
        # halfway-reasonable imputation of the features).
        if n_test > 0 and it > 0:
            clf = HistGradientBoostingClassifier(**clf_kwargs)
            clf.fit(X_filled[:n_train], labels)
            test_probs = clf.predict_proba(X_filled[n_train:]).astype(np.float32)
            if test_probs.shape[1] < n_classes:
                pad = np.zeros((test_probs.shape[0], n_classes - test_probs.shape[1]),
                               dtype=np.float32)
                test_probs = np.concatenate([test_probs, pad], axis=1)
        else:
            test_probs = np.full((n_test, n_classes), 1.0 / n_classes, dtype=np.float32)

        if n_test > 0:
            lb_feats = np.concatenate([train_oh, test_probs], axis=0)
        else:
            lb_feats = train_oh
        X_ext = np.concatenate([X_filled, lb_feats], axis=1)

        new_filled = X_filled.copy()
        for c in miss_cols:
            obs = ~nan_mask[:, c]
            miss = nan_mask[:, c]
            if miss.sum() == 0:
                continue
            X_pred = np.delete(X_ext, c, axis=1)
            y = X_filled[obs, c]
            m = HistGradientBoostingRegressor(**reg_kwargs)
            m.fit(X_pred[obs], y)
            new_filled[miss, c] = m.predict(X_pred[miss])
        X_filled = new_filled

    assert np.isfinite(X_filled).all(), "Non-finite values remaining after imputation"

    train_out = X_filled[:n_train].astype(np.float32)
    test_out = X_filled[n_train:].astype(np.float32)
    if test_out.shape[0] == 0:
        test_out = test_out.reshape(0, n_features).astype(np.float32)

    np.save(os.path.join(OUT_DIR, "train_imputed.npy"), train_out)
    np.save(os.path.join(OUT_DIR, "test_imputed.npy"), test_out)


if __name__ == "__main__":
    main()

