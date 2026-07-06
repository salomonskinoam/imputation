"""The california-impute-coamp-single task (grid slot 2: Numeric·Single·CoAmp)."""
from sdk import repo_root
from tasks_def.configs import california_coamp_single as config
from worlds.imputation.world import ImputationWorld

CALIFORNIA_COAMP_SINGLE_TASK = ImputationWorld(
    name="california-impute-coamp-single",
    config=config.CONFIG,
    source_dir=repo_root() / "tasks" / "california-impute-coamp-single",
)
