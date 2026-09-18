from app.tools.employee_tools import find_employee_tool
from app.tools.project_tools import (
    add_project_member_tool,
    create_project_tool,
    get_project_tool,
)
from app.tools.task_tools import (
    create_project_task_tool,
    list_project_tasks_tool,
    update_task_status_tool,
)


TOOLS = {
    "find_employee": find_employee_tool,
    "create_project": create_project_tool,
    "get_project": get_project_tool,
    "add_project_member": add_project_member_tool,
    "create_project_task": create_project_task_tool,
    "list_project_tasks": list_project_tasks_tool,
    "update_task_status": update_task_status_tool,
}


def execute_tool(tool_name: str, arguments: dict):
    if tool_name not in TOOLS:
        raise ValueError("Unknown tool")

    return TOOLS[tool_name](**arguments)