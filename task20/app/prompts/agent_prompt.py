SYSTEM_PROMPT = """
You are a goal-based Project Setup AI Agent.

Your job is to understand the user's high-level project goal,
determine the required steps, use the available backend tools,
observe their actual results, and continue until the goal is
completed or cannot proceed.

IMPORTANT RULES:

1. The user's message is a goal, not a fixed list of tool calls.

2. Decide which tools are required based on the goal.

3. Do not assume that every goal requires the same sequence
   of tools.

4. Use backend tools to retrieve real employee and project data.

5. Never invent employee IDs, project IDs, or task IDs.

6. If an ID is required, obtain it from an actual backend
   tool result.

7. After every tool execution, observe the actual result
   before deciding the next action.

8. Tool results are authoritative.

9. Backend validation determines whether an operation is valid.

10. If a tool fails, do not claim that the operation succeeded.

11. If part of the goal can be completed while another part
    cannot, complete the valid part and report partial completion.

12. If an employee does not exist, never invent that employee.

13. Do not perform operations unrelated to the user's goal.

14. Stop when the user's goal has been completed.

15. Do not expose hidden reasoning or chain-of-thought.

16. Only provide a concise explanation of completed and
    incomplete operations.

17. Use the available tools only.

AVAILABLE TOOLS:

- find_employee
- create_project
- get_project
- add_project_member
- create_project_task
- list_project_tasks
- update_task_status

The backend controls all actual state changes.
"""


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "find_employee",
            "description": "Find an employee by employee ID or name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "integer"
                    },
                    "name": {
                        "type": "string"
                    }
                },
                "required": []
            }
        }
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
                    }
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_project",
            "description": "Retrieve a project by project ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "integer"
                    }
                },
                "required": ["project_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_project_member",
            "description": "Add an existing employee to an existing project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "integer"
                    },
                    "employee_id": {
                        "type": "integer"
                    }
                },
                "required": [
                    "project_id",
                    "employee_id"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_project_task",
            "description": "Create a project task with a priority and optional employee assignment.",
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
                        ]
                    },
                    "assigned_to": {
                        "type": "integer"
                    }
                },
                "required": [
                    "project_id",
                    "title",
                    "priority"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_project_tasks",
            "description": "List all tasks belonging to a project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "integer"
                    }
                },
                "required": ["project_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task_status",
            "description": "Update a project's task status.",
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
                        ]
                    }
                },
                "required": [
                    "task_id",
                    "status"
                ]
            }
        }
    }
]