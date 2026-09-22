import hashlib
import json


def build_idempotency_key(run_id, action_id):
    """
    Create a stable idempotency key for one agent action.

    The same run + action will always produce
    the same key, even after retries or restart.
    """

    raw_value = f"{run_id}:{action_id}"

    return hashlib.sha256(
        raw_value.encode("utf-8")
    ).hexdigest()


def build_idempotency_record(
    run_id,
    action_id,
    tool,
    arguments,
):
    """
    Create the persistent information needed to
    identify and safely retry one action.
    """

    return {
        "run_id": run_id,
        "action_id": action_id,
        "tool": tool,
        "idempotency_key": build_idempotency_key(
            run_id,
            action_id,
        ),
        "arguments": arguments,
        "status": "pending",
        "attempt_count": 0,
        "last_failure": None,
        "previous_result": None,
    }


def arguments_hash(arguments):
    """
    Produce a stable hash of tool arguments.

    This helps detect whether an action's arguments
    changed between attempts.
    """

    serialized = json.dumps(
        arguments,
        sort_keys=True,
        separators=(",", ":"),
    )

    return hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()