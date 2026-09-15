from app.services.ai_service import get_ai_response
from app.storage.chat_memory import (
    add_message,
    create_session,
    get_recent_history,
    get_history,
    delete_session,
    session_exists,
)


def chat_with_ai(session_id: str, message: str):

    create_session(session_id)

    add_message(
        session_id,
        "user",
        message,
    )

    history = get_recent_history(session_id)

    response = get_ai_response(history)

    add_message(
        session_id,
        "assistant",
        response,
    )

    return response


def get_chat_history(session_id: str):

    if not session_exists(session_id):
        raise ValueError("Session not found")

    return get_history(session_id)


def clear_chat_history(session_id: str):

    if not session_exists(session_id):
        raise ValueError("Session not found")

    delete_session(session_id)