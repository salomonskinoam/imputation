"""Band-resolution submission docs for the imputation world (static / no-predictions mode).

Regenerates, for every task in `tasks_def/band_manifest.py`, the SDK two-file record:
  - `readmes/tasks/<task>.md`         (per-task record, via sdk.hor_utils.band_report.render_record)
  - a row in `readmes/README_submission.md` master table (upserted, one per task)
  - a slim `analysis/<eval8>/band_supports.json` durable record.

Unlike the classification engine (`budgeted/scratch/analysis/band_resolution.py`) this needs NO stored
per-cell predictions and NO re-execution: the band comes from the inlined run SCORES, and the noise floor
(sigma_abs -> LSD -> #band_supports) comes from a STATIC offline resolution model (a task property from the
committed npz: N = rate*n_test scored cells + per-target class/dispersion structure). sigma is therefore an
estimate, recorded verbatim in `sigma_source`; it upgrades to a prediction-resample sigma once a task is
re-evaluated with a predictions-persisting grader (see worlds/imputation/verify.py).

Metrics + decision rule follow the horizon-band-verdict skill: report SPREAD + #band_supports (never
mean/std); #band_supports >= 3 -> viable, <= 2 -> reject; runs at/below FLOOR are degenerate.

  python tools/band_report_impute.py            # compute + print all
  python tools/band_report_impute.py --emit     # + write records and upsert master-table rows
  python tools/band_report_impute.py --validate  # check the row<->record invariant (SDK)
"""
from __future__ import annotations
import importlib
import json
import math
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from sdk.hor_utils.band_report import BandReport, render_record, render_row, validate  # noqa: E402
from sdk.hor_utils.resolution import resolution  # noqa: E402
from tasks_def.band_manifest import MANIFEST  # noqa: E402

# ONE grid-arranged master table: the SDK 8-col block (task first, so band_report.validate still keys on
# it) with the 4 binary knob columns appended (they cannot precede the SDK block, whose validator reads
# fixed positions 4/6/7). Rows are sorted by the binary grid so scanning down is the 2x2^3 counting.
TABLE_HEADER = ("| task | metric | band | spread | #obs / #supports | verdict | submit | links "
                "| type | #cols | co-amp | dataset |")
TABLE_SEP = "|" + "---|" * 12
_TYPE = {"num": 0, "cat": 1}
_COLS = {"single": 0, "multi": 1}
_COAMP = {"no": 0, "yes": 1}
_DSET = {"california": 0, "covertype": 1, "adult": 0, "bank": 1}


def _slot_parts(slot):
    """('num','single','no','california') from 'num/single/no/california'; None if not a clean grid slot."""
    p = slot.split("/")
    if len(p) == 4 and "(" not in slot:
        return p[0], p[1], p[2], p[3].strip()
    return None


def _grid_key(slot):
    p = _slot_parts(slot)
    if not p:
        return (1, slot)   # superseded / extra rows sort after the 16 clean grid cells, alphabetically
    t, c, a, d = p
    return (0, _TYPE.get(t, 9), _COLS.get(c, 9), _COAMP.get(a, 9), _DSET.get(d, 9))


def _knob_cells(slot):
    p = _slot_parts(slot)
    if not p:
        # keep the coordinate visible for extras (e.g. 'cat/single/yes/adult (superseded)')
        raw = slot.split("/")
        raw += [""] * (4 - len(raw))
        cap = {"num": "Num", "cat": "Cat", "single": "Single", "multi": "Multi", "no": "No", "yes": "Yes"}
        return " " + " | ".join(cap.get(x.strip(), x.strip()) for x in raw[:4]) + " |"
    t, c, a, d = p
    cap = {"num": "Num", "cat": "Cat", "single": "Single", "multi": "Multi", "no": "No", "yes": "Yes"}
    return f" {cap[t]} | {cap[c]} | {cap[a]} | {d} |"


def _rewrite_table(path, body):
    """Replace the master table block (the '| task ...' header + separator + its contiguous data rows)
    with `body`, preserving all surrounding prose. Idempotent."""
    lines = path.read_text().splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.lstrip().lower().startswith("| task"))
    end = start
    while end < len(lines) and lines[end].lstrip().startswith("|"):
        end += 1
    path.write_text("\n".join(lines[:start] + body + lines[end:]) + "\n")

Z = 2.0
FLOOR = 0.02      # imputation skill is baseline-relative (0 = naive); only ~0 runs are degenerate
CEILING = 0.97


def _cfg(mod_name):
    return importlib.import_module(mod_name).CONFIG


def _target_sigmas(cfg, mid):
    """Static per-target-column absolute sigma of the recovery skill, from the committed npz.

    categorical: err_naive = 1 - mode_freq; SE(err_method) ~ sqrt(en(1-en)/N) at the naive operating
                 point -> sigma_skill = sqrt(en(1-en)) / (en*sqrt(N)).
    numeric:     skill = 1 - rmse_m/rmse_n; SE(rmse_m) ~ rmse_m/sqrt(2N) -> sigma_skill ~ (1-mid)/sqrt(2N).
    N = rate*n_test scored cells per target column.
    """
    z = np.load(REPO / cfg["npz_name"] if (REPO / cfg["npz_name"]).exists()
                else REPO / "worlds/imputation/data" / cfg["npz_name"], allow_pickle=True)
    names = [str(s) for s in z["feature_names"].tolist()]
    X = z["features"]
    N = max(1, int(cfg["rate"] * cfg["n_test"]))
    cats = set(cfg.get("categorical_cols") or [])
    sigs = []
    for c in cfg["target_cols"]:
        if c in cats:
            y = X[:, names.index(c)].astype(int)
            en = 1.0 - np.bincount(y).max() / len(y)
            sigs.append(math.sqrt(en * (1 - en)) / (en * math.sqrt(N)) if en > 1e-9 else 0.0)
        else:
            sigs.append((1.0 - mid) / math.sqrt(2 * N))
    return sigs, N


def _observed_levels(scores, lsd):
    """Tiers the runs actually occupy: greedy clusters separated by more than one LSD."""
    s = sorted(scores)
    if lsd <= 0:
        return len(set(s))
    levels, anchor = 1, s[0]
    for x in s[1:]:
        if x - anchor > lsd:
            levels += 1
            anchor = x
    return levels


def analyze(task, spec):
    cfg = _cfg(spec["cfg"])
    all_scores = [float(x) for x in spec["scores"]]
    nd = [s for s in all_scores if s > FLOOR]
    degenerate = len(nd) < 2
    band_scores = nd if not degenerate else all_scores
    lo, hi = float(min(band_scores)), float(max(band_scores))
    width, mid = hi - lo, (hi + lo) / 2.0

    sigs, N = _target_sigmas(cfg, mid if mid > 0 else 0.5)
    sigma_abs = math.sqrt(sum(x * x for x in sigs)) / len(sigs)
    ceiling = hi >= CEILING or sigma_abs == 0.0 or len(set(band_scores)) < 2

    if ceiling:
        band_supports, lsd = None, Z * math.sqrt(2) * sigma_abs
    else:
        res = resolution(band_scores, sigma_rel=sigma_abs / mid, z=Z)
        band_supports, lsd = float(res["tiers"]), float(res["lsd"])
    observed = _observed_levels(band_scores, lsd if lsd else 0.0)

    # Verdict leads with REALIZED spread (observable), not the sampling-noise capacity (which the static
    # ruler inflates); #band_supports is shown as the capacity ceiling in the table's #obs/#supports cell.
    if degenerate:
        auto_verdict, auto_submit = "FLOORED (runs at the naive baseline)", "NO (floored)"
    elif ceiling:
        auto_verdict, auto_submit = "CEILING (Method B invalid; needs the gap test)", "NO"
    elif observed >= 3 and band_supports >= 3.0:
        auto_verdict = f"viable: {observed} distinct tiers realized over spread {width:.2f} (capacity {band_supports:.1f})"
        auto_submit = "**YES**"
    else:
        auto_verdict = f"below the bar: {observed} tiers realized, spread {width:.2f} (capacity {band_supports:.1f})"
        auto_submit = "NO"

    return dict(
        task=task, metric="recovery",
        band=[lo, hi], band_note=spec.get("band_note", ""), width=width, mid=mid,
        scores_sorted=[round(s, 4) for s in sorted(band_scores)],
        sigma_abs=sigma_abs, lsd=lsd, band_supports=band_supports, n_observed=observed,
        ceiling=bool(ceiling), gap={},
        sigma_source=(f"static offline resolution: N={N} scored cells/target (rate*n_test) + per-target "
                      "class/dispersion structure; NO prediction resample"),
        n_runs=len(all_scores), n_nondegenerate=len(nd), n_failed=0,
        n_test=0, n_classes=0,
        verdict=spec.get("verdict_line", auto_verdict), submit=spec.get("submit", auto_submit),
        eval=spec.get("eval", ""),
    )


def to_band_report(spec, r):
    d = dict(r)
    ev = r["eval"]
    d.update(dict(
        band_supports=None if r["ceiling"] else r["band_supports"],
        observed=r["n_observed"],
        verdict_line=r["verdict"], submit=r["submit"], narrative=spec.get("narrative", {}),
        links=dict(task_url=spec.get("task_url", ""),
                   evals=[{"label": lbl, "url": url} for lbl, url in spec.get("evals", [])],
                   record=f"tasks/{r['task']}.md",
                   source_json=(f"analysis/{ev}/band_supports.json" if ev else "")),
    ))
    return BandReport.from_dict(d)


def main(argv):
    args = argv[1:]
    if "--validate" in args:
        probs = validate(REPO / "readmes/README_submission.md", REPO / "readmes/tasks")
        for pr in probs:
            print(f"[{pr.kind}] {pr.task}: {pr.detail}")
        print(f"{len(probs)} problem(s)." if probs else "invariant OK (row <-> record bijection holds).")
        return 1 if any(pr.kind != "polarity_advisory" for pr in probs) else 0

    emit = "--emit" in args
    keys = [a for a in args if not a.startswith("--")] or list(MANIFEST)
    rows = []  # (grid_key, rendered_table_row) for the one merged table
    for task in keys:
        spec = MANIFEST[task]
        r = analyze(task, spec)
        if r["eval"]:
            out = REPO / "analysis" / r["eval"]
            out.mkdir(parents=True, exist_ok=True)
            (out / "band_supports.json").write_text(json.dumps(r, indent=2))
        if emit:
            report = to_band_report(spec, r)
            (REPO / "readmes/tasks" / f"{r['task']}.md").write_text(render_record(report))
            rows.append((_grid_key(spec.get("slot", "")),
                         render_row(report) + _knob_cells(spec.get("slot", ""))))
    if emit and keys == list(MANIFEST):   # full run -> rewrite the single grid-sorted master table in place
        body = [TABLE_HEADER, TABLE_SEP] + [row for _, row in sorted(rows, key=lambda x: x[0])]
        _rewrite_table(REPO / "readmes/README_submission.md", body)
        bs = "ceiling" if r["ceiling"] else ("degenerate" if r["band_supports"] is None else f"{r['band_supports']:.2f}")
        print(f"{task:36s} band {r['band'][0]:.3f}-{r['band'][1]:.3f} w={r['width']:.3f} "
              f"sig={r['sigma_abs']:.4f} LSD={r['lsd']:.4f} #obs={r['n_observed']} "
              f"#supports={bs:>7s}  {r['submit']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
