"""The covertype-impute-coamp-multi task (grid slot 4: Numeric·Multi·CoAmp)."""
from sdk import repo_root
from tasks_def.configs import covertype_coamp_multi as config
from worlds.imputation.world import ImputationWorld

COVERTYPE_COAMP_MULTI_TASK = ImputationWorld(
    name="covertype-impute-coamp-multi",
    config=config.CONFIG,
    source_dir=repo_root() / "tasks" / "covertype-impute-coamp-multi",
)
