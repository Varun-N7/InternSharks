conversation_history = {}

MAX_HISTORY_MESSAGES = 10


def get_history(session_id: str):
    return conversation_history.get(session_id, [])


def create_session(session_id: str):
    if session_id not in conversation_history:
        conversation_history[session_id] = []


def add_message(session_id: str, role: str, content: str):
    conversation_history[session_id].append(
        {
            "role": role,
            "content": content,
        }
    )


def get_recent_history(session_id: str):
    history = get_history(session_id)

    return history[-MAX_HISTORY_MESSAGES:]


def delete_session(session_id: str):
    if session_id in conversation_history:
        del conversation_history[session_id]


def session_exists(session_id: str):
    return session_id in conversation_history