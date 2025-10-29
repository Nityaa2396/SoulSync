from __future__ import annotations
from typing import Dict

def reflect(agent_name: str, user_text: str, agent_text: str) -> Dict[str, float]:
    """Tiny heuristic reflection stub. Extend with LLM grading in Week 3."""
    empathy = 0.7 if any(w in agent_text.lower() for w in ["i hear", "understand", "valid"]) else 0.3
    clarity = 0.7 if len(agent_text.split()) > 12 else 0.4
    return {"empathy": empathy, "clarity": clarity}
