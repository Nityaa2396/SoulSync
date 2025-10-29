from __future__ import annotations
from typing import Dict, Optional

def looks_like_self_blame(user_text: Optional[str]) -> bool:
    low = user_text.lower()
    return any(phrase in low for phrase in [
        "it's my fault",
        "its my fault",
        "i ruin everything",
        "i'm the problem",
        "im the problem",
        "i'm not good enough",
        "im not good enough",
        "i'm worthless",
        "im worthless",
        "he's right about me",
        "she's right about me",
        "he is right about me",
        "she is right about me",
    ])

def looks_like_overwhelm(user_text: Optional[str]) -> bool:
    low = user_text.lower()
    return any(phrase in low for phrase in [
        "i can't breathe",
        "i cant breathe",
        "i'm freaking out",
        "im freaking out",
        "i'm overwhelmed",
        "im overwhelmed",
        "i'm panicking",
        "im panicking",
        "i feel like i'm breaking",
        "i feel like im breaking",
        "i feel like i'm drowning",
        "i feel like im drowning",
        "i'm shaking",
        "im shaking",
    ])

def route_and_merge(responses: Dict[str, str], user_text: Optional[str]) -> str:
    """
    Build the final response in a way that feels human:
    - Stay with their feeling first (Listener)
    - Only add gentle cognitive kindness if they're blaming themselves
    - Only add grounding if they're overwhelmed
    - No long essays, no lecture tone
    """

    listener = (responses.get("listener") or "").strip()
    cognitive = (responses.get("cognitive") or "").strip()
    mindfulness = (responses.get("mindfulness") or "").strip()

    final_chunks = []

    # 1. Listener is always included and is the main emotional mirror.
    if listener:
        final_chunks.append(listener)

    # 2. If they're attacking themselves, offer a tiny self-kindness nudge (not a full CBT lecture).
    if looks_like_self_blame(user_text) and cognitive:
        final_chunks.append(
             "I just want to gently hold one thing with you 💗:\n"
              + cognitive
        )


    # 3. If they're overwhelmed or spiraling physically, offer short grounding.
    elif looks_like_overwhelm(user_text) and mindfulness:
        final_chunks.append(
              "Your body sounds like it's carrying a lot right now. "
               "If it helps, we can slow down for a few breaths together ✨:\n"
               + mindfulness
             )


    # Join the parts we decided to include.
    final = "\n\n".join([p for p in final_chunks if p]).strip()

    # 4. Fallback if somehow empty.
    if not final:
        final = (
            "I'm here with you. It sounds like that landed really hard. 💗 "
            "If you want to share the part that hurt the most, I'm listening. "
            "If you'd rather not talk details, that's totally okay too."
        )

    return final
