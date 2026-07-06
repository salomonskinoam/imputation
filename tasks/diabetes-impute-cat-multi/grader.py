"""Grader entry point the MCP server imports (delegates to DIABETES_CAT_MULTI_TASK.grade())."""
from tasks_def.diabetes_cat_multi import DIABETES_CAT_MULTI_TASK


def grade(transcript: str = ""):
    return DIABETES_CAT_MULTI_TASK.grade(transcript)


if __name__ == "__main__":
    print(grade().model_dump())
