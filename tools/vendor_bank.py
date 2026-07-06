"""Offline vendor: Bank Marketing (UCI id=222) → frozen COMPLETE snapshot for CATEGORICAL imputation.

Finance/marketing modality: Portuguese bank telemarketing campaign. Complete (no missing; "unknown" is a
valid category). Each categorical column integer-coded as ONE column; numeric kept. `labels` = the
subscription target y (yes/no → 1/0) for the stratified split only.

Writes worlds/imputation/data/bank.npz: features float32 (N,F), labels int64 (N,), feature_names.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent.parent / "worlds" / "imputation" / "data" / "bank.npz"


def main() -> None:
    from ucimlrepo import fetch_ucirepo
    d = fetch_ucirepo(id=222)
    X = d.data.features.copy()
    y = d.data.targets.iloc[:, 0].astype(str).str.strip().str.lower()
    keep = y.notna()
    X, y = X[keep].reset_index(drop=True), y[keep].reset_index(drop=True)

    cols = list(X.columns)
    mat = {}
    for c in cols:
        if pd.api.types.is_numeric_dtype(X[c]):
            mat[c] = X[c].to_numpy(dtype=np.float32)
        else:
            # keep native "unknown"/NaN as its own category (no row loss); don't target mostly-unknown cols
            codes, uniq = pd.factorize(X[c].astype("object").fillna("unknown"), sort=True)
            mat[c] = codes.astype(np.float32)
            print(f"  cat {c}: {len(uniq)} classes, mode_freq={np.bincount(codes).max()/len(codes):.3f}")
    Xv = np.column_stack([mat[c] for c in cols]).astype(np.float32)
    yv = (y == "yes").astype(np.int64)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT, features=Xv, labels=yv, feature_names=np.array(cols, dtype="U64"))
    print(f"wrote {OUT}")
    print(f"  features {Xv.shape} {Xv.dtype}  labels {yv.shape} (yes frac {yv.mean():.3f})")
    print(f"  feature_names={cols}")
    print(f"  size ~{OUT.stat().st_size/1e6:.2f} MB")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"vendor FAILED: {type(e).__name__}: {e}")
        sys.exit(1)
