"""Grader entry point the MCP server imports (delegates to ADULT_CAT_COAMP_SINGLE_OCC_TASK.grade())."""
from tasks_def.adult_cat_coamp_single_occ import ADULT_CAT_COAMP_SINGLE_OCC_TASK


def grade(transcript: str = ""):
    return ADULT_CAT_COAMP_SINGLE_OCC_TASK.grade(transcript)


if __name__ == "__main__":
    print(grade().model_dump())
