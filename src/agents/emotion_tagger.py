from __future__ import annotations
from typing import List, Tuple
from ..core.llm import LLMClient, Message

SYSTEM = """You are an Emotion Tagger.

Given the user's most recent message, label the PRIMARY emotional theme using one of these buckets:

- LONELY / UNWANTED (no one cares about me, nobody likes me, I'm left out)
- SELF-BLAME / SHAME (it's my fault, I'm the problem, I'm not good enough)
- PANIC / OVERWHELM (I'm shaking, I can't breathe, I can't calm down)
- ANGER / HURT (they hurt me, we fought, I'm mad, I feel disrespected)
- EXHAUSTION / EMPTY (tired, numb, I don't feel anything, done with everything)

Return a JSON object with:
{ "tag": "...", "summary": "short plain-language summary of what hurts" }

The summary should be 1 short sentence in plain emotional language.
Do NOT give advice.
Do NOT be clinical.
"""

class EmotionTaggerAgent:
    def __init__(self):
        self.llm = LLMClient()

    def tag_latest(self, user_text: str) -> dict:
        msgs = [
            Message(role="user", content=user_text)
        ]
        raw = self.llm.chat(msgs, system=SYSTEM)
        # We will try a naive eval-ish parse here. We'll be defensive:
        try:
            import json
            data = json.loads(raw)
            if "tag" in data and "summary" in data:
                return data
        except Exception:
            pass
        # fallback if model didn't give valid JSON:
        return {"tag": "UNKNOWN", "summary": raw[:200]}
