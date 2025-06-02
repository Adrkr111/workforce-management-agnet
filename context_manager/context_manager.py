from collections import defaultdict

class ContextManager:
    def __init__(self):
        self.sessions = defaultdict(list)

    def get_history(self, session_id):
        return self.sessions[session_id]

    def add_message(self, session_id, message_dict):
        self.sessions[session_id].append(message_dict)

    def clear(self, session_id):
        self.sessions[session_id] = []
