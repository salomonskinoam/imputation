"""Covertype DIRECT SINGLE (grid row 9: Covertype · Numeric · Single · No-coamp).

Same engine/amputation as covertype-impute-direct (MAR on `Slope`, rate 0.5), but a single target
(`Elevation`) so it fills the Single·No slot for Covertype (mirror of the california Single·No base task).
No co-amputation.
"""
from tasks_def.configs import covertype_direct as _base

CONFIG: dict = {
    **_base.CONFIG,
    "target_cols": ["Elevation"],
}
