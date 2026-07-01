# Building the imputation world (running doc)

**Status: running design doc. Discard after the world is built.** Working scratchpad for turning the
direction ([README_general_direction.md](README_general_direction.md)) into a concrete SDK world.
Decisions at top; the design is now **measured/validated**, not assumed. SDK guide:
[../sdk/CREATING_A_WORLD.md](../sdk/CREATING_A_WORLD.md). Clone structure from `../multimodal_fusion/` (§7).

---

## 1. Locked design (measured)

- **Flagship dataset = Covertype** (UCI id=31). Complete tabular, 7-class cover type, a dominant
  numeric signal feature (`Elevation`). Not implied — this is the choice.
- **Core mechanism = controlled weak downstream model.** The literature ([README_general_direction.md](README_general_direction.md) §8 + memory) proves impute-then-predict with a *powerful* learner
  is Bayes-optimal for almost any imputation → downstream is insensitive. So the grader, not the
  student, owns a **frozen weak model**; the student only produces model-ready features. This is what
  makes imputation instrumental.
- **Grading = downstream macro-F1 only** (direct cell-recovery is NOT implemented — see §6 note).
- **Zero preprocessing** of features besides amputation (student sees raw values minus amputed cells;
  the frozen model runs on raw features — raw, unscaled actually *widens* the band, measured §3).
- **Per-task config** (like fusion): shared `config_world.py` + `tasks_def/configs/<task>.py`.
- **The measured band** (proof the design works, §3): lazy mean-fill 0.25 → strong imputer 0.37 →
  oracle 0.43 macro-F1; a monotone 0.118 skill spread across realistic solutions.

## 2. The corruption config (measured constants)

All values below were calibrated by experiment (§3), not guessed. Each has a role and a known
failure mode if pushed too far.

| Knob | Locked value | What it does (band lever) | Failure mode if pushed |
|---|---|---|---|
| Frozen downstream model | multinomial **logistic regression, RAW features** (no scaling), C=1.0, max_iter=3000 | weak model can't self-heal → imputation quality propagates to score; raw/unscaled widens the band | too strong (GBM) → routes around → band ≈ 0 |
| Mechanism | **MAR** — P(missing) rises with an *observed* driver col (`Slope`) | keeps the target's full value range observable → strong imputers can recover → skill separates | **MNAR self-mask removes the range → recovery & band collapse** (measured: MNAR-0.7 skill-gap −0.01) |
| Rate | **0.5** of the target columns | enough bias to sink mean-fill | too high → even strong imputers can't recover → collapse |
| Target columns (amputed) | `Elevation`, `Horizontal_Distance_To_Roadways`, `Horizontal_Distance_To_Fire_Points` (top-3 MI) | remove carried signal so lazy fill loses it | amputing everything → no signal left → floor collapse |
| Protected columns (kept intact) | `Hillshade_*`, `Slope`, `Aspect`, Hydrology distances | **the recovery path** — reconstructors stay observed so skill can recover the amputed cells | amputing these too → nobody recovers → collapse |
| Train size | ~5,000 (small) | keeps the weak end-model from routing around the amputed feature (more train → it self-heals → band collapses) | too large → band shrinks |
| Test size | ~30,000+ (large) | sets RESOLUTION: σ∝1/√N_test so separable tiers∝√N_test (measured 5.6→9.4→15.9 tiers at N_test=3k→10k→30k); free here (Covertype 581k rows) | too small → few resolvable tiers |
| Apply to | **train + test** | the deployed pipeline must impute at inference too | — |
| Metric | macro-F1 (7-class) | — | — |

## 3. The validation (why we believe there's a band)

Measured on Covertype (6k rows, frozen raw logistic), macro-F1 across the solution ladder:

| Config | mean (lazy) | KNN | MICE-linear | MICE-HGB (strong) | oracle | skill band |
|---|---|---|---|---|---|---|
| **MAR rate 0.5 (LOCKED)** | 0.253 | 0.271 | 0.282 | **0.371** | 0.425 | **0.118** (monotone) |
| MAR rate 0.3 | 0.308 | 0.328 | 0.338 | 0.376 | 0.425 | 0.068 |
| MNAR rate 0.3 | 0.356 | 0.361 | 0.402 | 0.380 | 0.425 | 0.046 (non-monotone) |
| MNAR rate 0.7 | 0.354 | — | 0.344 | 0.344 | 0.425 | ≈0 (collapsed) |

Takeaways that shaped the lock: (a) **weak frozen model is essential** — with a strong model the gap
is ~0; (b) **raw beats standardized** (standardizing the frozen model collapsed the skill-gap to
~0–0.02); (c) **MAR ≫ MNAR** for the band because MAR preserves recoverability; (d) **rate 0.5 > 0.3**
for MAR; (e) imputation *skill* matters a lot — linear-MICE→HGB-MICE alone is +0.089.

### Resolution & the end-model choice (measured via SDK noise_floor §12/§14)

Bootstrapping the test set gives σ (resampling noise) → `LSD = z√2·σ` → separable `tiers = 1 + width/LSD`:
- **raw logistic** (LOCKED): band 0.22→0.42, σ=0.019 at N_test=3.2k → **3 separable tiers**, clean monotone
  order (lazy fills < strong imputer < oracle). With **N_test=30k → all 5 tiers resolve** (σ=0.005).
- **MLP(128,64)** (REJECTED): higher absolute ceiling (~0.56) but band collapses to **2 tiers and the
  realistic imputers mis-order** (KNN<mean, MICE-lin≈MICE-HGB) — added capacity lets it route around.
- **accuracy metric** (REJECTED): 0.7+ ceiling but band ≈0 (majority-dominated; hides the elevation
  signal that lives in minority classes). Use macro-F1.

Decision: **frozen raw multinomial logistic + macro-F1 + small train (~5k) + large test (~30k+)**.
Absolute ceiling (~0.42) is cosmetic — the world normalizes scores; what matters is the resolvable
tiers, which raw-logit maximizes and test-size dials up.

## 4. World package layout (to create)

```
worlds/imputation/
  __init__.py  world.py  config_world.py  paths.py  objective.py  verify.py
  prompt_builder.py  prehook.py  setup_data.py  amputate.py  studentview.py  Dockerfile
tasks_def/
  __init__.py  covertype.py  configs/{__init__.py,covertype.py}
tasks/covertype-impute/   # apex shims: task.yaml grader.py setup.sh solution.sh .dockerignore
  src/pre_build/check_build.py  src/venvs/{pyproject.toml,uv.lock}  tests/README.txt
hor.py               # copy verbatim from fusion
```

## 5. Data pipeline & encapsulation

- **Vendoring** (`setup_data.py`, build-time): fetch Covertype via ucimlrepo (figshare CDN blocked —
  do NOT use sklearn fetchers that pull from it), subsample, freeze a versioned snapshot.
- **Amputation** (`amputate.py`): dataset-agnostic, seeded, config-driven (mechanism/rate/target/
  protected cols). MAR driver + targets from config. Emits the corrupted student view; grader keeps
  the true values + labels.
- **StudentView** (`studentview.py`): builds agent-visible corrupted data; reused by deferred-mode
  `stage_inputs()`.
- **Deliverable**: student outputs model-ready feature matrices for train + test (values only — **no
  mask column**, raw schema enforced). Student does NOT train the classifier.
- **Encapsulation**: true values + labels grader-only (700 dirs); student sees only the corrupted
  view (`/data_agent`, 755) + post-write leak guard.

## 6. verify.py / scoring contract

- Read merged config from `CONTAINER_ACTIVE_CONFIG`; resolve via `objective.py`.
- Fit the **frozen logistic model** on (student's imputed train features, grader-only train labels),
  predict student's imputed test features, score **macro-F1** → normalize (mean-fill→0,
  best_observed→1) → write `{primary, score, reason}` to `bench_result_path`. Gates: artifact present,
  schema valid (no extra/mask columns), beats mean-fill baseline. Keep `grade()` < 600s.
- NOTE (direct cell-recovery, NOT implemented): one could also grade NRMSE of recovered cells vs
  truth. We dropped it — the downstream metric is the graded signal. Kept here only as a reference.

## 7. Files to copy/adapt from `../multimodal_fusion/`

`worlds/fusion/world.py` (HorTask overrides, `dockerfile_template`, deferred `_produce`,
`stage_inputs`), `prompt_builder.py`, `paths.py`, `config_world.py`, `verify.py`, `setup_data.py`,
`projection.py`→`studentview.py`, `upload_probe.py`; `tasks_def/*`; `tasks/<task>/{grader.py,
setup.sh,task.yaml}`; `Dockerfile`; root `hor.py`.

## 8. Build checklist (ordered)

1. [x] Flagship = Covertype; framing = unaware; **corruption config calibrated & band proven** (§3).
2. [ ] Scaffold `worlds/imputation/` + `hor.py` by copying fusion and renaming.
3. [ ] `setup_data.py`: vendor Covertype, freeze snapshot.
4. [ ] `amputate.py` + `studentview.py`: config-driven MAR amputation; corrupted view + truth.
5. [ ] `config_world.py` + `tasks_def/configs/covertype.py`: model, mechanism=MAR, rate=0.5, target/
       protected cols, metric.
6. [ ] `verify.py`: frozen logistic macro-F1 → `{primary,score,reason}`; gates incl. no-mask schema.
7. [ ] `prompt_builder.py` (neutral/unaware prompt), `prehook.py`, `Dockerfile`.
8. [ ] Degenerate `solution.sh`; `python hor.py validate <task> -a noop` → 0; oracle/strong-impute → high.
9. [ ] Re-measure the band in-world; confirm it matches §3.

## 9. Resolved decisions

- Flagship → Covertype. Framing → unaware (neutral "produce model-ready features" prompt).
- Downstream → frozen weak logistic; student produces features, doesn't train the classifier.
- Mechanism/rate → MAR / 0.5 (measured). Preprocessing → none. Mask → withheld.
- Direct cell-recovery → not implemented (docs-only).
- Per-task config → yes (`config_world.py` + `tasks_def/configs/<task>.py`).

## 10. Pointers

- Direction + measured tables: [README_general_direction.md](README_general_direction.md)
- Proposal: [imputation_proposal.md](imputation_proposal.md)
- SDK guide: [../sdk/CREATING_A_WORLD.md](../sdk/CREATING_A_WORLD.md)
- Reference world + deeper notes: `../multimodal_fusion/` and its `imputation_world.md`
- Throwaway measurement scripts: session scratchpad (`analyze.py`, `concentration.py`, `sweep.py`, `ladder.py`).
