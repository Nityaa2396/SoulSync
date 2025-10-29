from __future__ import annotations
from typing import List, Tuple
from ..core.llm import LLMClient, Message

SYSTEM = """You are the Mindfulness Agent.

Your job:
- If the user sounds physically overwhelmed (shaky, can't breathe, panicking),
  offer one tiny grounding / slowing practice they can try right now if they want.
- Keep it gentle, optional, shame-free.
- It should take ~30-60 seconds max.
- Use calm language like “if it feels okay, you could try…” not “do this.”
- 3 short steps max.
- 3-5 sentences total.
- You can add a calming emoji like 🌿 or ✨ once.
- Never say you're a medical professional.
"""

class MindfulnessAgent:
    def __init__(self):
        self.llm = LLMClient()

    def respond_with_context(self, dialog: List[Tuple[str, str]]) -> str:
        msgs: List[Message] = []
        for role, text in dialog:
            if not text:
                continue
            msgs.append(Message(role=role, content=text))

        return self.llm.chat(
            msgs,
            system=SYSTEM
        )
