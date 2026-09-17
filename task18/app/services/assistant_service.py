import json
import re

from pydantic import ValidationError

from app.models.assistant import (
    CalculatorArguments,
    GetTaskArguments
)
from app.services.ai_service import call_openrouter
from app.tools.registry import execute_tool


def validate_tool_arguments(tool_name: str, arguments: dict):
    if tool_name == "calculator":
        validated = CalculatorArguments(**arguments)
        return validated.model_dump()

    if tool_name == "get_task":
        validated = GetTaskArguments(**arguments)
        return validated.model_dump()

    if tool_name == "get_current_date":
        if arguments:
            raise ValueError("get_current_date does not accept arguments")
        return {}

    raise ValueError("Unknown tool")


def check_division_by_zero(message: str):
    text = message.lower()

    division_words = [
        "divided by 0",
        "divide by 0",
        "division by 0",
        "divided by zero",
        "divide by zero",
        "division by zero"
    ]

    for phrase in division_words:
        if phrase in text:
            raise ValueError("Cannot divide by zero")


def run_assistant(message: str):
    # Protect the backend from division-by-zero requests.
    check_division_by_zero(message)

    messages = [
        {
            "role": "user",
            "content": message
        }
    ]

    first_response = call_openrouter(messages)

    assistant_message = first_response["choices"][0]["message"]

    tool_calls = assistant_message.get("tool_calls")

    if not tool_calls:
        return {
            "response": assistant_message.get("content", "")
        }

    messages.append(assistant_message)

    for tool_call in tool_calls:
        function = tool_call.get("function", {})

        tool_name = function.get("name")
        arguments_text = function.get("arguments", "{}")

        if not tool_name:
            raise ValueError("Invalid tool call")

        try:
            arguments = json.loads(arguments_text)
        except json.JSONDecodeError:
            raise ValueError("Invalid tool arguments")

        try:
            validated_arguments = validate_tool_arguments(
                tool_name,
                arguments
            )
        except ValidationError:
            raise ValueError("Invalid tool arguments")

        try:
            result = execute_tool(
                tool_name,
                validated_arguments
            )
        except ValueError as e:
            raise ValueError(str(e))
        except Exception:
            raise ValueError("Tool execution failed")

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.get("id"),
                "content": json.dumps(result)
            }
        )

    final_response = call_openrouter(
        messages,
        use_tools=False
    )

    final_message = final_response["choices"][0]["message"]

    return {
        "response": final_message.get("content", "")
    }