import uuid
import json
from typing import Dict, Any
from datetime import datetime


class SessionCache:
    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._max_sessions_created = {}

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = {
            'data': None,
            'column_widths': None,
            'role': None,
            'created_at': datetime.now().isoformat(),
            'modified_at': datetime.now().isoformat(),
        }
        return session_id

    def get_session(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self._sessions:
            return None
        return self._sessions[session_id]

    def update_data(self, session_id: str, data: Any):
        if session_id in self._sessions:
            self._sessions[session_id]['data'] = data
            self._sessions[session_id]['modified_at'] = datetime.now().isoformat()

    def update_column_widths(self, session_id: str, widths: Dict[str, int]):
        if session_id in self._sessions:
            self._sessions[session_id]['column_widths'] = widths
            self._sessions[session_id]['modified_at'] = datetime.now().isoformat()

    def set_role(self, session_id: str, role: str):
        if session_id in self._sessions:
            self._sessions[session_id]['role'] = role

    def get_data(self, session_id: str) -> Any:
        session = self.get_session(session_id)
        return session['data'] if session else None

    def get_column_widths(self, session_id: str) -> Dict[str, int]:
        session = self.get_session(session_id)
        return session['column_widths'] if session else None

    def get_role(self, session_id: str) -> str:
        session = self.get_session(session_id)
        return session['role'] if session else None

    def export_session_data(self, session_id: str) -> str:
        session = self.get_session(session_id)
        if not session:
            return ''
        export_data = {
            'data': session['data'],
            'column_widths': session['column_widths'],
            'exported_at': datetime.now().isoformat(),
        }
        return json.dumps(export_data, ensure_ascii=False, indent=2)


session_cache = SessionCache()
