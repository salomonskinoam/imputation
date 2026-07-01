# Handoff: make more imputation tasks (cheaply)

Fresh chat starts here. First read `CLAUDE.md` + `readmes/README_general_direction.md` (§10 recipe, §12
failures, §13 the working task). This file = how to stamp out more tasks and what NOT to retry.

## State

One working task: **`covertype-impute-direct`** — score imputation *recovery* directly (recovered TEST
cells vs truth; `mean_c(1 − RMSE_c/RMSE_naive_c)`, 0 = mean-fill, 1 = perfect). Real agents (biggie)
recover ~0.33 (band 0.27–0.39), beat a HGB-MICE ref (0.26), ~10–12 separable levels. Hosted + validated.
Downstream variant (`covertype-impute`) is **parked** (see failures).

- task_id `ff227290-a39d-4cf8-a162-4d79b580743f` · eval `c56b6c86-36e5-45da-9f9b-8d40ae038f2b`
- mini-batch `0067d7a3-4134-40d9-a4eb-c29faeeb24fe`

## A task = npz + config + shim (engine is dataset-agnostic)

Everything else (`worlds/imputation/{amputate,verify,setup_data,world,prehook,prompt_builder}.py`) is
generic. To add a task, copy the covertype-direct trio and change values:
1. `tools/vendor_<ds>.py` → commit `worlds/imputation/data/<ds>.npz` (fetch via **ucimlrepo/OpenML**;
   figshare is blocked).
2. `tasks_def/configs/<ds>_direct.py` — `data_rel, npz_name, n_features, class_names, n_train, n_test,
   mechanism, driver_col, target_cols, rate`.
3. `tasks_def/<ds>_direct.py` instance + add to `tasks_def/__init__.py`.
4. `tasks/<ds>-impute-direct/` — copy the shim, swap `grader.py` import + `setup.sh IMPUTATION_TASK=`.
5. `hor.py create/push` → `validate -a noop|-a oracle` → `evaluations submit`.

## The easy generation axes

- **New dataset** (biggest lever, unlimited supply): any *complete* tabular set with numeric target
  cols works with direct scoring. Natively-missing sets (FICO/NHANES) need a carved complete subset.
- **New amputation on any dataset (config only → new task):** `mechanism` ∈ {MAR, MNAR, co_amputate},
  `rate`, `target_cols`, `driver_col`, `reconstructor_cols`. A mechanism×rate sweep is a whole task
  family for free.
- **Difficulty/resolution:** harder = amputate a *less-reconstructable* feature or a bigger `rate`;
  more separable levels = bigger `N_test` (σ ∝ 1/√(rate·N_test), so levels ∝ √).

## Pick a dataset/feature that separates (direct scoring)

Only requirement: the amputed feature is **recoverable by good methods but not by naive fill** →
**medium reconstructability ~0.5–0.9** (too high → trivial methods win; ~0 → nobody recovers →
floor-collapse). Vet before committing: `scratchpad/concentration.py` (per-feature MI + reconstruct-R²),
then `scratchpad/tiers_direct.py` for the realized spread. Shortlist (measured, §7/§10): FICO (numeric,
native codes → carve subset), California (`MedInc`), Adult (`relationship`, categorical → needs the
scoring branch below), Superconductivity (very redundant → likely too easy).

## Do NOT retry (measured dead ends)

- **Downstream scoring for a band.** A capable/standardized downstream model routes around missing
  features → mean-fill ≈ oracle, no spread (Covertype B0 panel §12; the §8 theorem). Prefer DIRECT.
- **Corrupt-not-delete** (inject wrong values): dropped as unrealistic/cheaty/non-scalable. NaN only.
- **Over-aggressive amputation** (high-rate MNAR, or co-amputating a feature + all its reconstructors)
  → nobody recovers → floor-collapse. Keep it recoverable.
- **Showing the agent the test set.** Always deferred (`train_at_grade=True`, `peek_test=0`): agent
  never sees test; grader re-runs its code on the held-out test. So deliverables must be **0-row-safe**
  (sklearn `.transform` errors on 0 rows).

## Eval + resolution (don't re-derive)

- **biggie-max-polara only**, `meteor`, `e2-custom-16-32768`, hosted (CLAUDE.md). `-a noop`→0; `-a oracle`
  grades a real score (hosted may show cosmetic **FAILED** since `best_observed=1` and oracle<1 — check
  `all checks passed` in the log, not the verdict word).
- Band = spread of biggie's runs (each run is a different solution → real skill band, not noise).
  Resolution: σ = SDK "sample" channel `√(v/N)`, N = amputed cells/col = `rate·N_test`,
  `v = (1−skill)²(κ_e−1)/4` (κ_e ≈ 3–5). Scripts: `scratchpad/{panel_adversarial,tiers_direct}.py`.
  Get submissions: `horizon rollouts pull <task_id>` → feedback `submission`.

## Open TODOs that unlock variety

- **Categorical direct-scoring branch in `verify.py`** (currently numeric NRMSE only) → unlocks
  categorical-imputation tasks (Adult/Telco/Soybean).
- Native-missing carve-out in vendor/setup_data (truth needed) for FICO/NHANES.
- Optional helper to stamp mechanism×rate variants from one config.

Pointers: `readmes/README_submission.md`, `readmes/tasks/covertype-impute-direct.md` (worked example +
resolution math); memory `flagship-amputation-targets`, `downstream-metric-insensitivity`,
`imputation-instrumental-literature`; reference world `../multimodal_fusion/`.
