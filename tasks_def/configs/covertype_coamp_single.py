"""Covertype co-amputate SINGLE — HARDER variant (grid slot 2 on Covertype, Numeric·Single·CoAmp).

First co-amp attempt (remove 3 reconstructors) came out MARGINAL: the 44 residual soil/wilderness
one-hot indicators still pin Elevation, so biggie's solutions converged (~0.60, ~2 levels) and more test
data did not help. This HARDER variant co-amputates ALL 44 indicators on the affected rows, forcing
Elevation to be recovered from the ~9 continuous terrain features only (Aspect, Slope, Hillshade×3,
distances) — a real skill test that should spread solutions. Risk: floor-collapse; vetted by a hosted
oracle validate before eval.
"""
from tasks_def.configs import covertype_direct as _base

# The 44 binary soil/wilderness one-hot indicators (the residual signal that pinned Elevation).
_INDICATORS = [f"Wilderness_Area{i}" for i in range(1, 5)] + [f"Soil_Type{i}" for i in range(1, 41)]

CONFIG: dict = {
    **_base.CONFIG,
    "mechanism":         "co_amputate",
    "target_cols":       ["Elevation"],
    "reconstructor_cols": _INDICATORS,
    "hints": [
        "Missing cells are NaN. On the affected rows many columns that would help predict the target "
        "are ALSO missing, so simple correlations are unavailable — recover from the remaining signal.",
        "Only the originally-missing target cells are scored, against the true values; recover them as "
        "accurately as you can.",
    ],
}
