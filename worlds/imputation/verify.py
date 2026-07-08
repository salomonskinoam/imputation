"""Scorer for the imputation world. Two scoring modes, selected by cfg["scoring_mode"]:

- "downstream" (default): fit a FROZEN weak logistic on the student's imputed train features + the
  grader-only train labels, predict imputed test, report macro-F1. (Weak lever — see §12; kept for
  completeness / other datasets.)
- "direct": score IMPUTATION QUALITY directly — compare the student's imputed values at the amputed
  cells of the held-out TEST against the true values (grader-only). Per amputed numeric column,
  skill = 1 − RMSE(method) / RMSE(naive mean-fill), clamped [0,1]; the score is the mean over amputed
  columns. Naive mean-fill → 0, perfect recovery → 1. No downstream model to route around, so
  imputation skill separates by construction (Direction A).

Truth (clean features, all labels) lives in /data_root; the corrupted view (with the NaN mask) is in
/data_agent (full test revealed at grade via stage_inputs). `compute_scores(...)` is pure and is
called by the local harness and by the pytest gate suite (via _container_score).
"""
from __future__ import annotations

import base64
import json
from pathlib import Path

import numpy as np

from worlds.imputation.amputate import _get


def make_frozen_model(cfg):
    from sklearn.linear_model import LogisticRegression
    model = LogisticRegression(C=float(_get(cfg, "logistic_C", 1.0)),
                               max_iter=int(_get(cfg, "logistic_max_iter", 3000)))
    if _get(cfg, "standardize", False):
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        return make_pipeline(StandardScaler(), model)
    return model


def check_artifact(arr, n_rows: int, n_features: int, name: str) -> str | None:
    if arr is None:
        return f"{name} missing"
    if arr.ndim != 2 or arr.shape != (n_rows, n_features):
        return f"{name} shape {getattr(arr, 'shape', None)} != ({n_rows}, {n_features})"
    if not np.isfinite(arr).all():
        return f"{name} contains NaN/inf (not fully imputed)"
    return None


def _rmse(a, b):
    return float(np.sqrt(np.mean((np.asarray(a, float) - np.asarray(b, float)) ** 2)))


def _downstream_score(s_tr, s_te, ytr, yte, n_classes, cfg) -> dict:
    from sklearn.metrics import f1_score
    best_observed = float(_get(cfg, "best_observed", 1.0) or 1.0)
    model = make_frozen_model(cfg).fit(s_tr, ytr)
    macro_f1 = float(f1_score(yte, model.predict(s_te), average="macro", labels=list(range(n_classes))))
    return {"primary": "macro_f1", "score": macro_f1 / best_observed,
            "reason": f"macro-F1 = {macro_f1:.4f} (best_observed={best_observed})",
            "student_macro_f1": macro_f1, "gate_ok": True}


def _direct_score(data_root_dir: Path, data_agent_dir: Path, s_te, cfg, meta) -> dict:
    """Recovery quality on the held-out test's amputed cells vs truth.

    Scores ONLY the configured target_cols. Under co-amputate, reconstructor columns are also NaN'd
    (and must be imputed to pass the gate) but are NOT scored, so a "single-target" task stays single.
    For the shipped MAR tasks target_cols == the amputed cols, so this is identical to scoring all NaN
    cols. Falls back to discovering all NaN cols if no target_cols are configured."""
    truth = np.load(data_root_dir / "test_features.npy").astype(np.float64)      # clean (grader-only)
    corr = np.load(data_agent_dir / "test_features.npy").astype(np.float64)      # corrupted (has NaN)
    corr_tr = np.load(data_agent_dir / "train_features.npy").astype(np.float64)  # for the naive baseline
    mask = np.isnan(corr)
    name_to_i = {n: i for i, n in enumerate(meta["feature_names"])}
    target_cols = list(_get(cfg, "target_cols", []) or [])
    cand = [name_to_i[c] for c in target_cols if c in name_to_i] if target_cols else range(mask.shape[1])
    amputed_cols = [c for c in cand if mask[:, c].any()]
    cat_set = {name_to_i[c] for c in (_get(cfg, "categorical_cols", []) or []) if c in name_to_i}
    per_col = {}
    skills = []
    preds = []  # imputed values at the scored cells, col-major (for c in amputed_cols: rows ascending)
    for c in amputed_cols:
        m = mask[:, c]
        preds.append(np.asarray(s_te[m, c], dtype=np.float32))
        obs_tr = corr_tr[~np.isnan(corr_tr[:, c]), c]
        if c in cat_set:
            # Classification recovery: naive = train majority class, error = misclassification rate.
            t = np.rint(truth[m, c]).astype(int)
            p = np.rint(s_te[m, c]).astype(int)
            mode_cls = int(np.bincount(np.rint(obs_tr).astype(int)).argmax()) if len(obs_tr) else 0
            err_naive = float(np.mean(t != mode_cls))
            err_method = float(np.mean(p != t))
            skill = 0.0 if err_naive <= 1e-12 else max(0.0, min(1.0, 1.0 - err_method / err_naive))
            per_col[int(c)] = {"acc_method": round(1 - err_method, 4), "acc_naive": round(1 - err_naive, 4),
                               "skill": round(skill, 4), "n": int(m.sum()), "kind": "categorical"}
        else:
            naive_val = float(obs_tr.mean()) if len(obs_tr) else 0.0
            base = _rmse(np.full(m.sum(), naive_val), truth[m, c])
            method = _rmse(s_te[m, c], truth[m, c])
            skill = 0.0 if base <= 1e-12 else max(0.0, min(1.0, 1.0 - method / base))
            per_col[int(c)] = {"rmse_method": round(method, 4), "rmse_naive": round(base, 4),
                               "skill": round(skill, 4), "n": int(m.sum()), "kind": "numeric"}
        skills.append(skill)
    score = float(np.mean(skills)) if skills else 0.0
    kinds = "categorical" if cat_set else "numeric"
    # Persist the imputed values at the scored cells (col-major, ascending rows per col) so an offline
    # band engine can recompute per-cell resolution without re-running the solution. y_true is
    # reconstructable from the committed npz (deterministic amputation), aligned by scored_cols order.
    flat = np.concatenate(preds) if preds else np.empty(0, dtype=np.float32)
    return {"primary": "recovery", "score": score,
            "reason": f"recovery skill (1 - err/err_naive; {kinds}) mean over {len(skills)} amputed cols = {score:.4f}",
            "per_col": per_col, "gate_ok": True,
            "predictions_b64": base64.b64encode(flat.tobytes()).decode(),
            "scored_cols": [int(c) for c in amputed_cols]}


def compute_scores(data_root_dir: Path, data_agent_dir: Path, solution_dir: Path, cfg) -> dict:
    data_root_dir, data_agent_dir, solution_dir = map(Path, (data_root_dir, data_agent_dir, solution_dir))
    meta = json.loads((data_root_dir / "meta.json").read_text())
    F, n_classes = int(meta["n_features"]), int(meta["n_classes"])
    ytr = np.load(data_root_dir / "train_labels.npy")
    yte = np.load(data_root_dir / "test_labels.npy")
    mode = _get(cfg, "scoring_mode", "downstream")

    def _load(p):
        return np.load(p).astype(np.float32) if p.exists() else None
    s_tr = _load(solution_dir / "train_imputed.npy")
    s_te = _load(solution_dir / "test_imputed.npy")
    gate = (check_artifact(s_tr, len(ytr), F, "train_imputed")
            or check_artifact(s_te, len(yte), F, "test_imputed"))
    if gate is not None:
        return {"primary": mode, "score": 0.0, "reason": f"GATE FAIL: {gate}", "gate_ok": False}

    if mode == "direct":
        return _direct_score(data_root_dir, data_agent_dir, s_te, cfg, meta)
    return _downstream_score(s_tr, s_te, ytr, yte, n_classes, cfg)


# ── Container/pytest entrypoint ─────────────────────────────────────────────────
def _container_score() -> dict:
    from sdk.path_mappings import (CONTAINER_ACTIVE_CONFIG, CONTAINER_DATA_ROOT,
                                    CONTAINER_DATA_AGENT, CONTAINER_WORKDIR, CONTAINER_ROOT)
    cfg = json.loads(Path(CONTAINER_ACTIVE_CONFIG).read_text())
    data_rel = _get(cfg, "data_rel")
    res = compute_scores(Path(CONTAINER_DATA_ROOT) / data_rel,
                         Path(CONTAINER_DATA_AGENT) / data_rel,
                         Path(CONTAINER_WORKDIR) / "solution", cfg)
    (Path(CONTAINER_ROOT) / "benchmark_result.json").write_text(json.dumps(res))
    return res


def test_solution_scored():
    """Grade the student's imputed artifacts and assert the output gate passed.

    Checks the deliverable is well-formed (both arrays present, right shape, finite, no NaN) so a
    malformed submission fails loudly instead of scoring 0 silently. The recovery/macro-F1 value
    itself is reported by the grader from the JSON result; this only guards the artifact contract.
    """
    res = _container_score()
    assert res["gate_ok"], res["reason"]
