from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Iterator
import os
from dotenv import load_dotenv
import anthropic

load_dotenv()
def get_secret(key: str, default: str = None) -> Optional[str]:
    """Get secret from Streamlit Cloud or fall back to env vars."""
    try:
        import streamlit as st
        return st.secrets.get(key) or os.getenv(key, default)
    except Exception:
        return os.getenv(key, default)

@dataclass
class Message:
    role: str
    content: str

class LLMClient:
    """
    ANTHROPIC-ONLY VERSION
    Removed all OpenAI code to fix deployment issues.
    """
    def __init__(self):
        # Get API key from environment
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "❌ ANTHROPIC_API_KEY not found!\n"
                "Add it to Streamlit Cloud: Settings → Secrets\n"
                "ANTHROPIC_API_KEY = \"sk-ant-api03-...\""
            )
        
        # Initialize Anthropic client
        self._anthropic_client = anthropic.Anthropic(api_key=api_key)
        
        # Model configuration
        self.anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

    def chat(self, messages: List[Message], system: Optional[str] = None) -> str:
        """
        Send messages to Claude and return response.
        """
        # Build messages array
        anthropic_messages = []
        for m in messages:
            if not m.content:
                continue
            anthropic_messages.append({
                "role": m.role,
                "content": m.content
            })
        
        # Call Claude API
        resp = self._anthropic_client.messages.create(
            model=self.anthropic_model,
            system=system or "You are a helpful assistant.",
            messages=anthropic_messages,
            temperature=0.8,
            max_tokens=800,
        )
        
        return resp.content[0].text.strip()

    def chat_stream(self, messages: List[Message], system: Optional[str] = None) -> Iterator[str]:
        """
        Streaming version - yields text chunks from Claude.
        """
        # Build messages array
        anthropic_messages = []
        for m in messages:
            if not m.content:
                continue
            anthropic_messages.append({
                "role": m.role,
                "content": m.content
            })
        
        # Stream from Claude
        with self._anthropic_client.messages.stream(
            model=self.anthropic_model,
            system=system or "You are a helpful assistant.",
            messages=anthropic_messages,
            temperature=0.8,
            max_tokens=800,
        ) as stream:
            for text in stream.text_stream:
                yield text