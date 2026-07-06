"""Offline vendor: fetch Adult (UCI id=2) and commit a frozen COMPLETE snapshot.

Run ONCE on a networked dev box:
    horizon_env/bin/python tools/vendor_adult.py

Adult is natively categorical (jobs, education, relationship, ...). We use it for CATEGORICAL
direct-recovery tasks: amputate a categorical FEATURE column and grade the recovered class.

Adult has native missingness ("?") in workclass/occupation/native-country; direct recovery needs the
truth, so we DROP rows with any missing → a complete carve-out (~45k rows). Each categorical column is
integer-coded (one column, 0..K-1) via pd.factorize; numeric columns are kept as-is. The `labels` array
is the income target (>50K -> 1) purely for the stratified split (direct scoring ignores label values).

Writes worlds/imputation/data/adult.npz:
    features      float32 (N, 14)   -- 6 numeric + 8 integer-coded categorical columns
    labels        int64   (N,)      -- income >50K (0/1), for the split only
    feature_names <U..>   (14,)     -- column names (incl. relationship, occupation, workclass, age, ...)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent.parent / "worlds" / "imputation" / "data" / "adult.npz"
CATEGORICAL = ["workclass", "education", "marital-status", "occupation",
               "relationship", "race", "sex", "native-country"]


def main() -> None:
    from ucimlrepo import fetch_ucirepo

    d = fetch_ucirepo(id=2)
    X = d.data.features.copy()
    y = d.data.targets.iloc[:, 0].astype(str).str.strip().str.rstrip(".")  # normalize ">50K." variant

    # Native missingness -> NaN, then drop for a complete carve-out.
    X = X.replace("?", np.nan)
    keep = X.notna().all(axis=1) & y.notna()
    X, y = X[keep].reset_index(drop=True), y[keep].reset_index(drop=True)

    cols = list(X.columns)
    codes = {}
    for c in cols:
        if c in CATEGORICAL:
            cat_codes, uniques = pd.factorize(X[c], sort=True)
            codes[c] = cat_codes.astype(np.float32)
            print(f"  {c}: {len(uniques)} classes, mode_freq={np.bincount(cat_codes).max()/len(cat_codes):.3f}")
        else:
            codes[c] = X[c].to_numpy(dtype=np.float32)

    Xv = np.column_stack([codes[c] for c in cols]).astype(np.float32)
    feature_names = np.array(cols, dtype="U64")
    yv = (y.to_numpy() == ">50K").astype(np.int64)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT, features=Xv, labels=yv, feature_names=feature_names)
    print(f"wrote {OUT}")
    print(f"  features {Xv.shape} {Xv.dtype}  labels {yv.shape} (>50K frac {yv.mean():.3f})")
    print(f"  feature_names={cols}")
    print(f"  size ~{OUT.stat().st_size/1e6:.2f} MB")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"vendor FAILED: {type(e).__name__}: {e}")
        sys.exit(1)
