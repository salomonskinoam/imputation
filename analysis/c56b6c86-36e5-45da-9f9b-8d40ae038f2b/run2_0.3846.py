import os
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer

DATA = "/data_agent/covertype"
OUT = "/workdir/solution"
os.makedirs(OUT, exist_ok=True)

train = np.load(os.path.join(DATA, "train_features.npy")).astype(np.float32)
test = np.load(os.path.join(DATA, "test_features.npy")).astype(np.float32)

n_train = train.shape[0]
n_test = test.shape[0]
n_feat = train.shape[1]

# Concatenate train and test so the imputer can use test rows' observed features as training signal too
if n_test > 0:
    X_all = np.concatenate([train, test], axis=0)
else:
    X_all = train.copy()

# Find columns with any NaN across the concatenated matrix (typically 0, 5, 9)
target_cols = [c for c in range(n_feat) if np.isnan(X_all[:, c]).any()]
print("Target cols with NaN:", target_cols)

imputed = X_all.copy()

for c in target_cols:
    y = X_all[:, c]
    observed = ~np.isnan(y)
    missing = np.isnan(y)
    n_missing = int(missing.sum())
    if n_missing == 0:
        continue
    predictor_cols = [j for j in range(n_feat) if j != c]
    X_pred = X_all[:, predictor_cols]

    Xtr = X_pred[observed]
    ytr = y[observed]
    Xva = X_pred[missing]

    # Model 1: HGBR — larger trees
    m1 = HistGradientBoostingRegressor(
        max_iter=800, learning_rate=0.04, max_leaf_nodes=127,
        min_samples_leaf=15, l2_regularization=0.5, random_state=0,
        early_stopping=True, validation_fraction=0.1, n_iter_no_change=30,
    )
    m1.fit(Xtr, ytr)
    p1 = m1.predict(Xva)

    # Model 2: HGBR — smaller trees, more regularization
    m2 = HistGradientBoostingRegressor(
        max_iter=800, learning_rate=0.04, max_leaf_nodes=63,
        min_samples_leaf=25, l2_regularization=1.0, random_state=1,
        early_stopping=True, validation_fraction=0.1, n_iter_no_change=30,
    )
    m2.fit(Xtr, ytr)
    p2 = m2.predict(Xva)

    # Model 3: Random Forest on mean-imputed predictors
    imp = SimpleImputer(strategy="mean")
    Xtr_f = imp.fit_transform(Xtr)
    Xva_f = imp.transform(Xva)
    m3 = RandomForestRegressor(
        n_estimators=300, min_samples_leaf=3, n_jobs=-1, random_state=0
    )
    m3.fit(Xtr_f, ytr)
    p3 = m3.predict(Xva_f)

    preds = (p1 + p2 + p3) / 3.0
    imputed[missing, c] = preds
    print(f"col {c}: filled {n_missing} values (ensemble of HGBR x2 + RF)")

assert not np.isnan(imputed).any(), "NaNs remain!"

train_imp = imputed[:n_train].astype(np.float32)
test_imp = imputed[n_train:].astype(np.float32)

np.save(os.path.join(OUT, "train_imputed.npy"), train_imp)
np.save(os.path.join(OUT, "test_imputed.npy"), test_imp)
print("Saved:", train_imp.shape, test_imp.shape)

