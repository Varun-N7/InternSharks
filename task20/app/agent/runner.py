import json
import uuid
import requests

from app.agent.registry import execute_tool
from app.config import MAX_AGENT_STEPS, OPENROUTER_API_KEY, OPENROUTER_MODEL
from app.prompts.agent_prompt import SYSTEM_PROMPT, TOOLS
from app.storage.run_store import save_run


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def call_openrouter(messages):
    if not OPENROUTER_API_KEY:
        raise ValueError("OpenRouter API key is not configured")

    if not OPENROUTER_MODEL:
        raise ValueError("OpenRouter model is not configured")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "tools": TOOLS,
        "tool_choice": "auto"
    }

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=data,
            timeout=30
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


def validate_tool_arguments(tool_name, arguments):

    if tool_name == "find_employee":
        employee_id = arguments.get("employee_id")
        name = arguments.get("name")

        if employee_id is None and not name:
            raise ValueError(
                "Employee ID or employee name is required"
            )

        if employee_id is not None and not isinstance(employee_id, int):
            raise ValueError("Invalid employee ID")

        if name is not None and not isinstance(name, str):
            raise ValueError("Invalid employee name")

        return arguments

    if tool_name == "create_project":
        name = arguments.get("name")
        description = arguments.get("description", "")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Project name is required")

        if not isinstance(description, str):
            raise ValueError("Invalid project description")

        return {
            "name": name,
            "description": description
        }

    if tool_name == "get_project":
        project_id = arguments.get("project_id")

        if not isinstance(project_id, int):
            raise ValueError("Invalid project ID")

        return {
            "project_id": project_id
        }

    if tool_name == "add_project_member":
        project_id = arguments.get("project_id")
        employee_id = arguments.get("employee_id")

        if not isinstance(project_id, int):
            raise ValueError("Invalid project ID")

        if not isinstance(employee_id, int):
            raise ValueError("Invalid employee ID")

        return {
            "project_id": project_id,
            "employee_id": employee_id
        }

    if tool_name == "create_project_task":
        project_id = arguments.get("project_id")
        title = arguments.get("title")
        priority = arguments.get("priority")
        assigned_to = arguments.get("assigned_to")

        if not isinstance(project_id, int):
            raise ValueError("Invalid project ID")

        if not isinstance(title, str) or not title.strip():
            raise ValueError("Task title is required")

        if priority not in ["low", "medium", "high"]:
            raise ValueError("Invalid priority")

        if assigned_to is not None and not isinstance(assigned_to, int):
            raise ValueError("Invalid employee ID")

        return {
            "project_id": project_id,
            "title": title,
            "priority": priority,
            "assigned_to": assigned_to
        }

    if tool_name == "list_project_tasks":
        project_id = arguments.get("project_id")

        if not isinstance(project_id, int):
            raise ValueError("Invalid project ID")

        return {
            "project_id": project_id
        }

    if tool_name == "update_task_status":
        task_id = arguments.get("task_id")
        status = arguments.get("status")

        if not isinstance(task_id, int):
            raise ValueError("Invalid task ID")

        if status not in ["todo", "in_progress", "completed"]:
            raise ValueError("Invalid task status")

        return {
            "task_id": task_id,
            "status": status
        }

    raise ValueError("Unknown tool")


def run_agent(goal: str):

    run_id = f"run_{uuid.uuid4().hex[:8]}"

    trace = {
        "run_id": run_id,
        "goal": goal,
        "status": "running",
        "steps": [],
        "tools_used": []
    }

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": goal
        }
    ]

    save_run(run_id, trace)

    executed_steps = 0

    while executed_steps < MAX_AGENT_STEPS:

        response = call_openrouter(messages)

        assistant_message = response["choices"][0]["message"]

        tool_calls = assistant_message.get("tool_calls")

        # No tool call means the AI has finished.
        if not tool_calls:

            final_response = assistant_message.get("content", "")

            trace["status"] = "completed"
            trace["response"] = final_response

            save_run(run_id, trace)

            return {
                "run_id": run_id,
                "status": "completed",
                "steps_executed": executed_steps,
                "tools_used": trace["tools_used"],
                "response": final_response
            }

        messages.append(assistant_message)

        for tool_call in tool_calls:

            # Check limit BEFORE executing another tool.
            if executed_steps >= MAX_AGENT_STEPS:

                trace["status"] = "failed"
                trace["response"] = (
                    "Agent stopped because the maximum "
                    "execution step limit was reached."
                )

                save_run(run_id, trace)

                return {
                    "run_id": run_id,
                    "status": "failed",
                    "steps_executed": executed_steps,
                    "tools_used": trace["tools_used"],
                    "response": trace["response"]
                }

            function = tool_call.get("function", {})

            tool_name = function.get("name")
            arguments_text = function.get("arguments", "{}")

            if not tool_name:
                raise ValueError("Invalid tool call")

            try:
                arguments = json.loads(arguments_text)
            except json.JSONDecodeError:
                raise ValueError("Invalid tool arguments")

            validated_arguments = validate_tool_arguments(
                tool_name,
                arguments
            )

            # Every individual tool execution is one step.
            executed_steps += 1

            step = {
                "step": executed_steps,
                "tool": tool_name,
                "arguments": validated_arguments
            }

            try:

                result = execute_tool(
                    tool_name,
                    validated_arguments
                )

                step["status"] = "success"
                step["result"] = result

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.get("id"),
                        "content": json.dumps(result)
                    }
                )

            except ValueError as e:

                step["status"] = "failed"
                step["result"] = {
                    "error": str(e)
                }

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.get("id"),
                        "content": json.dumps(
                            {
                                "success": False,
                                "error": str(e)
                            }
                        )
                    }
                )

            trace["steps"].append(step)

            if tool_name not in trace["tools_used"]:
                trace["tools_used"].append(tool_name)

            save_run(run_id, trace)

            # Stop immediately after the 10th tool execution.
            if executed_steps >= MAX_AGENT_STEPS:

                trace["status"] = "failed"
                trace["response"] = (
                    "Agent stopped because the maximum "
                    "execution step limit was reached."
                )

                save_run(run_id, trace)

                return {
                    "run_id": run_id,
                    "status": "failed",
                    "steps_executed": executed_steps,
                    "tools_used": trace["tools_used"],
                    "response": trace["response"]
                }

    # Safety fallback
    trace["status"] = "failed"
    trace["response"] = (
        "Agent stopped because the maximum "
        "execution step limit was reached."
    )

    save_run(run_id, trace)

    return {
        "run_id": run_id,
        "status": "failed",
        "steps_executed": executed_steps,
        "tools_used": trace["tools_used"],
        "response": trace["response"]
    }