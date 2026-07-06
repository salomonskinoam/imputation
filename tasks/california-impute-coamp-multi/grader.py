"""Grader entry point the MCP server imports (delegates to CALIFORNIA_COAMP_MULTI_TASK.grade())."""
from tasks_def.california_coamp_multi import CALIFORNIA_COAMP_MULTI_TASK


def grade(transcript: str = ""):
    return CALIFORNIA_COAMP_MULTI_TASK.grade(transcript)


if __name__ == "__main__":
    print(grade().model_dump())
