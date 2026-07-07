# The two untouched knob-slots: categorical co-amputate (reasoning + eval strategy)

The only untouched slots in the 2×2³ grid are **Cat·Single·Yes** and **Cat·Multi·Yes** (categorical
co-amputate). Co-amputate = on the affected rows (chosen MAR by a numeric driver) delete the target(s)
AND their top reconstructor columns together; recover the target(s) from the weaker residual; score only
the target(s). Config-only on datasets we already have (Adult/Bank). Reasoning by two Opus subagents,
grounded in what we measured.

## What we measured (the priors)
- Categorical **single** (no-coamp) CONVERGES (one obvious classifier approach → shared MI ceiling;
  occupation ~0.24).
- Categorical **multi** (no-coamp) SPREADS — for a specific reason (below).
- Numeric co-amp is DATASET-DEPENDENT: California (fragile feature-combination) spread; Covertype
  (redundant residual) converged/floored. Removing signal helps only if the residual recovery is
  genuinely skill-dependent.
- Oracle/vet does NOT predict the band; only a real eval does.

## Decisive mechanism fact (checked in amputate.py)
- **MAR (no-coamp)** nulls each target column on an INDEPENDENT row draw → when one target is missing the
  OTHER targets are usually still OBSERVED. That co-observation of mutually-predictive targets
  (relationship↔marital↔sex) is exactly why Cat·Multi spread (exploiting it is optional → solutions vary).
- **co_amputate** draws the affected rows ONCE and nulls ALL targets + reconstructors on the SAME rows →
  on every scored row **all targets are missing together.** So **co-amp structurally removes the
  inter-target redundancy that made multi spread.** This cannot be preserved by reconstructor choice.

## Slot A — Cat·Single·Yes
**Base rate: converge/floor.** A single categorical target has one obvious approach; co-amp changes the
outcome only via the residual, which for most single targets is carried by ONE strong predictor (remove
it → floor) or a redundant alternative (→ converge). Spread must be engineered by choosing a target whose
post-removal recovery rests on a COMBINATION of weak signals (the California pattern).

**Best shot — Adult `relationship`, co-amputate `marital-status` + `sex`.**
- relationship base-recoverability ~0.65 (far from floor, headroom to harden). `marital-status` is its
  near-duplicate (Husband/Wife ⟺ Married) and `sex` makes Husband-vs-Wife deterministic — removing both
  caps the easy skill and forces the residual (age, income, capital-gain, hours, occupation,
  education-num) to do the work → a fragile weak-signal combination → the California spread signature.
- MAR driver `hours-per-week` (or `age` if too easy). Expected band ~0.25–0.45, ~3–5 levels.
- **Confidence it spreads: MEDIUM** (best structural match to the California pattern of any single
  categorical target). Risk: Husband/Wife collapse over-simplifies → converge; `age` alone saturates.
- **Hedge:** Bank `education`, co-amputate `job`. LOW–MED (job-carried → floor risk).

## Slot B — Cat·Multi·Yes
**Lean converge/narrow.** The multi band came from optional exploitation of co-observed sibling targets;
co-amp deletes that co-observation, leaving only recovery from residual observed non-target features (the
numeric-co-amp regime: dataset-dependent, narrow/floor-prone). The only surviving spread sources are (1)
an OBSERVED external anchor for the easy targets (Adult `sex`), and (2) optional MICE-style chaining
(impute anchor-recoverable targets first, feed into the hard one) — skill-dependent but weaker.

**Best shot — Adult, targets `[occupation, relationship, marital-status]`, co-amputate
`[education-num, education]` (DISJOINT; occupation's top predictors), keep `sex`/`age`/`workclass`/`hours`
observed.**
- Rationale: co-amputate only the HARDEST target's (occupation's) obvious predictors → occupation must be
  recovered indirectly (workclass/hours/capital-gain/age/sex + the imputed relationship/marital via
  chaining) = the skill-dependent variance source; keep `sex` observed so relationship/marital stay
  recoverable to a moderate non-floor level = floor insurance + headroom. Do NOT co-amputate sex/anchors
  (would floor the easy targets) and do NOT co-amputate a big block (Covertype "all-44 → floor" lesson).
- MAR driver `age`. **Confidence it spreads: LOW–MEDIUM** (converge/narrow is the single most likely
  result; this is the best minority shot).
- **Hedge (dial-back):** same targets, milder `reconstructor_cols = [education-num]` only. Run if the
  best-shot floors.

## OUTCOME (measured, 5 runs each, biggie-max-polara/meteor)

| task | design | band | levels | verdict |
|---|---|---|---|---|
| adult-impute-cat-coamp-single | relationship, co-amp marital+sex | 0.051–0.074 | 2.0 | ❌ FLOORED |
| bank-impute-cat-coamp-single | education, co-amp job | 0.000–0.010 | 1.3 | ❌ FLOORED |
| adult-impute-cat-coamp-multi | occ+rel+marital, co-amp educ-num+educ | 0.292–0.319 | ~3 | ❌ CONVERGED (over-hardened) |
| adult-impute-cat-coamp-multi-mild | occ+rel+marital, co-amp educ-num only | 0.293–0.368 | 4/7.2 | ✅ WORKS |

**Slot A — Cat·Single·Yes → SALVAGED (WORKS with the right target).** First attempts floored: relationship
K=6 (co-amp marital+sex) → 2 levels at ~0.06; education K=4 → ~0; and the follow-up bank job K=12 (co-amp
education) → ~0.065. Root cause diagnosed: each is carried by ONE strong predictor, so co-amputating it
collapses to naive. **Salvage (high-cardinality, distributed-predictor target): occupation K=14, co-amp
educ+educ-num → 0.091–0.168, 3 realized levels / capacity 8 → WORKS** (adult-impute-cat-coamp-single-occ,
eval 56635973). So the floor was a target-choice artifact (low-card single-carrier), not a slot property —
matching the original high-cardinality guidance. Target-specific, not dataset-specific: bank job floored
because education is its single carrier; a distributed-predictor Bank target was not found/tried. Absolute
scores are low, but it is a real multi-level spread. Discriminating skill (5-solution analysis, eval
56635973): regularization/averaging depth, NOT estimator family — a single deep HGB overfits the 14-class
target (0.091), shallow regularized ensembles or a bagged RandomForest reach 0.168. (Different axis than the
mild-multi, where estimator family drove it.) Reconstructing education first is a red herring: occupation
never consumes the co-amputated education columns, so imputing them adds nothing.

**Slot B — Cat·Multi·Yes → WORKS, via the dial-back.** Prediction was LOW–MED, and the mechanism reasoning
held: the aggressive best-shot (co-amp BOTH occupation predictors) over-hardened → converged ~0.30 (3
levels). The mild hedge (co-amp educ-num only, keep educ as an observed anchor) SPREAD 0.29–0.37, 4/7.2
levels. So the slot works, and the lesson is **hardening is a dial, not a switch**: keep one strong
reconstructor observed as a floor-anchor for the easy targets, remove the other → the hard target's
indirect recovery + optional MICE chaining supplies the skill variance. The hedge design was the winner,
not the best-shot; building both was the right call.

## Eval strategy (how we learn if they work)
Per the eval-directly flow (no classifier vet):
1. **Build both best-shots** (config-only on Adult; the categorical scorer + co_amputate engine already
   exist): `adult-impute-cat-coamp-single` (relationship, recon marital-status+sex) and
   `adult-impute-cat-coamp-multi` (occ+rel+marital, recon education-num+education).
2. **Floor-check hosted** with `validate -a noop` (build) — no oracle. (A quick oracle-validate on a
   throwaway is optional to catch a hard floor, but oracle doesn't predict the band, so we mostly rely on
   the eval.)
3. **Eval-directly, 7 runs each** (biggie-max-polara/meteor). Read band + levels-in-band (offline LSD).
4. **Branch on the result:** if a slot SPREADS → WORKS, done. If it FLOORS → run the dial-back hedge
   (single: Bank education; multi: [education-num]-only). If it CONVERGES high (trivial) → the slot is a
   measured dead-end for categorical (record it, like Covertype numeric co-amp).
5. Cost: 2 tasks × 7 runs = 14 runs (up to +14 if both need hedges). Both are honestly LOW–MED to MED
   confidence — we expect at least one to be marginal; the value is *knowing*, and filling the last grid
   slots either as WORKS or as documented dead-ends.
