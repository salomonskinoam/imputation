"""California co-amputate SINGLE (grid slot 2, Numeric·Single·CoAmp).

Same as california_direct but the amputation also deletes `median_income`'s key reconstructor
(`total_rooms`) on the affected rows, so the direct recovery path is gone. Vetting
(`scratchpad/vet_coamp.py`) shows California income is a fragile feature *combination* (rooms/household
ratio) with no single strong predictor, so removing a ratio component collapses oracle recovery to ~0
(floor). Built anyway to confirm the collapse with real runs; expected to be a floored/near-floored band.
"""
from tasks_def.configs import california_direct as _base

CONFIG: dict = {
    **_base.CONFIG,
    "mechanism":         "co_amputate",
    "target_cols":       ["median_income"],
    "reconstructor_cols": ["total_rooms"],
    "hints": [
        "Missing cells are NaN. On the affected rows some columns that would help predict the target "
        "may ALSO be missing, so simple correlations may not be available.",
        "Only the originally-missing target cells are scored, against the true values; recover them as "
        "accurately as you can from whatever signal remains.",
    ],
}
