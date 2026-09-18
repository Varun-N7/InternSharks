from app.tools.employee_tools import get_employee, get_leave_balance
from app.tools.holiday_tools import get_company_holidays
from app.tools.leave_tools import apply_leave, get_leave_requests


TOOLS = {
    "get_employee": get_employee,
    "get_leave_balance": get_leave_balance,
    "get_company_holidays": get_company_holidays,
    "apply_leave": apply_leave,
    "get_leave_requests": get_leave_requests,
}


def execute_tool(tool_name: str, arguments: dict):
    if tool_name not in TOOLS:
        raise ValueError("Unknown tool")

    return TOOLS[tool_name](**arguments)