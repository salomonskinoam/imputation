"""Offline vendor step: fetch Covertype (UCI id=31) and commit a small frozen snapshot.

Run ONCE on a networked dev box (never at Docker build / grade time):
    horizon_env/bin/python tools/vendor_covertype.py

Writes worlds/imputation/data/covertype.npz with:
    features      float32 (N, F)   -- the 54 cartographic features (10 numeric + 44 binary indicators)
    labels        int64   (N,)     -- cover type, remapped to 0..6
    feature_names <U..>   (F,)     -- column names, so the world can pick target/driver/protected cols

N is a seeded subsample (default 60k) — enough for train 5k + test 30k with margin, ~13 MB committed.
The committed file is the SINGLE source the image build reads; fetching never happens at build.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

N_KEEP = 60_000
SEED = 0
OUT = Path(__file__).resolve().parent.parent / "worlds" / "imputation" / "data" / "covertype.npz"


def main() -> None:
    from ucimlrepo import fetch_ucirepo

    d = fetch_ucirepo(id=31)
    X = d.data.features
    y = d.data.targets.iloc[:, 0].to_numpy()

    feature_names = np.array(list(X.columns), dtype="U64")
    Xv = X.to_numpy(dtype=np.float32)
    yv = y.astype(np.int64)

    # remap labels to dense 0..K-1
    classes = np.unique(yv)
    remap = {c: i for i, c in enumerate(classes.tolist())}
    yv = np.array([remap[c] for c in yv.tolist()], dtype=np.int64)

    rng = np.random.RandomState(SEED)
    if len(Xv) > N_KEEP:
        idx = np.sort(rng.choice(len(Xv), N_KEEP, replace=False))
        Xv, yv = Xv[idx], yv[idx]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT, features=Xv, labels=yv, feature_names=feature_names)
    print(f"wrote {OUT}")
    print(f"  features {Xv.shape} {Xv.dtype}  labels {yv.shape} classes={sorted(set(yv.tolist()))}")
    print(f"  feature_names[:12]={list(feature_names[:12])}")
    print(f"  size ~{OUT.stat().st_size/1e6:.1f} MB")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"vendor FAILED: {type(e).__name__}: {e}")
        sys.exit(1)
