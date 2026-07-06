"""California DIRECT MULTI (grid row 3: California · Numeric · Multi · No-coamp).

Same engine/amputation as california-impute-direct (MAR on `latitude`, rate 0.5), but two targets
(`median_income` + `population`) so it fills the Multi·No slot for California (mirror of the covertype
Multi·No base task). No co-amputation.
"""
from tasks_def.configs import california_direct as _base

CONFIG: dict = {
    **_base.CONFIG,
    "target_cols": ["median_income", "population"],
}
