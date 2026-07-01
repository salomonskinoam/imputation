"""Amputator: the single source of truth for the student-visible (corrupted) view.

Analog of fusion's worlds/fusion/projection.py StudentView. Reads the FULL CLEAN data from
`root_dir` (/data_root, grader-only), applies the configured NaN amputation to the target columns,
and writes the corrupted student view to `dest_dir` (/data_agent) — never test labels or truth. Used
by BOTH prehook (setup) and world.stage_inputs (deferred grade) so the view is byte-identical.

Mechanisms (config-driven; NaN deletion only, no corruption):
- **MAR**  — P(missing) ∝ rank of an OBSERVED driver column (default `Slope`); target cols only.
- **MNAR** — P(missing) ∝ rank of the target column's OWN value (self-masking) → forces extrapolation.
- **co_amputate** — pick rows by MNAR-on-the-primary-target, then NULL the target cols AND the
  configured reconstructor cols on those rows (correlated/blockwise) → removes the recovery path.
See readmes/README_general_direction.md §12.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

SPLITS = ("train", "test")


def _get(cfg, key, default=None):
    """Read a key from a plain dict OR an attr-style config (HorConfig)."""
    if isinstance(cfg, dict):
        return cfg.get(key, default)
    return getattr(cfg, key, default)


def _rank_frac(v: np.ndarray) -> np.ndarray:
    order = np.argsort(np.argsort(v))
    return order / max(len(v) - 1, 1)   # 0..1, high value -> ~1


def mar_amputate(X, driver_idx, target_idxs, rate, seed):
    """MAR: P(missing) ∝ rank(driver); driver stays observed."""
    rng = np.random.RandomState(seed)
    Xc = X.astype(np.float32, copy=True)
    p = np.minimum(1.0, 2.0 * rate * _rank_frac(Xc[:, driver_idx]))
    for j in target_idxs:
        Xc[rng.random(len(Xc)) < p, j] = np.nan
    return Xc


def mnar_amputate(X, target_idxs, rate, seed):
    """MNAR self-masking: for each target col, P(missing) ∝ rank of its OWN value."""
    rng = np.random.RandomState(seed)
    Xc = X.astype(np.float32, copy=True)
    for j in target_idxs:
        p = np.minimum(1.0, 2.0 * rate * _rank_frac(X[:, j]))
        Xc[rng.random(len(Xc)) < p, j] = np.nan
    return Xc


def co_amputate(X, target_idxs, reconstructor_idxs, rate, seed):
    """Blockwise: choose rows by MNAR on the primary target, then null targets + reconstructors on
    those rows (the recovery path disappears on the affected rows)."""
    rng = np.random.RandomState(seed)
    Xc = X.astype(np.float32, copy=True)
    p = np.minimum(1.0, 2.0 * rate * _rank_frac(X[:, target_idxs[0]]))
    rows = rng.random(len(Xc)) < p
    for j in list(target_idxs) + list(reconstructor_idxs):
        Xc[rows, j] = np.nan
    return Xc


def amputate_matrix(X, *, mechanism, target_idxs, driver_idx, reconstructor_idxs, rate, seed):
    """Dispatch. Returns a NaN-corrupted copy of X per the mechanism."""
    if mechanism == "MAR":
        return mar_amputate(X, driver_idx, target_idxs, rate, seed)
    if mechanism == "MNAR":
        return mnar_amputate(X, target_idxs, rate, seed)
    if mechanism == "co_amputate":
        return co_amputate(X, target_idxs, reconstructor_idxs, rate, seed)
    raise ValueError(f"unknown mechanism: {mechanism!r}")


class Amputator:
    """cfg may be a plain dict (local harness) or a HorConfig (in-container)."""

    def __init__(self, cfg) -> None:
        self.cfg = cfg
        self.mechanism = _get(cfg, "mechanism", "MAR")
        self.target_cols = list(_get(cfg, "target_cols"))
        self.driver_col = _get(cfg, "driver_col")
        self.reconstructor_cols = list(_get(cfg, "reconstructor_cols", []) or [])
        self.rate = float(_get(cfg, "rate"))
        self.seed = int(_get(cfg, "ampute_seed", 0))

    def _idxs(self, feature_names):
        name_to_i = {n: i for i, n in enumerate(feature_names)}
        need = [c for c in ([self.driver_col] if self.driver_col else []) + self.target_cols
                + self.reconstructor_cols if c is not None]
        missing = [c for c in need if c not in name_to_i]
        if missing:
            raise KeyError(f"amputate: columns not in feature_names: {missing}")
        driver_idx = name_to_i[self.driver_col] if self.driver_col else -1
        return (driver_idx,
                [name_to_i[c] for c in self.target_cols],
                [name_to_i[c] for c in self.reconstructor_cols])

    def corrupt(self, X, feature_names, split_offset: int = 0):
        driver_idx, target_idxs, recon_idxs = self._idxs(feature_names)
        return amputate_matrix(X, mechanism=self.mechanism, target_idxs=target_idxs,
                               driver_idx=driver_idx, reconstructor_idxs=recon_idxs,
                               rate=self.rate, seed=self.seed + split_offset)

    def write(self, root_dir: Path, dest_dir: Path, *, peek_train=None, peek_test=None) -> dict:
        """Project the corrupted view. peek_* = None → full; int → first N rows (0 → shape-only).
        Train is normally full (student develops on it); test is normally hidden (0) during rollout
        and revealed (None) at grade via stage_inputs."""
        root_dir, dest_dir = Path(root_dir), Path(dest_dir)
        dest_dir.mkdir(parents=True, exist_ok=True)
        meta = json.loads((root_dir / "meta.json").read_text())
        feature_names = list(meta["feature_names"])
        peek = {"train": peek_train, "test": peek_test}

        info: dict = {"missing_frac": {}, "rows_written": {}}
        for s_i, split in enumerate(SPLITS):
            X = np.load(root_dir / f"{split}_features.npy")
            Xc = self.corrupt(X, feature_names, split_offset=s_i)
            pk = peek[split]
            if pk is not None:
                Xc = Xc[:pk]
            np.save(dest_dir / f"{split}_features.npy", Xc)
            info["missing_frac"][split] = float(np.isnan(Xc).mean()) if len(Xc) else 0.0
            info["rows_written"][split] = int(len(Xc))
            if split == "train":  # train labels student-visible; test labels NEVER
                y = np.load(root_dir / "train_labels.npy")
                np.save(dest_dir / "train_labels.npy", y if pk is None else y[:pk])

        (dest_dir / "meta.json").write_text(json.dumps(self.student_meta(meta), indent=2))
        info["target_cols"] = self.target_cols
        info["mechanism"] = self.mechanism
        return info

    def student_meta(self, root_meta: dict) -> dict:
        return {
            "feature_names": list(root_meta["feature_names"]),
            "n_features": int(root_meta["n_features"]),
            "n_classes": int(root_meta["n_classes"]),
            "class_names": list(root_meta["class_names"]),
            "n_train": int(root_meta["n_train"]),
            "n_test": int(root_meta["n_test"]),
            "task": root_meta.get("task", ""),
        }
