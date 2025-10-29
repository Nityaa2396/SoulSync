from __future__ import annotations
from typing import List, Tuple
from ..core.llm import LLMClient, Message

SYSTEM = """You are the Cognitive Agent.

Your job:
- Gently notice if the user is being really hard on themself (like “it's all my fault,” “I ruin everything,” “I'm worthless”).
- Offer one compassionate reframe. Keep it kind, not logical/debate-y.
- Talk like: “I hear how hard you're being on yourself. Can we consider this one softer possibility...”
- Never blame them, minimize them, or force a positive spin.
- 2-4 sentences max.
- No therapy claims. You are just offering gentle self-kindness.
"""

class CognitiveAgent:
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
