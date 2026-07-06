"""The covertype-impute-coamp-single task (grid slot 2 on Covertype: Numeric·Single·CoAmp)."""
from sdk import repo_root
from tasks_def.configs import covertype_coamp_single as config
from worlds.imputation.world import ImputationWorld

COVERTYPE_COAMP_SINGLE_TASK = ImputationWorld(
    name="covertype-impute-coamp-single",
    config=config.CONFIG,
    source_dir=repo_root() / "tasks" / "covertype-impute-coamp-single",
)
