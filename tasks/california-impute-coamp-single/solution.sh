#!/usr/bin/env bash
set -euo pipefail
# Oracle / reference solution: a strong conditional imputer (HGB-MICE). Deferred handshake — the test
# is a 0-row placeholder during the rollout and the FULL held-out test is revealed at grade, when the
# grader re-runs this script. Must be 0-row-safe (sklearn .transform errors on 0 samples).
mkdir -p /workdir/solution
cat > /workdir/solution/solution.py <<'PY'
from pathlib import Path
import numpy as np
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer
from sklearn.ensemble import HistGradientBoostingRegressor

DATA = Path("/data_agent/california")
OUT = Path("/workdir/solution")
OUT.mkdir(parents=True, exist_ok=True)

Xtr = np.load(DATA / "train_features.npy")
Xte = np.load(DATA / "test_features.npy")
imp = IterativeImputer(estimator=HistGradientBoostingRegressor(max_iter=60),
                       max_iter=3, random_state=0).fit(Xtr)

def impute(X):  # 0-row-safe: the test placeholder is empty during development
    return imp.transform(X).astype(np.float32) if len(X) else X.astype(np.float32)

np.save(OUT / "train_imputed.npy", impute(Xtr))
np.save(OUT / "test_imputed.npy", impute(Xte))
print(f"wrote imputed features (train={len(Xtr)}, test={len(Xte)})")
PY
/venvs/model_venv/bin/python /workdir/solution/solution.py
