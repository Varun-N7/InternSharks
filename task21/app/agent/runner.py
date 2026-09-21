import json
import uuid
import requests

from app.config import OPENROUTER_API_KEY, OPENROUTER_MODEL, MAX_AGENT_STEPS
from app.agent.registry import TOOLS, execute_tool
from app.agent.state_manager import create_run, load_run, save_state
from app.services.approval_service import create_action, mark_executed
from app.prompts.agent_prompt import AGENT_SYSTEM_PROMPT


def openrouter_call(messages):
    if not OPENROUTER_API_KEY:
        raise ValueError("Invalid OpenRouter API key")

    if not OPENROUTER_MODEL:
        raise ValueError("OpenRouter model is not configured")

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "tools": build_tool_schemas(),
        "tool_choice": "auto",
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )

    if response.status_code == 401:
        raise ValueError("Invalid OpenRouter API key")

    if response.status_code == 429:
        raise ValueError("OpenRouter rate limit reached")

    if response.status_code >= 400:
        try:
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message")

            if error_message:
                raise ValueError(
                    f"OpenRouter error: {error_message}"
                )

        except ValueError:
            raise

        except Exception:
            pass

        raise ValueError("OpenRouter request failed")

    try:
        data = response.json()
    except Exception:
        raise ValueError("Invalid OpenRouter response")

    if "choices" not in data or not data["choices"]:
        raise ValueError("Invalid OpenRouter response")

    return data["choices"][0]["message"]


def build_tool_schemas():
    return [
        {
            "type": "function",
            "function": {
                "name": "find_employee",
                "description": "Find an employee by ID or name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {"type": "integer"},
                        "name": {"type": "string"},
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_project",
                "description": "Get a project by ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "integer"},
                    },
                    "required": ["project_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_projects",
                "description": "List all projects.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_project_tasks",
                "description": "Get tasks belonging to a project.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "integer"},
                    },
                    "required": ["project_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_task",
                "description": "Get a task by ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "integer"},
                    },
                    "required": ["task_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "create_project",
                "description": "Create a new project.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                    },
                    "required": ["name"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "add_project_member",
                "description": "Add an employee to a project.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "integer"},
                        "employee_id": {"type": "integer"},
                    },
                    "required": ["project_id", "employee_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "create_project_task",
                "description": "Create a project task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "integer"},
                        "title": {"type": "string"},
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                        },
                        "assigned_to": {"type": "integer"},
                    },
                    "required": [
                        "project_id",
                        "title",
                        "priority",
                    ],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "update_task_status",
                "description": "Update a task status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "integer"},
                        "status": {
                            "type": "string",
                            "enum": [
                                "todo",
                                "in_progress",
                                "completed",
                            ],
                        },
                    },
                    "required": ["task_id", "status"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "delete_project_task",
                "description": "Delete a project task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "integer"},
                    },
                    "required": ["task_id"],
                },
            },
        },
    ]


def validate_arguments(tool_name, arguments):
    if not isinstance(arguments, dict):
        raise ValueError("Invalid tool arguments")

    integer_fields = {
        "employee_id",
        "project_id",
        "task_id",
    }

    for field in integer_fields:
        if field in arguments and not isinstance(arguments[field], int):
            raise ValueError(f"Invalid {field}")


def add_trace(
    run,
    step,
    trace_type,
    tool,
    status,
    arguments=None,
    result=None,
):
    event = {
        "step": step,
        "type": trace_type,
        "tool": tool,
        "status": status,
    }

    if arguments is not None:
        event["arguments"] = arguments

    if result is not None:
        event["result"] = result

    run["execution_trace"].append(event)


def start_agent(goal):
    run_id = "run_" + uuid.uuid4().hex[:10]

    run = create_run(
        run_id=run_id,
        goal=goal,
    )

    run["messages"] = [
        {
            "role": "system",
            "content": AGENT_SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": goal,
        },
    ]

    save_state(run)

    return continue_agent(run)


def continue_agent(run):
    while run["step_count"] < MAX_AGENT_STEPS:

        assistant_message = openrouter_call(
            run["messages"]
        )

        tool_calls = assistant_message.get("tool_calls")

        if not tool_calls:
            run["status"] = "completed"

            run["messages"].append(
                assistant_message
            )

            save_state(run)

            return build_response(run)

        run["messages"].append(
            assistant_message
        )

        for tool_call in tool_calls:

            if run["step_count"] >= MAX_AGENT_STEPS:
                run["status"] = "failed"

                save_state(run)

                return build_response(run)

            tool_name = tool_call["function"]["name"]

            raw_arguments = tool_call["function"].get(
                "arguments",
                "{}",
            )

            try:
                arguments = json.loads(raw_arguments)

            except json.JSONDecodeError:
                run["status"] = "failed"

                add_trace(
                    run,
                    run["step_count"] + 1,
                    "tool_execution",
                    tool_name,
                    "failed",
                    result="Invalid tool arguments",
                )

                save_state(run)

                return build_response(run)

            validate_arguments(
                tool_name,
                arguments,
            )

            tool = TOOLS.get(tool_name)

            if not tool:
                run["status"] = "failed"

                save_state(run)

                return build_response(run)

            if tool["requires_approval"]:

                action_id = create_action(
                    run_id=run["run_id"],
                    tool=tool_name,
                    arguments=arguments,
                )

                run["pending_action"] = {
                    "action_id": action_id,
                    "tool": tool_name,
                    "arguments": arguments,
                    "status": "pending",
                }

                run["status"] = "waiting_for_approval"

                add_trace(
                    run,
                    run["step_count"] + 1,
                    "approval_required",
                    tool_name,
                    "waiting",
                    arguments,
                )

                save_state(run)

                return build_response(run)

            run["step_count"] += 1

            try:
                result = execute_tool(
                    tool_name,
                    arguments,
                )

                add_trace(
                    run,
                    run["step_count"],
                    "tool_execution",
                    tool_name,
                    "success",
                    arguments,
                    result,
                )

            except Exception as error:
                result = {
                    "error": str(error)
                }

                add_trace(
                    run,
                    run["step_count"],
                    "tool_execution",
                    tool_name,
                    "failed",
                    arguments,
                    result,
                )

            run["messages"].append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": tool_name,
                    "content": json.dumps(result),
                }
            )

            save_state(run)

    run["status"] = "failed"

    save_state(run)

    return build_response(run)


def approve_and_resume(run, action):
    tool_name = action["tool"]
    arguments = action["arguments"]

    validate_arguments(
        tool_name,
        arguments,
    )

    result = execute_tool(
        tool_name,
        arguments,
    )

    run["step_count"] += 1

    mark_executed(
        action["action_id"]
    )

    run["pending_action"] = None

    add_trace(
        run,
        run["step_count"],
        "tool_execution",
        tool_name,
        "success",
        arguments,
        result,
    )

    run["messages"].append(
        {
            "role": "tool",
            "tool_call_id": action["action_id"],
            "name": tool_name,
            "content": json.dumps(result),
        }
    )

    run["status"] = "running"

    save_state(run)

    return continue_agent(run)


def build_response(run):
    return {
        "run_id": run["run_id"],
        "goal": run["goal"],
        "status": run["status"],
        "step_count": run["step_count"],
        "pending_action": run["pending_action"],
        "execution_trace": run["execution_trace"],
        "response": (
            "Agent is waiting for human approval."
            if run["status"] == "waiting_for_approval"
            else "Agent execution completed."
            if run["status"] == "completed"
            else "Agent execution stopped."
        ),
    }