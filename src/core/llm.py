from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI

@dataclass
class Message:
    role: str
    content: str

class LLMClient:
    """
    Thin wrapper with provider switch.
    Week 1: we implement OpenAI.
    Later we can add Anthropic / Bedrock branches.
    """
    def __init__(self):
        self.provider = os.getenv("PROVIDER", "openai")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620")
        self._openai_client = None

        if self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError("Missing OPENAI_API_KEY in .env")
            self._openai_client = OpenAI(api_key=api_key)

    def chat(self, messages: List[Message], system: Optional[str] = None) -> str:
        """
        Send messages to the chosen provider and return the assistant text.
        messages = [Message(role="user", content="..."), ...]
        system = system prompt for that agent (listener, cognitive, etc.)
        """
        if self.provider == "openai":
            # Build OpenAI-style messages list: system -> history -> user
            openai_messages: List[Dict[str, str]] = []
            if system:
                openai_messages.append({"role": "system", "content": system})
            for m in messages:
                 # 🧩 Guard: skip any empty or None content to avoid API 400 error
               if not m.content:
                continue
                # Map our Message dataclass to OpenAI role/content
                openai_messages.append({
                    "role": m.role,
                    "content": m.content
                })

            resp = self._openai_client.chat.completions.create(
                model=self.openai_model,
                messages=openai_messages,
                temperature=0.7,
                max_tokens=300,
            )

            # pull assistant text
            return resp.choices[0].message.content.strip()

        # if provider isn't implemented yet, fallback instead of crashing
        joined = "\n".join([f"{m.role.upper()}: {m.content}" for m in messages[-4:]])
        return f"[unimplemented-{self.provider}] {joined}"
