from __future__ import annotations
from typing import Dict
from ..core.router import route_and_merge

class SupervisorAgent:
    def merge(self, responses: Dict[str, str], user_text: str) -> str:
        return route_and_merge(responses, user_text)
