conversation_history = {}


def get_history(session_id: str):
    return conversation_history.get(session_id, [])


def add_message(session_id: str, message: dict):
    if session_id not in conversation_history:
        conversation_history[session_id] = []

    conversation_history[session_id].append(message)


def clear_history(session_id: str):
    conversation_history.pop(session_id, None)