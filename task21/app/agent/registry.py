from app.tools.employee_tools import find_employee_tool

from app.tools.project_tools import (
    create_project_tool,
    get_project_tool,
    list_projects_tool,
    add_project_member_tool,
)

from app.tools.task_tools import (
    create_project_task_tool,
    get_project_tasks_tool,
    get_task_tool,
    update_task_status_tool,
    delete_project_task_tool,
)


TOOLS = {
    "find_employee": {
        "function": find_employee_tool,
        "requires_approval": False,
    },

    "get_project": {
        "function": get_project_tool,
        "requires_approval": False,
    },

    "list_projects": {
        "function": list_projects_tool,
        "requires_approval": False,
    },

    "get_project_tasks": {
        "function": get_project_tasks_tool,
        "requires_approval": False,
    },

    "get_task": {
        "function": get_task_tool,
        "requires_approval": False,
    },

    "create_project": {
        "function": create_project_tool,
        "requires_approval": True,
    },

    "add_project_member": {
        "function": add_project_member_tool,
        "requires_approval": True,
    },

    "create_project_task": {
        "function": create_project_task_tool,
        "requires_approval": True,
    },

    "update_task_status": {
        "function": update_task_status_tool,
        "requires_approval": True,
    },

    "delete_project_task": {
        "function": delete_project_task_tool,
        "requires_approval": True,
    },
}


def get_tool(tool_name):
    if tool_name not in TOOLS:
        raise ValueError("Unknown tool")

    return TOOLS[tool_name]


def execute_tool(tool_name, arguments):
    tool = get_tool(tool_name)

    return tool["function"](**arguments)