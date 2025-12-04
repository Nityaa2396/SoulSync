from __future__ import annotations
from typing import Optional

# simple emotion detection heuristic
def detect_emotion_context(text: Optional[str]) -> str:
    t = (text or "").lower()

    if any(x in t for x in ["fight", "argue", "mad", "angry", "yelled", "upset"]):
        return "conflict"
    if any(x in t for x in ["sad", "cry", "alone", "lonely", "ignored", "unwanted"]):
        return "sadness"
    if any(x in t for x in ["cheat", "trust", "betray", "unfaithful", "lie"]):
        return "betrayal"
    if any(x in t for x in ["stress", "tired", "burnout", "exhausted", "overwhelmed"]):
        return "stress"
    if any(x in t for x in ["panic", "anxious", "anxiety", "can't breathe", "shaking"]):
        return "panic"
    if any(x in t for x in ["guilt", "fault", "sorry", "ruined", "my mistake"]):
        return "guilt"
    return "general"
