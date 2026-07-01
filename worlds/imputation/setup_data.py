"""Build-time data stage: committed npz -> FULL CLEAN data in /data_root (grader-only).

Runs once at Docker build via `python -m worlds.imputation.setup_data` (under model_venv). Loads the
committed snapshot (worlds/imputation/data/<npz_name>), takes a seeded stratified split into
n_train / n_test, and writes EVERYTHING — train+test features, train+test labels, meta — to
/data_root/<data_rel>. The prehook later amputates a student view into /data_agent; test labels and
the un-amputated truth never leave /data_root.

The core `build_data_root(...)` is also called directly by the local Stage-1 harness (no container).
A module-level guard exits nonzero so a broken data stage fails the image build, not grade time.
"""
from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

import numpy as np

from worlds.imputation.amputate import _get


def build_data_root(npz_path: Path, out_dir: Path, cfg) -> dict:
    from sklearn.model_selection import train_test_split

    npz_path, out_dir = Path(npz_path), Path(out_dir)
    data = np.load(npz_path, allow_pickle=True)
    X = data["features"].astype(np.float32)
    y = data["labels"].astype(np.int64)
    feature_names = [str(s) for s in data["feature_names"].tolist()]

    n_train = int(_get(cfg, "n_train"))
    n_test = int(_get(cfg, "n_test"))
    seed = int(_get(cfg, "split_seed", 0))
    n_classes = int(_get(cfg, "n_classes"))
    class_names = list(_get(cfg, "class_names"))

    Xtr, Xte, ytr, yte = train_test_split(
        X, y, train_size=n_train, test_size=n_test, random_state=seed, stratify=y)

    out_dir.mkdir(parents=True, exist_ok=True)
    np.save(out_dir / "train_features.npy", Xtr)
    np.save(out_dir / "train_labels.npy", ytr)
    np.save(out_dir / "test_features.npy", Xte)
    np.save(out_dir / "test_labels.npy", yte)   # grader-only; never copied to /data_agent

    meta = {
        "feature_names": feature_names,
        "n_features": int(X.shape[1]),
        "n_classes": n_classes,
        "class_names": class_names,
        "n_train": int(len(ytr)),
        "n_test": int(len(yte)),
        "task": _get(cfg, "task_description", ""),
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    assert set(np.unique(ytr).tolist()) | set(np.unique(yte).tolist()) <= set(range(n_classes)), \
        "labels outside 0..n_classes-1"
    return meta


def main() -> None:
    from sdk.path_mappings import CONTAINER_DATA_ROOT
    from sdk.hor_logger import log
    from worlds.imputation.active import active_config

    cfg = active_config()
    npz = Path(__file__).resolve().parent / "data" / _get(cfg, "npz_name")
    out = Path(CONTAINER_DATA_ROOT) / _get(cfg, "data_rel")
    meta = build_data_root(npz, out, cfg)
    log("setup_data", f"{_get(cfg, 'data_rel')} -> /data_root: "
                      f"train={meta['n_train']} test={meta['n_test']} F={meta['n_features']} "
                      f"n_classes={meta['n_classes']}")


if __name__ == "__main__":
    try:
        main()
        from sdk.hor_logger import log
        log("setup_data", "Done.")
    except Exception:
        traceback.print_exc()
        sys.exit(1)
