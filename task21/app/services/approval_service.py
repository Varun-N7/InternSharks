import uuid

from app.storage.action_repository import (
    save_action,
    get_action,
    update_action_status,
)


def create_action(run_id, tool, arguments):
    action_id = "action_" + uuid.uuid4().hex[:10]

    save_action(
        action_id=action_id,
        run_id=run_id,
        tool=tool,
        arguments=arguments,
        status="pending",
    )

    return action_id


def get_approval_action(action_id):
    return get_action(action_id)


def mark_approved(action_id):
    update_action_status(
        action_id,
        "approved",
    )


def mark_rejected(action_id):
    update_action_status(
        action_id,
        "rejected",
    )


def mark_executed(action_id):
    update_action_status(
        action_id,
        "executed",
    )