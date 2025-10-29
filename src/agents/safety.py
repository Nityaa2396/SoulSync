from __future__ import annotations
from typing import Optional

DISCLAIMER = (
    "I’m an AI helper here for reflection, not a licensed therapist. "
    "If you’re in distress or considering harm, please contact your local emergency services or a crisis hotline."
)

RISK_TERMS = ["hurt myself", "suicide", "kill myself", "end it", "no reason to live"]

def safety_check(user_text: Optional[str]) -> Optional[str]:
    # 🔒 Guard against None or empty input (Streamlit reruns can send None)
    if not user_text:
        return None

    low = user_text.lower()

    if any(term in low for term in RISK_TERMS):
        return (
            DISCLAIMER
            + " You’re not alone. Consider reaching out to a trusted person or professional for support right now. 💗"
        )

    return None
