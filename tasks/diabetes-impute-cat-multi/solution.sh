#!/usr/bin/env bash
set -euo pipefail
# Trivial placeholder filler (NOT an oracle; best_observed=1). Fills each missing cell with the train
# column mean so it is finite + 0-row-safe. Scores near the floor. We validate with -a noop.
mkdir -p /workdir/solution
cat > /workdir/solution/solution.py <<'PY'
from pathlib import Path
import numpy as np
DATA = Path("/data_agent/diabetes"); OUT = Path("/workdir/solution"); OUT.mkdir(parents=True, exist_ok=True)
Xtr = np.load(DATA / "train_features.npy"); Xte = np.load(DATA / "test_features.npy")
fill = np.nanmean(Xtr, axis=0)
def imp(X):
    if len(X) == 0: return X.astype(np.float32)
    Y = X.copy(); idx = np.where(np.isnan(Y)); Y[idx] = np.take(fill, idx[1]); return Y.astype(np.float32)
np.save(OUT / "train_imputed.npy", imp(Xtr)); np.save(OUT / "test_imputed.npy", imp(Xte))
print("placeholder mean-fill done", Xtr.shape, Xte.shape)
PY
/venvs/model_venv/bin/python /workdir/solution/solution.py
