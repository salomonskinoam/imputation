# Strategy analysis — covertype-impute-direct, 5 runs (eval c56b6c86)

biggie-max-polara, 5 runs. Task: recover 3 NaN'd continuous columns (0 Elevation, 5 Dist-to-Roadways,
9 Dist-to-Firepoints) in Covertype under MAR; score = mean over amputed cols of
`1 − RMSE(method)/RMSE(mean-fill)` on the held-out test. Per-run code: `runN_<score>.py`.

## Band and the axes that move it

Hosted band (worst→best): **0.271 · 0.299 · 0.301 · 0.377 · 0.385**. Multi-axis: the runs vary on model
family/ensemble, iteration scheme, label use, and pooling, and the band splits cleanly into a top pair
(~0.38) and a bottom trio (~0.27–0.30).

| rank | run | score | model / ensemble | pool train+test? | iteration | uses label | feature-eng |
|---|---|---|---|---|---|---|---|
| 1 | 2 | **0.385** | HGB×2 (diff leaves/L2) + RandomForest, averaged | YES (`concatenate`) | single-pass | no | none |
| 2 | 1 | 0.377 | ExtraTrees + RF + HGB, weighted 0.5/0.25/0.25 | YES (`vstack`) | single sweep (ordered) | no | none |
| 3 | 4 | 0.301 | single HGB + HGB **classifier** for label probs | YES (`concatenate`) | MICE 6-iter | **yes** (one-hot train + predicted test class-probs) | none |
| 4 | 3 | 0.299 | single HGB | YES (`vstack`) | MICE 5-iter | no | none |
| 5 | 5 | 0.271 | HGB×5 seeds, averaged | **NO (inductive)** | single-pass | yes (label col; NaN for test) | none |

## What sorts this band (different from California)

Unlike California, pooling does NOT sort this band — 4 of the 5 pool train+test features. The movers here:

- **Diverse multi-family ensembling wins the top.** The top two average *different model families*
  (run2: HGB×2 + RandomForest; run1: ExtraTrees + RF + HGB). The bottom three all lean on a single
  family (single HGB, or HGB seed-averaging — run5). With 3 target columns of differing difficulty,
  model diversity buys more than depth of iteration.
- **Single-pass beat MICE.** Both top runs impute in one sweep (run1 explicitly: "more sweeps actually
  hurt slightly in CV"). The two MICE runs (run3 5-iter, run4 6-iter) sit in the bottom trio — iterating
  a strong regressor over already-strong features adds error here.
- **Labels didn't help.** The two label-users (run4 via a per-iteration classifier's test class-probs;
  run5 via a raw label column) are ranked 3rd and last. The cartographic features already carry the
  signal; the label block adds noise/complexity.
- **Inductive is the floor.** run5 is the only run that fits on train rows only (no test pooling) and it
  scores lowest — pooling still matters at the margin, it just isn't the dominant sorter here.

## Contrast with california-impute-direct

Same task engine, different dominant axis — evidence the world discriminates on genuine imputation
craft rather than one exploit:

- **California** (single target, ~50% missing): **pooling dominates** (fit-row count is the lever);
  simplicity is the tiebreak among poolers.
- **Covertype** (3 targets, mixed difficulty): **ensemble diversity + single-pass dominate**; pooling is
  near-universal so it only separates the inductive floor.

Both agree on the negatives: **MICE over-iteration and using the label are neutral-to-harmful.**

## Resolution

`scratchpad/tiers_direct.py`: bootstrap test rows for σ. Band 0.27–0.39 (width ~0.11); realized
separable levels ~4/5 (adjacent flip-rate check). See `readmes/tasks/covertype-impute-direct.md`.
