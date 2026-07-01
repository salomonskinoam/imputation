"""Grader entry point the MCP server imports (delegates to COVERTYPE_TASK.grade())."""
from tasks_def.covertype import COVERTYPE_TASK


def grade(transcript: str = ""):
    return COVERTYPE_TASK.grade(transcript)


if __name__ == "__main__":
    print(grade().model_dump())
