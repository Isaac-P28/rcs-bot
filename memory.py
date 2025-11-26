# Simple in-memory chat history
# For production, you would swap this for Redis or a database.

CHAT_HISTORY = {}  # key = conversation ID, value = list of messages

def add_message(convo_id, role, content):
    if convo_id not in CHAT_HISTORY:
        CHAT_HISTORY[convo_id] = []

    CHAT_HISTORY[convo_id].append({"role": role, "content": content})

    # Keep only last 20 messages
    CHAT_HISTORY[convo_id] = CHAT_HISTORY[convo_id][-40:]

def get_history(convo_id):
    return CHAT_HISTORY.get(convo_id, [])
