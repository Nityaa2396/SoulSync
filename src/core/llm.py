from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Iterator
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Message:
    role: str
    content: str

class LLMClient:
    """
    Thin wrapper with provider switch.
    Supports OpenAI and Anthropic (Claude).
    Now includes streaming support for real-time responses.
    
    ✅ FIXED: Defaults to Anthropic, removes OpenAI import if not needed
    """
    def __init__(self):
        # ✅ FIX 1: Default to anthropic (not openai)
        self.provider = os.getenv("PROVIDER", "anthropic").lower()
        
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        self._openai_client = None
        self._anthropic_client = None

        if self.provider == "openai":
            # Only import OpenAI if actually using it
            try:
                from openai import OpenAI
            except ImportError:
                raise RuntimeError("Install openai: pip install openai")
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError("Missing OPENAI_API_KEY in .env or Streamlit secrets")
            self._openai_client = OpenAI(api_key=api_key)
        
        elif self.provider == "anthropic":
            # Better error message for missing Anthropic key
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise RuntimeError(
                    "Missing ANTHROPIC_API_KEY in .env or Streamlit secrets. "
                    "Add it to Settings → Secrets in Streamlit Cloud."
                )
            try:
                import anthropic
                self._anthropic_client = anthropic.Anthropic(api_key=api_key)
            except ImportError:
                raise RuntimeError("Install anthropic: pip install anthropic")
        
        else:
            raise ValueError(f"Unknown PROVIDER '{self.provider}'. Use 'openai' or 'anthropic'")

    def chat(self, messages: List[Message], system: Optional[str] = None) -> str:
        """
        Send messages to the chosen provider and return the assistant text.
        messages = [Message(role="user", content="..."), ...]
        system = system prompt for that agent (listener, cognitive, etc.)
        
        This is the NON-STREAMING version (original behavior).
        """
        
        # === OPENAI ===
        if self.provider == "openai":
            from openai import OpenAI  # Import only when needed
            
            openai_messages: List[Dict[str, str]] = []
            if system:
                openai_messages.append({"role": "system", "content": system})
            
            for m in messages:
                if not m.content:
                    continue
                openai_messages.append({
                    "role": m.role,
                    "content": m.content
                })

            resp = self._openai_client.chat.completions.create(
                model=self.openai_model,
                messages=openai_messages,
                temperature=0.8,  # Higher = more creative, less formulaic
                max_tokens=800,
            )

            return resp.choices[0].message.content.strip()
        
        # === ANTHROPIC (CLAUDE) ===
        elif self.provider == "anthropic":
            # Claude requires system prompt separate from messages
            # and doesn't accept system messages in the messages array
            anthropic_messages = []
            
            for m in messages:
                if not m.content:
                    continue
                # Claude uses same role names as OpenAI
                anthropic_messages.append({
                    "role": m.role,
                    "content": m.content
                })
            
            resp = self._anthropic_client.messages.create(
                model=self.anthropic_model,
                system=system or "You are a helpful assistant.",
                messages=anthropic_messages,
                temperature=0.8,
                max_tokens=800,
            )
            
            return resp.content[0].text.strip()
        
        # Fallback
        joined = "\n".join([f"{m.role.upper()}: {m.content}" for m in messages[-4:]])
        return f"[unimplemented-{self.provider}] {joined}"

    def chat_stream(self, messages: List[Message], system: Optional[str] = None) -> Iterator[str]:
        """
        STREAMING version - yields text chunks as they arrive from the LLM.
        
        Usage:
            for chunk in llm.chat_stream(messages, system):
                print(chunk, end="", flush=True)
        
        Returns an iterator that yields string chunks.
        """
        
        # === OPENAI STREAMING ===
        if self.provider == "openai":
            from openai import OpenAI  # Import only when needed
            
            openai_messages: List[Dict[str, str]] = []
            if system:
                openai_messages.append({"role": "system", "content": system})
            
            for m in messages:
                if not m.content:
                    continue
                openai_messages.append({
                    "role": m.role,
                    "content": m.content
                })

            stream = self._openai_client.chat.completions.create(
                model=self.openai_model,
                messages=openai_messages,
                temperature=0.8,
                max_tokens=800,
                stream=True  # Enable streaming
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        # === ANTHROPIC (CLAUDE) STREAMING ===
        elif self.provider == "anthropic":
            anthropic_messages = []
            
            for m in messages:
                if not m.content:
                    continue
                anthropic_messages.append({
                    "role": m.role,
                    "content": m.content
                })
            
            # Claude streaming uses a different API
            with self._anthropic_client.messages.stream(
                model=self.anthropic_model,
                system=system or "You are a helpful assistant.",
                messages=anthropic_messages,
                temperature=0.8,
                max_tokens=800,
            ) as stream:
                for text in stream.text_stream:
                    yield text
        
        else:
            # Fallback: just yield the full response at once
            result = self.chat(messages, system)
            yield result