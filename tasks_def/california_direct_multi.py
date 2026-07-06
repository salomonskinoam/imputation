"""The california-impute-direct-multi task (grid row 3: CA Numeric Multi No-coamp)."""
from sdk import repo_root
from tasks_def.configs import california_direct_multi as config
from worlds.imputation.world import ImputationWorld

CALIFORNIA_DIRECT_MULTI_TASK = ImputationWorld(
    name="california-impute-direct-multi",
    config=config.CONFIG,
    source_dir=repo_root() / "tasks" / "california-impute-direct-multi",
)
