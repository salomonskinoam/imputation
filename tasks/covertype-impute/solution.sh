#!/usr/bin/env bash
set -euo pipefail
# Oracle / reference solution: a strong conditional imputer (HGB-MICE). Writes the deliverable script
# and RUNS it (static mode), leaving the two imputed-feature artifacts for the grader to score.
mkdir -p /workdir/solution
cat > /workdir/solution/solution.py <<'PY'
import json
from pathlib import Path
import numpy as np
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer
from sklearn.ensemble import HistGradientBoostingRegressor

DATA = Path("/data_agent/covertype")
OUT = Path("/workdir/solution")
OUT.mkdir(parents=True, exist_ok=True)

Xtr = np.load(DATA / "train_features.npy")
Xte = np.load(DATA / "test_features.npy")
imp = IterativeImputer(estimator=HistGradientBoostingRegressor(max_iter=60),
                       max_iter=3, random_state=0).fit(Xtr)
np.save(OUT / "train_imputed.npy", imp.transform(Xtr).astype(np.float32))
np.save(OUT / "test_imputed.npy", imp.transform(Xte).astype(np.float32))
print("wrote imputed features")
PY
/venvs/model_venv/bin/python /workdir/solution/solution.py
