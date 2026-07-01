"""The covertype-impute task: an ImputationWorld instance (MAR amputation on Covertype)."""
from sdk import repo_root
from tasks_def.configs import covertype as config
from worlds.imputation.world import ImputationWorld

COVERTYPE_TASK = ImputationWorld(
    name="covertype-impute",
    config=config.CONFIG,
    source_dir=repo_root() / "tasks" / "covertype-impute",
)
