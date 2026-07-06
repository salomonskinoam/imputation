"""Offline vendor: Diabetes 130-US Hospitals (UCI id=296) → frozen COMPLETE snapshot.

Clinical modality: inpatient diabetes encounters. Native missingness ("?") concentrated in a few columns;
drop the high-missing columns + identifier columns, then drop rows with any remaining "?" → a complete
carve-out (~90k+ rows). Every categorical column is integer-coded as ONE column (pd.factorize); numeric
columns kept. The `labels` array is `readmitted` (NO/>30/<30 → 3 classes) for the stratified split only.

A categorical MULTI task recovers the admission triad + a hard anchor: `admission_type_id`,
`discharge_disposition_id`, `insulin`, `readmitted`.

Writes worlds/imputation/data/diabetes.npz: features float32 (N,F), labels int64 (N,), feature_names.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent.parent / "worlds" / "imputation" / "data" / "diabetes.npz"
DROP_COLS = ["encounter_id", "patient_nbr", "weight", "payer_code", "medical_specialty",
             "max_glu_serum", "A1Cresult"]   # >80% missing lab columns; not targets


def main() -> None:
    from ucimlrepo import fetch_ucirepo
    d = fetch_ucirepo(id=296)
    X = d.data.features.copy()
    y = d.data.targets.iloc[:, 0].astype(str).str.strip()   # readmitted: NO / >30 / <30

    X = X.drop(columns=[c for c in DROP_COLS if c in X.columns], errors="ignore")
    X = X.replace("?", np.nan)
    keep = X.notna().all(axis=1) & y.notna()
    X, y = X[keep].reset_index(drop=True), y[keep].reset_index(drop=True)

    cols = list(X.columns)
    mat = {}
    for c in cols:
        if pd.api.types.is_numeric_dtype(X[c]):
            mat[c] = X[c].to_numpy(dtype=np.float32)
        else:
            codes, uniq = pd.factorize(X[c], sort=True)
            mat[c] = codes.astype(np.float32)
            print(f"  cat {c}: {len(uniq)} classes, mode_freq={np.bincount(codes).max()/len(codes):.3f}")
    yv = pd.factorize(y, sort=True)[0].astype(np.int64)   # readmitted -> 0..2
    # readmitted is the hard-anchor TARGET: include it as a feature column (also the stratify label,
    # which is never revealed to the student, so no leak).
    cols = cols + ["readmitted"]
    mat["readmitted"] = yv.astype(np.float32)
    print(f"  cat readmitted: {len(set(yv.tolist()))} classes, mode_freq={np.bincount(yv).max()/len(yv):.3f}")
    Xv = np.column_stack([mat[c] for c in cols]).astype(np.float32)

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
