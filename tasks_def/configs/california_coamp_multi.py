"""California co-amputate MULTI (grid slot 4 realized on California, Numeric·Multi·CoAmp).

Amputate `median_income` + `population`, and also delete their key reconstructors
(`households`, `total_bedrooms`) on the affected rows. Vetting (`scratchpad/vet_coamp.py`) shows this
drops oracle recovery to ~0.08 (near-floor; California's signal is a fragile feature combination). Built
to confirm with real runs; expected a narrow/near-floored band.
"""
from tasks_def.configs import california_direct as _base

CONFIG: dict = {
    **_base.CONFIG,
    "mechanism":         "co_amputate",
    "target_cols":       ["median_income", "population"],
    "reconstructor_cols": ["households", "total_bedrooms"],
    "hints": [
        "Missing cells are NaN. On the affected rows some columns that would help predict the targets "
        "may ALSO be missing, so simple correlations may not be available.",
        "Only the originally-missing target cells are scored, against the true values; recover them as "
        "accurately as you can from whatever signal remains.",
    ],
}
