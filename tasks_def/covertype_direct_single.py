"""The covertype-impute-direct-single task (grid row 9: COV Numeric Single No-coamp)."""
from sdk import repo_root
from tasks_def.configs import covertype_direct_single as config
from worlds.imputation.world import ImputationWorld

COVERTYPE_DIRECT_SINGLE_TASK = ImputationWorld(
    name="covertype-impute-direct-single",
    config=config.CONFIG,
    source_dir=repo_root() / "tasks" / "covertype-impute-direct-single",
)
