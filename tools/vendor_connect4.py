"""Offline vendor: Connect-4 (UCI id=26) → frozen complete snapshot for CATEGORICAL imputation.

Board-game state modality: 42 board cells (a1..g6), each ∈ {b(lank), o, x} → integer-coded 0/1/2. Fully
complete (no missing). The `labels` array is the game outcome (loss/draw/win → 0/1/2) for the stratified
split only. A categorical MULTI task hides a few balanced mid-board cells; recovery must exploit the
physical redundancy (gravity: a cell is non-blank only if the one below it is; turn parity).

Writes worlds/imputation/data/connect4.npz: features float32 (N,42), labels int64 (N,), feature_names.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent.parent / "worlds" / "imputation" / "data" / "connect4.npz"
CELL = {"b": 0, "o": 1, "x": 2}
OUTCOME = {"loss": 0, "draw": 1, "win": 2}


def main() -> None:
    from ucimlrepo import fetch_ucirepo
    d = fetch_ucirepo(id=26)
    X = d.data.features.copy()
    y = d.data.targets.iloc[:, 0].astype(str).str.strip().str.lower()
    cols = list(X.columns)
    Xv = np.column_stack([X[c].astype(str).str.strip().str.lower().map(CELL).to_numpy() for c in cols]).astype(np.float32)
    yv = y.map(OUTCOME).to_numpy().astype(np.int64)
    assert not np.isnan(Xv).any(), "unexpected NaN / unmapped cell value"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT, features=Xv, labels=yv, feature_names=np.array(cols, dtype="U64"))
    print(f"wrote {OUT}")
    print(f"  features {Xv.shape} {Xv.dtype}  labels {yv.shape} classes={sorted(set(yv.tolist()))}")
    print(f"  feature_names={cols}")
    print(f"  size ~{OUT.stat().st_size/1e6:.2f} MB")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"vendor FAILED: {type(e).__name__}: {e}")
        sys.exit(1)
