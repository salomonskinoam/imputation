# Handoff: making more imputation tasks (cheaply), remembering what didn't work

Start a fresh chat from this file. Goal: **spin up more imputation tasks by reusing the working
direct-recovery machine**, without repeating the dead ends. Read `CLAUDE.md` and
`readmes/README_general_direction.md` first (esp. §7 dataset table, §10 selection recipe, §12 what
failed, §13 the working task). Memory (`MEMORY.md`) auto-loads more context.

## Where we are (one line)

One working, hosted, validated task: **`covertype-impute-direct`** (Direction A = score imputation
recovery directly). Real agents (biggie-max-polara) recover mean **0.326** (band 0.27–0.39), beating a
HGB-MICE reference (0.26); ~10–12 separable skill levels. The downstream variant is parked (§ below).

Coordinates:
- direct task: `covertype-impute-direct`, task_id `ff227290-a39d-4cf8-a162-4d79b580743f`, eval `c56b6c86-36e5-45da-9f9b-8d40ae038f2b`
- downstream (PARKED): `covertype-impute`, task_id `c20fa806-8b3a-4c34-bfb9-f3f97c7cd3d4`
- mini-batch (all `hor.py create`): `0067d7a3-4134-40d9-a4eb-c29faeeb24fe`

## The machine (why more tasks are cheap)

The world engine is **dataset-agnostic**; a task is just **a committed npz + a config + an apex shim**.
Key files (all under `worlds/imputation/`):
- `amputate.py` — `Amputator` + `amputate_matrix`: mechanisms **MAR / MNAR / co_amputate** (NaN
  deletion), config-driven, single source of truth (used by prehook + stage_inputs).
- `verify.py` — `scoring_mode: "downstream" | "direct"`. **direct** = `mean_c(1 − RMSE_c/RMSE_naive_c)`
  on the amputed TEST cells vs truth (0 = mean-fill, 1 = perfect). **numeric only right now.**
- `setup_data.py` (committed npz → `/data_root` full clean), `world.py`, `prehook.py`,
  `prompt_builder.py` (neutral downstream template + recovery-framed direct template), `config_world.py`
  (world defaults: `train_at_grade=True`, `peek_train=None`, `peek_test=0` → deferred, test hidden).
- Per-task: `tasks_def/configs/covertype_direct.py`, `tasks_def/covertype_direct.py`,
  `tasks/covertype-impute-direct/` (apex shim), `tools/vendor_covertype.py` (offline vendor).

## Easy ways to make more tasks (the axes)

1. **New dataset (biggest lever; unlimited supply).** Any complete tabular dataset with numeric target
   columns works with direct scoring. Steps ≈ 30 min:
   - `tools/vendor_<ds>.py` (copy vendor_covertype.py): fetch via **ucimlrepo / OpenML** (figshare CDN
     is blocked in this env), commit `worlds/imputation/data/<ds>.npz` (`features`, `labels`,
     `feature_names`).
   - `tasks_def/configs/<ds>_direct.py` (copy covertype_direct.py): set `data_rel, npz_name,
     n_features, n_classes/class_names, n_train, n_test, mechanism, driver_col, target_cols, rate`.
   - `tasks_def/<ds>_direct.py` instance + register in `tasks_def/__init__.py`.
   - `tasks/<ds>-impute-direct/` shim (copy covertype-impute-direct): swap `grader.py` import +
     `setup.sh` `IMPUTATION_TASK=`. Oracle `solution.sh` must stay **0-row-safe**.
   - `hor.py create <task> --mini-batch-id <mb>` → `push` → `validate -a noop|-a oracle` → eval.
2. **New amputation on any dataset (config-only → new task).** Vary `mechanism` (MAR / MNAR /
   co_amputate), `rate`, `target_cols`, `driver_col`, `reconstructor_cols`. Each combination rewards a
   different imputation skill.
3. **Resolution / difficulty knobs.** `rate` and `N_test` (σ ∝ 1/√(rate·N_test); more test cells →
   more separable levels, ∝ √). Harder target feature (lower reconstructability) → wider method spread.

## Design gates for a NEW dataset/feature (so the task actually separates)

From §10 recipe, but for DIRECT scoring the route-around problem is gone, so the core requirement is
just **recoverability spread**:
- **Complete cells** (we amputate ourselves → we own the truth). Natively-missing datasets (FICO,
  NHANES) need a carved complete subset first.
- **Amputed feature(s) recoverable by good methods but NOT by naive fill** → medium reconstructability
  (~0.5–0.9). Too high (>0.95) → even trivial methods recover (narrow); too low (~0) → nobody recovers
  (floor-collapse). Check with `scratchpad/concentration.py` (per-feature MI + reconstruct-R²) before
  committing; then `scratchpad/panel_adversarial.py` / `tiers_direct.py` to confirm a spread.
- Dataset shortlist (measured, §7/§10): **FICO** (numeric, authentic MNAR `-7/-8/-9`, native-missing →
  carve subset), **California** (numeric, `MedInc`), **Adult** (categorical `relationship` → needs the
  categorical scoring branch, see TODO), **Superconductivity** (numeric but very redundant → may be
  too easy).

## What did NOT work (do not repeat)

- **Downstream scoring for a band = weak lever.** A standardized linear (or any capable) downstream
  model **routes around** missing features using the rest → mean-fill ≈ oracle, no spread. Measured on
  Covertype (B0 panel, §12) and it's the §8 theorem (impute-then-predict is Bayes-optimal for any
  imputation with a strong learner). Only *maybe* works on a lean, low-redundancy dataset with one
  irreplaceable feature. **Prefer DIRECT scoring.**
- **Corrupt-not-delete** (inject wrong values instead of NaN): dropped — unrealistic, "cheaty", hard to
  engineer, non-scalable. **Stay with NaN deletion.**
- **Over-aggressive amputation → floor-collapse.** MNAR at high rate, or co-amputating a feature AND all
  its reconstructors, makes recovery impossible for everyone → no spread (both-ends-collapse, §3). Keep
  it recoverable (medium).
- **v1 static handshake leaked test features** to the agent (enabled overfitting-style peeking). Fixed:
  **always deferred (`train_at_grade=True`), test hidden (`peek_test=0`)**, grader re-runs code on the
  held-out test. Consequence: deliverables must be **0-row-safe** (sklearn `.transform` errors on 0
  rows) — the oracle and prompt already handle this.
- Agent-side observations (not rules): MICE-iteration and using labels did NOT help recovery; ensemble
  diversity + transductive train+test *feature* pooling did. (Pooling is features-only, no labels, not a
  leak — the agent never sees test; only its code does at grade.)

## Eval + resolution protocol

- **Model: biggie-max-polara ONLY**, agent-type `meteor`, machine `e2-custom-16-32768`, hosted (see
  CLAUDE.md). `horizon evaluations submit <task_id> --runs 5 --model biggie-max-polara --agent-type
  meteor --machine-type e2-custom-16-32768 --json`. Surface run + task links.
- `validate -a noop` must be 0; `-a oracle` grades a real score (hosted may show cosmetic **FAILED**
  because `best_observed=1` raw scores and oracle < 1 — check the log for `all checks passed`, not the
  verdict word).
- **The band** = the spread of scores across biggie's runs (each run is a different solution → real
  skill band, NOT noise). **Resolution:** σ is the SDK "sample" channel `√(v/N)` with N = amputed cells
  per column = `rate·N_test`, `v = (1−skill)²(κ_e−1)/4` (κ_e = per-cell error kurtosis ≈ 3–5); so
  σ ∝ 1/√(rate·N_test) and `tiers = 1 + width/(z√2σ)`. Covertype-direct: σ≈0.0038, ~10–12 levels.
  Scripts: `scratchpad/{panel_adversarial,tiers_direct}.py`. Extract submissions:
  `horizon rollouts pull <task_id>` → grade_result feedback `submission`.

## Gotchas

- figshare CDN blocked → vendor via ucimlrepo / OpenML, never `sklearn.fetch_*` that pull figshare.
- Encapsulation: truth + all labels live ONLY in `/data_root` (700); `/data_agent` (755) = corrupted
  features + train labels; prehook has a leak-guard. Never weaken this.
- Commit style: no em-dash, no "co-authored" line, logical commits. `scratchpad/` and `.horizon-local/`
  are gitignored. `sdk/` is a submodule.

## Open TODOs that unlock more task variety

- **Categorical direct-scoring branch in `verify.py`** — currently numeric NRMSE only. Add
  accuracy/macro-F1 for categorical target columns → unlocks categorical-imputation tasks (Adult
  `relationship`, Telco, Soybean).
- **Native-missing datasets** (FICO/NHANES): carve a complete subset in `setup_data`/vendor before
  amputating (need known truth).
- One vendor tool per new dataset (mirror `tools/vendor_covertype.py`).
- Optional: a `deferred`/rate-sweep helper to stamp out mechanism×rate task variants from one config.

## Pointers

- `readmes/README_general_direction.md` (§7 datasets, §10 recipe, §12 failures, §13 direct works),
  `readmes/README_building_the_world.md` (lifecycle/build), `readmes/README_submission.md` (submission
  table), `readmes/tasks/covertype-impute-direct.md` (the worked example + resolution math).
- Memory: `band-definition`, `downstream-metric-insensitivity`, `imputation-instrumental-literature`,
  `flagship-amputation-targets`, `world-v1-built`.
- Reference world: `../multimodal_fusion/` (submission/analysis structure, deferred pattern).
