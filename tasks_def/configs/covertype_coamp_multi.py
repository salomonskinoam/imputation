"""Covertype co-amputate MULTI — HARDER variant (grid slot 4, Numeric·Multi·CoAmp).

First co-amp attempt came out MARGINAL/narrow (band 0.04). Removing ALL 44 indicators floored it (oracle
0.00) — with 3 hard targets there was too little signal left. This DIALED-BACK harder variant co-amputates
the 3 targets + all 4 Wilderness_Area + the first 20 Soil_Type indicators (24 total), keeping the other 20
soil types as residual signal, to make recovery harder than the 3-reconstructor original without flooring.
Vetted by a hosted oracle validate before eval.
"""
from tasks_def.configs import covertype_direct as _base

# Dialed-back: 4 wilderness + first 20 soil types (keep Soil_Type21-40 as residual signal).
_INDICATORS = [f"Wilderness_Area{i}" for i in range(1, 5)] + [f"Soil_Type{i}" for i in range(1, 21)]

CONFIG: dict = {
    **_base.CONFIG,
    "mechanism":         "co_amputate",
    "target_cols": [
        "Elevation",
        "Horizontal_Distance_To_Roadways",
        "Horizontal_Distance_To_Fire_Points",
    ],
    "reconstructor_cols": _INDICATORS,
    "hints": [
        "Missing cells are NaN. On the affected rows many columns that would help predict the targets "
        "are ALSO missing, so simple correlations are unavailable — recover from the remaining signal.",
        "Only the originally-missing target cells are scored, against the true values; recover them as "
        "accurately as you can.",
    ],
}
