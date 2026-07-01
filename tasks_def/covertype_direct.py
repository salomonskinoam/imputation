"""The covertype-impute-direct task: direct imputation-quality scoring (Direction A)."""
from sdk import repo_root
from tasks_def.configs import covertype_direct as config
from worlds.imputation.world import ImputationWorld

COVERTYPE_DIRECT_TASK = ImputationWorld(
    name="covertype-impute-direct",
    config=config.CONFIG,
    source_dir=repo_root() / "tasks" / "covertype-impute-direct",
)
