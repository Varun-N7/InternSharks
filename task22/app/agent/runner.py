import json
import uuid
import requests

from app.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
    MAX_AGENT_STEPS,
    MAX_RETRIES,
    RETRY_BASE_DELAY,
    EXTERNAL_TOOL_TIMEOUT,
    OPENROUTER_TIMEOUT,
)

from app.agent.registry import TOOLS, execute_tool
from app.agent.state_manager import create_run, save_state
from app.services.approval_service import (
    create_action,
    mark_executed,
    get_execution,
)

from app.prompts.agent_prompt import AGENT_SYSTEM_PROMPT

from app.reliability.retry import execute_with_retry
from app.reliability.timeout import execute_with_timeout
from app.reliability.errors import (
    RetryableError,
    NonRetryableError,
)


def openrouter_call(messages):
    if not OPENROUTER_API_KEY:
        raise NonRetryableError(
            "Invalid OpenRouter API key"
        )

    if not OPENROUTER_MODEL:
        raise NonRetryableError(
            "OpenRouter model is not configured"
        )

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "tools": build_tool_schemas(),
        "tool_choice": "auto",
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=OPENROUTER_TIMEOUT,
        )

    except requests.Timeout:
        raise RetryableError(
            "OpenRouter request timed out"
        )

    except requests.RequestException as error:
        raise RetryableError(
            f"OpenRouter network error: {error}"
        )

    if response.status_code == 401:
        raise NonRetryableError(
            "Invalid OpenRouter API key"
        )

    if response.status_code == 429:
        raise RetryableError(
            "OpenRouter rate limit reached"
        )

    if response.status_code in (
        500,
        502,
        503,
        504,
    ):
        raise RetryableError(
            f"OpenRouter temporary error: "
            f"HTTP {response.status_code}"
        )

    if response.status_code >= 400:
        try:
            error_data = response.json()

            error_message = (
                error_data
                .get("error", {})
                .get("message")
            )

            if error_message:
                raise NonRetryableError(
                    f"OpenRouter error: "
                    f"{error_message}"
                )

        except NonRetryableError:
            raise

        except Exception:
            pass

        raise NonRetryableError(
            f"OpenRouter request failed with "
            f"HTTP {response.status_code}"
        )

    try:
        data = response.json()

    except Exception:
        raise NonRetryableError(
            "Invalid OpenRouter response"
        )

    if (
        "choices" not in data
        or not data["choices"]
    ):
        raise NonRetryableError(
            "Invalid OpenRouter response"
        )

    return data["choices"][0]["message"]


def call_openrouter_with_retry(messages):
    return execute_with_retry(
        lambda: openrouter_call(messages),
        max_retries=MAX_RETRIES,
        base_delay=RETRY_BASE_DELAY,
    )


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
                        "employee_id": {
                            "type": "integer"
                        },
                        "name": {
                            "type": "string"
                        },
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
                        "project_id": {
                            "type": "integer"
                        },
                    },
                    "required": [
                        "project_id"
                    ],
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
                        "project_id": {
                            "type": "integer"
                        },
                    },
                    "required": [
                        "project_id"
                    ],
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
                        "task_id": {
                            "type": "integer"
                        },
                    },
                    "required": [
                        "task_id"
                    ],
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
                        "name": {
                            "type": "string"
                        },
                        "description": {
                            "type": "string"
                        },
                    },
                    "required": [
                        "name"
                    ],
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
                        "project_id": {
                            "type": "integer"
                        },
                        "employee_id": {
                            "type": "integer"
                        },
                    },
                    "required": [
                        "project_id",
                        "employee_id"
                    ],
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
                        "project_id": {
                            "type": "integer"
                        },
                        "title": {
                            "type": "string"
                        },
                        "priority": {
                            "type": "string",
                            "enum": [
                                "low",
                                "medium",
                                "high"
                            ],
                        },
                        "assigned_to": {
                            "type": "integer"
                        },
                    },
                    "required": [
                        "project_id",
                        "title",
                        "priority"
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
                        "task_id": {
                            "type": "integer"
                        },
                        "status": {
                            "type": "string",
                            "enum": [
                                "todo",
                                "in_progress",
                                "completed"
                            ],
                        },
                    },
                    "required": [
                        "task_id",
                        "status"
                    ],
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
                        "task_id": {
                            "type": "integer"
                        },
                    },
                    "required": [
                        "task_id"
                    ],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_external_project_status",
                "description": (
                    "Get external project status."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "integer"
                        },
                        "failure_mode": {
                            "type": "string",
                            "enum": [
                                "success",
                                "temporary_failure",
                                "timeout",
                                "permanent_failure",
                            ],
                        },
                    },
                    "required": [
                        "project_id"
                    ],
                },
            },
        },
    ]


def validate_arguments(
    tool_name,
    arguments,
):
    if not isinstance(arguments, dict):
        raise NonRetryableError(
            "Invalid tool arguments"
        )

    integer_fields = {
        "employee_id",
        "project_id",
        "task_id",
    }

    for field in integer_fields:
        if field in arguments:
            if (
                not isinstance(
                    arguments[field],
                    int,
                )
                or isinstance(
                    arguments[field],
                    bool,
                )
            ):
                raise NonRetryableError(
                    f"Invalid {field}"
                )


def add_trace(
    run,
    step,
    trace_type,
    tool,
    status,
    arguments=None,
    result=None,
    attempt=None,
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

    if attempt is not None:
        event["attempt"] = attempt

    run["execution_trace"].append(event)


def execute_tool_with_reliability(
    tool_name,
    arguments,
    on_retry=None,
    on_attempt=None,
):
    tool = TOOLS.get(tool_name)

    if not tool:
        raise NonRetryableError(
            f"Unknown tool: {tool_name}"
        )

    def operation():
        if tool_name == (
            "get_external_project_status"
        ):
            return execute_with_timeout(
                lambda: execute_tool(
                    tool_name,
                    arguments,
                ),
                timeout_seconds=(
                    EXTERNAL_TOOL_TIMEOUT
                ),
            )

        return execute_tool(
            tool_name,
            arguments,
        )

    return execute_with_retry(
        operation,
        max_retries=MAX_RETRIES,
        base_delay=RETRY_BASE_DELAY,
        on_retry=on_retry,
        on_attempt=on_attempt,
    )


def start_agent(goal):
    run_id = (
        "run_"
        + uuid.uuid4().hex[:10]
    )

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
    while (
        run["step_count"]
        < MAX_AGENT_STEPS
    ):

        llm_result = (
            call_openrouter_with_retry(
                run["messages"]
            )
        )

        if not llm_result["success"]:
            run["status"] = "failed"

            add_trace(
                run,
                run["step_count"],
                "llm_execution",
                "openrouter",
                "failed",
                result={
                    "error": llm_result[
                        "error"
                    ],
                    "attempt_count":
                        llm_result[
                            "attempt_count"
                        ],
                },
                attempt=llm_result[
                    "attempt_count"
                ],
            )

            save_state(run)

            return build_response(run)

        assistant_message = (
            llm_result["result"]
        )

        tool_calls = assistant_message.get(
            "tool_calls"
        )

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

            if (
                run["step_count"]
                >= MAX_AGENT_STEPS
            ):
                run["status"] = "failed"

                save_state(run)

                return build_response(run)

            tool_name = (
                tool_call["function"]["name"]
            )

            raw_arguments = (
                tool_call["function"].get(
                    "arguments",
                    "{}",
                )
            )

            try:
                arguments = json.loads(
                    raw_arguments
                )

            except json.JSONDecodeError:
                run["status"] = "failed"

                add_trace(
                    run,
                    run["step_count"] + 1,
                    "tool_execution",
                    tool_name,
                    "failed",
                    result=(
                        "Invalid tool arguments"
                    ),
                )

                save_state(run)

                return build_response(run)

            try:
                validate_arguments(
                    tool_name,
                    arguments,
                )

            except Exception as error:
                run["status"] = "failed"

                add_trace(
                    run,
                    run["step_count"] + 1,
                    "tool_execution",
                    tool_name,
                    "failed",
                    arguments,
                    {
                        "error": str(error)
                    },
                )

                save_state(run)

                return build_response(run)

            tool = TOOLS.get(
                tool_name
            )

            if not tool:
                run["status"] = "failed"

                add_trace(
                    run,
                    run["step_count"] + 1,
                    "tool_execution",
                    tool_name,
                    "failed",
                    arguments,
                    {
                        "error": "Unknown tool"
                    },
                )

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

                run["status"] = (
                    "waiting_for_approval"
                )

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

            def on_tool_retry(attempt, next_attempt, delay, error):
                add_trace(
                    run,
                    run["step_count"],
                    "tool_execution",
                    tool_name,
                    "failed",
                    arguments,
                    {
                        "error": error,
                        "retryable": True,
                    },
                    attempt,
                )

            reliability_result = (
                execute_tool_with_reliability(
                    tool_name,
                    arguments,
                    on_retry=on_tool_retry,
                )
            )

            if reliability_result["success"]:

                result = (
                    reliability_result["result"]
                )

                add_trace(
                    run,
                    run["step_count"],
                    "tool_execution",
                    tool_name,
                    "success",
                    arguments,
                    result,
                    reliability_result[
                        "attempt_count"
                    ],
                )

            else:

                result = {
                    "error": (
                        reliability_result[
                            "error"
                        ]
                    ),
                    "attempt_count": (
                        reliability_result[
                            "attempt_count"
                        ]
                    ),
                }

                add_trace(
                    run,
                    run["step_count"],
                    "tool_execution",
                    tool_name,
                    "failed",
                    arguments,
                    result,
                    reliability_result[
                        "attempt_count"
                    ],
                )

                run["status"] = (
                    "partially_completed"
                )

            run["messages"].append(
                {
                    "role": "tool",
                    "tool_call_id": (
                        tool_call["id"]
                    ),
                    "name": tool_name,
                    "content": json.dumps(
                        result
                    ),
                }
            )

            save_state(run)

    run["status"] = "failed"

    save_state(run)

    return build_response(run)


def approve_and_resume(
    run,
    action,
):
    tool_name = action["tool"]
    arguments = action["arguments"]
    action_id = action["action_id"]

    validate_arguments(
        tool_name,
        arguments,
    )

    existing_execution = (
        get_execution(action_id)
    )

    if existing_execution:
        if existing_execution["status"] == (
            "executed"
        ):
            previous_result = (
                existing_execution[
                    "previous_result"
                ]
            )

            try:
                previous_result = json.loads(
                    previous_result
                )
            except Exception:
                pass

            run["pending_action"] = None
            run["status"] = "running"

            run["messages"].append(
                {
                    "role": "tool",
                    "tool_call_id": action_id,
                    "name": tool_name,
                    "content": json.dumps(
                        previous_result
                    ),
                }
            )

            save_state(run)

            return continue_agent(run)

    run["step_count"] += 1

    def on_approval_tool_retry(attempt, next_attempt, delay, error):
        from app.storage.action_repository import update_attempt
        update_attempt(action_id, attempt, error)
        add_trace(
            run,
            run["step_count"],
            "tool_execution",
            tool_name,
            "failed",
            arguments,
            {
                "error": error,
                "retryable": True,
            },
            attempt,
        )

    reliability_result = (
        execute_tool_with_reliability(
            tool_name,
            arguments,
            on_retry=on_approval_tool_retry,
        )
    )

    if reliability_result["success"]:

        result = (
            reliability_result["result"]
        )

        mark_executed(
            action_id,
            result=result,
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
            reliability_result[
                "attempt_count"
            ],
        )

        run["messages"].append(
            {
                "role": "tool",
                "tool_call_id": action_id,
                "name": tool_name,
                "content": json.dumps(
                    result
                ),
            }
        )

        run["status"] = "running"

        save_state(run)

        return continue_agent(run)

    result = {
        "error": reliability_result[
            "error"
        ],
        "attempt_count": (
            reliability_result[
                "attempt_count"
            ]
        ),
    }

    add_trace(
        run,
        run["step_count"],
        "tool_execution",
        tool_name,
        "failed",
        arguments,
        result,
        reliability_result[
            "attempt_count"
        ],
    )

    run["status"] = (
        "partially_completed"
    )

    save_state(run)

    return build_response(run)


def build_response(run):
    return {
        "run_id": run["run_id"],
        "goal": run["goal"],
        "status": run["status"],
        "step_count": run["step_count"],
        "pending_action": run[
            "pending_action"
        ],
        "execution_trace": run[
            "execution_trace"
        ],
        "response": (
            "Agent is waiting for human approval."
            if run["status"]
            == "waiting_for_approval"
            else "Agent execution completed."
            if run["status"]
            == "completed"
            else "Agent execution stopped."
        ),
    }