from app.tools.calculator import calculator
from app.tools.date_tool import get_current_date
from app.tools.task_tool import get_task


TOOLS = {
    "calculator": calculator,
    "get_current_date": get_current_date,
    "get_task": get_task,
}


def execute_tool(tool_name: str, arguments: dict):
    if tool_name not in TOOLS:
        raise ValueError("Unknown tool")

    return TOOLS[tool_name](**arguments)
