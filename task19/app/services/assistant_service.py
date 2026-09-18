import json
import re

import requests
from pydantic import ValidationError

from app.config import (
    MAX_TOOL_ROUNDS,
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
)
from app.models.leave import ApplyLeaveArguments
from app.prompts.employee_assistant_prompt import SYSTEM_PROMPT, TOOLS
from app.storage.chat_memory import add_message, get_history
from app.tools.registry import execute_tool


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

TOOLS_BY_NAME = {
    tool["function"]["name"]: tool
    for tool in TOOLS
}


def validate_user_leave_type(message: str):
    """
    Reject unsupported leave types before the AI can map them
    to casual or sick leave.
    """

    invalid_leave_types = [
        "vacation leave",
        "annual leave",
        "earned leave",
        "privilege leave",
        "optional leave",
        "holiday leave",
    ]

    message_lower = message.lower()

    for leave_type in invalid_leave_types:
        if re.search(rf"\b{re.escape(leave_type)}\b", message_lower):
            raise ValueError(
                f"Invalid leave type: '{leave_type}'. "
                "Only casual leave and sick leave are supported."
            )


def validate_tool_arguments(tool_name: str, arguments: dict):
    if tool_name in [
        "get_employee",
        "get_leave_balance",
        "get_leave_requests",
    ]:
        employee_id = arguments.get("employee_id")

        if not isinstance(employee_id, int):
            raise ValueError("Invalid employee ID")

        return {
            "employee_id": employee_id
        }

    if tool_name == "get_company_holidays":
        start_date = arguments.get("start_date")
        end_date = arguments.get("end_date")

        return {
            "start_date": start_date,
            "end_date": end_date,
        }

    if tool_name == "apply_leave":
        validated = ApplyLeaveArguments(**arguments)

        return validated.model_dump()

    raise ValueError("Unknown tool")


def call_openrouter(messages, use_tools=True):
    if not OPENROUTER_API_KEY:
        raise ValueError("OpenRouter API key is not configured")

    if not OPENROUTER_MODEL:
        raise ValueError("OpenRouter model is not configured")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
    }

    if use_tools:
        data["tools"] = TOOLS
        data["tool_choice"] = "auto"
    else:
        data["tool_choice"] = "none"

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=data,
            timeout=30,
        )
    except requests.RequestException:
        raise ValueError("Could not connect to OpenRouter")

    if response.status_code == 401:
        raise ValueError("Invalid OpenRouter API key")

    if response.status_code == 429:
        raise ValueError("OpenRouter rate limit reached")

    if response.status_code >= 400:
        raise ValueError("OpenRouter request failed")

    try:
        result = response.json()
    except ValueError:
        raise ValueError("Invalid response from OpenRouter")

    if "choices" not in result or not result["choices"]:
        raise ValueError("Invalid AI response")

    return result


def run_assistant(session_id: str, message: str):
    # Backend validation happens BEFORE AI tool execution.
    validate_user_leave_type(message)

    history = get_history(session_id)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    messages.extend(history)

    messages.append(
        {
            "role": "user",
            "content": message,
        }
    )

    tools_used = []

    for _ in range(MAX_TOOL_ROUNDS):
        response = call_openrouter(
            messages,
            use_tools=True,
        )

        assistant_message = response["choices"][0]["message"]

        tool_calls = assistant_message.get("tool_calls")

        if not tool_calls:
            final_response = assistant_message.get(
                "content",
                "",
            )

            add_message(
                session_id,
                {
                    "role": "user",
                    "content": message,
                },
            )

            add_message(
                session_id,
                {
                    "role": "assistant",
                    "content": final_response,
                },
            )

            return {
                "response": final_response,
                "tools_used": tools_used,
            }

        messages.append(assistant_message)

        for tool_call in tool_calls:
            function = tool_call.get(
                "function",
                {},
            )

            tool_name = function.get("name")

            arguments_text = function.get(
                "arguments",
                "{}",
            )

            if not tool_name:
                raise ValueError("Invalid tool call")

            if tool_name not in TOOLS_BY_NAME:
                raise ValueError("Unknown tool")

            try:
                arguments = json.loads(arguments_text)
            except json.JSONDecodeError:
                raise ValueError("Invalid tool arguments")

            try:
                validated_arguments = validate_tool_arguments(
                    tool_name,
                    arguments,
                )
            except ValidationError:
                raise ValueError("Invalid tool arguments")

            if tool_name not in tools_used:
                tools_used.append(tool_name)

            try:
                result = execute_tool(
                    tool_name,
                    validated_arguments,
                )
            except ValueError as e:
                raise ValueError(str(e))
            except Exception:
                raise ValueError("Tool execution failed")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.get("id"),
                    "content": json.dumps(result),
                }
            )

    raise ValueError("Maximum tool-call limit exceeded")