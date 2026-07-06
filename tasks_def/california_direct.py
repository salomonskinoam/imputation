"""The california-impute-direct task: direct imputation-quality scoring (Direction A)."""
from sdk import repo_root
from tasks_def.configs import california_direct as config
from worlds.imputation.world import ImputationWorld

CALIFORNIA_DIRECT_TASK = ImputationWorld(
    name="california-impute-direct",
    config=config.CONFIG,
    source_dir=repo_root() / "tasks" / "california-impute-direct",
)
