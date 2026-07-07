# Imputation world, proposal

A world of tasks where the student builds a model/code that predicts well on unseen data when
the data it learns from has missing or corrupted values. Recovering/handling those values is the
means, not the graded end: the task succeeds only if the downstream prediction is good.

This is a directional doc, the why and the constraints, to bootstrap a new world repo. Specific
datasets, exact metrics, and final wording are decided later, inside the world.

## Why this world
There are many genuinely different ways to handle missing/corrupted data (simple fills,
conditional models, neighbor methods, low-rank completion, tree-based, generative), and no single
one wins across datasets; the best approach flips with the data and with how the values went bad.
So agents try different methods and scores spread without us forcing it. We engineer the
difficulty (and the spread) by HOW we remove or corrupt the data.

## The prompt (parameterized)
> You are given a sample dataset {{dataset_sample}} {{maybe disclose that some values are missing
> or corrupted}} and an objective {{downstream_objective}} with metric {{metric}}. I want you to
> create {{code/model}} that given new unseen data similar to the one you have seen, is able to
> predict the {{label(s)}}.
> Deliverable: {{artifact}}

What gets parameterized: the type of amputation/corruption, the base dataset, the metric(s), the
mode (agent-time vs deferred/grader-time), and optionally whether we disclose that values are
missing/corrupted (so the student may have to discover it).

## The task must be instrumental
Graded on the downstream prediction on unseen data, not on cell-recovery in a vacuum. A task must
FAIL with bad handling of the missing/corrupted data and SUCCEED with good. A solution that does
not beat the trivial baseline (naive fill) scores zero.

## Data
REAL data only, never synthetic. Difficulty and structure are engineered on top of real data via
the amputation/corruption (which values, which mechanism, what rate). A good instance: the trivial
baseline is far from achievable and no single method is pre-determined to win. Which datasets:
chosen later, inside the world.

## Modes and the graded artifact
Default is agent-time (the student builds/iterates during the rollout). A deferred / grader-time
mode (train-at-grade) is added later, as in the fusion environment. The graded artifact is the
SAME across both modes so the switch is seamless.

## The band is the goal
The main design work is choosing HOW to remove/corrupt data so strong and weak solutions land at
clearly different scores (a wide band). Light random masking makes methods converge (narrow,
boring); harder mechanisms, higher rates, and correlated columns separate skill. The first thing to
do after building is measure that spread.

## Reward hacking
Keep the held-out truth grader-only (never agent-visible); choose the removal/metric so the trivial
baseline cannot win; standard encapsulation against leakage / forbidden-dir reads.

## Constraints
CPU-only for now.

## Building it
Build this as an SDK world (a `worlds/<world>/` subclass plus task instances). See
`CREATING_A_WORLD.md` in the SDK.
