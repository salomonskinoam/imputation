"""Build the task prompt from the merged config. Two modes (cfg.scoring_mode):

- "downstream": neutral/unaware framing — "produce model-ready features", scored by a fixed linear
  classifier. Does NOT name imputation (the student discovers the data needs cleaning).
- "direct": names the goal — recover the missing values; scored by recovery accuracy vs truth.

Both use the DEFERRED handshake: the student gets the full training data + a shape-only test
placeholder, writes a `solution.py`, and the grader re-runs it on the full held-out test at grade.
"""
from __future__ import annotations

import re
import tomllib
from pathlib import Path

from sdk.path_mappings import CONTAINER_DATA_AGENT, CONTAINER_WORKDIR

_INTRO = {
    "downstream": "Build a feature pipeline that turns the rows into model-ready feature vectors.",
    "direct": ("Some feature values are missing (NaN). Build a pipeline that RECOVERS them as "
               "accurately as possible."),
}

_SCORED = {
    "downstream": (
        "Your processed features are fed to a FIXED multinomial logistic-regression classifier: the\n"
        "grader fits it on your processed train features + the train labels, then predicts your\n"
        "processed test features. Your score is macro-F1 on the held-out test labels (never provided).\n"
        "Make the features as predictive as possible under that fixed linear classifier."),
    "direct": (
        "For the held-out TEST rows, your recovered values at the missing cells are compared to the\n"
        "true values. Score = how much you reduce the error versus a naive mean-fill, averaged over\n"
        "the affected columns: 0 = no better than filling the column mean, 1 = perfect recovery.\n"
        "Only the originally-missing cells are scored; leave the observed values as they are."),
}

_TEMPLATE = """\
You are given a sample of data for the task: {task_description}. {intro}

## Data

All arrays live under {data_dir}/ as NumPy .npy files (2-D: rows = examples, columns = features):
- train_features.npy  ({n_train}, {n_features})  and  train_labels.npy  (integer class ids 0..{km1}: {classes})
- test_features.npy — a SHAPE-ONLY placeholder during development (0 rows). At grade time your script
  is re-run with the full held-out test ({n_test} rows) in its place. You never see the real test;
  do NOT hardcode row counts — read however many rows are present, and handle 0 test rows gracefully
  (e.g. skip transforming an empty test array; it is re-run on the full test at grade).
{data_dir}/meta.json lists the feature names and the full counts.

## How you are scored

{scored_block}

## Deliverable

Write a Python script to {script_path}. It must read {data_dir}/ and write two arrays:
- {train_out}: processed train features, shape (n_train, {n_features}), every value finite (no NaN)
- {test_out}:  processed test features,  shape (n_test, {n_features}),  every value finite

Your script is run by the grader as `python solution.py` from /workdir on the FULL data (the hidden
test is in place then), so read the row counts at runtime — do NOT hardcode them. Keep the same
{n_features} columns in the same order. Only /workdir is writeable.

## Environment

{environment_info}
{hints}\
"""


class PromptBuilder:
    def __init__(self, cfg, source_dir: Path) -> None:
        self.cfg = cfg
        self.source_dir = Path(source_dir)

    @property
    def environment_info(self) -> str:
        toml_path = self.source_dir / "src" / "venvs" / "pyproject.toml"
        with open(toml_path, "rb") as f:
            data = tomllib.load(f)
        deps = data["dependency-groups"]["model"]
        packages = [re.split(r"[>=<!;\[]", d)[0].strip() for d in deps if isinstance(d, str)]
        return (f"- Python: /venvs/model_venv/bin/python\n"
                f"          Packages: {', '.join(packages)}\n"
                f"          Internet is blocked. pip installs will fail.")

    @property
    def hints(self) -> str:
        if not getattr(self.cfg, "hints", None):
            return ""
        lines = "\n".join(f"- {h}" for h in self.cfg.hints)
        return f"\n## Hints\n\nYou might try any, none, or several of these:\n{lines}\n"

    def build(self) -> str:
        mode = getattr(self.cfg, "scoring_mode", "downstream")
        n_features = getattr(self.cfg, "n_features", 54)
        classes = ", ".join(f"{i}={c}" for i, c in enumerate(self.cfg.class_names))
        return _TEMPLATE.format(
            task_description=self.cfg.task_description,
            intro=_INTRO[mode],
            scored_block=_SCORED[mode],
            data_dir=str(CONTAINER_DATA_AGENT / self.cfg.data_rel),
            n_train=self.cfg.n_train, n_test=self.cfg.n_test, n_features=n_features,
            km1=self.cfg.n_classes - 1, classes=classes,
            script_path=str(CONTAINER_WORKDIR / self.cfg.script_rel),
            train_out=str(CONTAINER_WORKDIR / self.cfg.train_imputed_rel),
            test_out=str(CONTAINER_WORKDIR / self.cfg.test_imputed_rel),
            environment_info=self.environment_info,
            hints=self.hints,
        )
