from __future__ import annotations
from typing import Dict, Optional

class MemoryHelper:
    """Helper for offering to save insights to user's journal."""
    
    INSIGHT_INDICATORS = [
        "maybe", "i think", "that makes sense", "oh", "yeah", "true",
        "i guess", "probably", "you're right"
    ]
    
    @staticmethod
    def should_offer_save(
        user_message: str,
        agent_response: str,
        turn_number: int
    ) -> bool:
        """
        Determine if we should offer to save this insight to memory.
        
        Offer when:
        1. User shows recognition ("maybe", "oh", "that makes sense")
        2. Agent provided meaningful insight (contains "pattern", "when", "why")
        3. Not too early in conversation (turn 3+)
        """
        if turn_number < 3:
            return False
        
        # Check if user is showing recognition
        user_lower = user_message.lower()
        has_recognition = any(indicator in user_lower for indicator in MemoryHelper.INSIGHT_INDICATORS)
        
        # Check if agent provided insight
        agent_lower = agent_response.lower()
        insight_words = ["pattern", "when you", "because", "why", "notice", "tends to"]
        has_insight = any(word in agent_lower for word in insight_words)
        
        return has_recognition and has_insight
    
    @staticmethod
    def generate_save_offer(insight: str) -> str:
        """Generate a natural offer to save the insight."""
        return (
            f"\n\n💭 This feels like an important realization. "
            f"Would you like me to save it to your journal? (yes/no)"
        )
    
    @staticmethod
    def extract_insight(agent_response: str, user_message: str) -> str:
        """Extract the key insight from the conversation turn."""
        # Simple extraction - take the key sentence
        sentences = agent_response.split(". ")
        
        # Look for sentences with insight indicators
        for sentence in sentences:
            if any(word in sentence.lower() for word in ["when", "pattern", "because", "why"]):
                return sentence.strip()
        
        # Fallback to first sentence
        return sentences[0] if sentences else agent_response