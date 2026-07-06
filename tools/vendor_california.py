"""Offline vendor step: fetch California housing (OpenML id=537) and commit a frozen snapshot.

Run ONCE on a networked dev box (never at Docker build / grade time):
    horizon_env/bin/python tools/vendor_california.py

The raw StatLib California housing (1990 census block groups). sklearn's fetch_california_housing
pulls from figshare (BLOCKED here); OpenML 537 is the same data and reachable.

Writes worlds/imputation/data/california.npz with:
    features      float32 (N, 8)   -- median_income, housing_median_age, total_rooms, total_bedrooms,
                                       population, households, latitude, longitude
    labels        int64   (N,)     -- median_house_value discretized into 5 quantile tiers (0..4).
                                       Direct scoring never uses label VALUES (only row counts + the
                                       stratified split), but the engine needs an integer class label.
    feature_names <U..>   (8,)     -- column names, so the world can pick target/driver cols.

Direct-recovery task amputates `median_income` (measured reconstruct-R^2 ~0.68 from features alone:
recoverable by a good conditional model, far above naive mean-fill -> a real skill band).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

SEED = 0
N_BINS = 5
OUT = Path(__file__).resolve().parent.parent / "worlds" / "imputation" / "data" / "california.npz"


def main() -> None:
    from sklearn.datasets import fetch_openml

    d = fetch_openml(data_id=537, as_frame=True)
    feature_names = np.array(list(d.data.columns), dtype="U64")
    Xv = d.data.to_numpy(dtype=np.float32)
    y = d.target.to_numpy(dtype=np.float64)

    # discretize the continuous target into N_BINS quantile tiers -> integer class label 0..N_BINS-1
    edges = np.quantile(y, np.linspace(0, 1, N_BINS + 1)[1:-1])
    yv = np.digitize(y, edges).astype(np.int64)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT, features=Xv, labels=yv, feature_names=feature_names)
    print(f"wrote {OUT}")
    print(f"  features {Xv.shape} {Xv.dtype}  labels {yv.shape} classes={sorted(set(yv.tolist()))}")
    print(f"  feature_names={list(feature_names)}")
    print(f"  size ~{OUT.stat().st_size/1e6:.2f} MB")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"vendor FAILED: {type(e).__name__}: {e}")
        sys.exit(1)
