from History import BufferWindowMessageHistory

class SessionMemoryManager:
    session_memory_map = {}  

    @staticmethod
    def get_session(session_id: str, k: int = 3):
        if session_id not in SessionMemoryManager.session_memory_map:
            SessionMemoryManager.session_memory_map[session_id] = BufferWindowMessageHistory(k=k)
        return SessionMemoryManager.session_memory_map[session_id]

    @staticmethod
    def clear_session(session_id: str):
        if session_id in SessionMemoryManager.session_memory_map:
            del SessionMemoryManager.session_memory_map[session_id]

    @staticmethod
    def clear_all():
        SessionMemoryManager.session_memory_map.clear()