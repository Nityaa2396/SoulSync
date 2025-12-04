from __future__ import annotations
from typing import Optional

DISCLAIMER = (
    "I’m an AI helper here for reflection, not a licensed therapist. "
    "If you’re in distress or considering harm, please contact your local emergency services or a crisis hotline."
)

RISK_TERMS = ["hurt myself", "suicide", "kill myself", "end it", "no reason to live"]

class SafetyAgent:
    def check(self, user_message, emotion_tag):
        risk_keywords = [
            "escape", "nothing matters", "give up", 
            "end it", "better off dead", "no point"
        ]
        risk_emotions = ["hopeless", "desperate", "suicidal"]
        
        if any(kw in user_message.lower() for kw in risk_keywords):
            return self.safety_protocol()
        if emotion_tag in risk_emotions:
            return self.safety_protocol()
        return None
    
    def safety_protocol(self):
        return """I'm hearing real pain in what you're sharing. 
        Before we continue - are you feeling like you might hurt 
        yourself or that you're unsafe right now? 
        
        If yes:
        • 988 Suicide & Crisis Lifeline (call/text)
        • Crisis Text Line: Text HOME to 741741
        • Emergency: Call 911
        
        Please tell me honestly - are you safe right now?"""

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
