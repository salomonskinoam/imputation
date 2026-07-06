"""Grader entry point the MCP server imports (delegates to ADULT_CAT_COAMP_MULTI_TASK.grade())."""
from tasks_def.adult_cat_coamp_multi import ADULT_CAT_COAMP_MULTI_TASK


def grade(transcript: str = ""):
    return ADULT_CAT_COAMP_MULTI_TASK.grade(transcript)


if __name__ == "__main__":
    print(grade().model_dump())
