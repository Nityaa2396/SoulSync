"""
OARS Policy - Motivational Interviewing Framework
O = Open questions
A = Affirmations  
R = Reflections
S = Summaries

Ensures therapeutic quality in responses.
"""

from typing import Dict, List, Optional
import random


class OARSPolicy:
    """Validates and enhances responses using OARS principles."""
    
    # Open questions that explore without judgment
    OPEN_QUESTIONS = [
        "What does that feel like for you?",
        "How has this been affecting you?",
        "What would it mean to you if that changed?",
        "Can you tell me more about what that's like?",
        "What do you think might help with this?",
        "How long have you been feeling this way?",
        "What's been on your mind about this?",
        "What matters most to you in this situation?",
        "How do you make sense of what happened?",
        "What do you need right now?"
    ]
    
    # Affirmations that recognize strength
    AFFIRMATIONS = [
        "It takes courage to share that.",
        "You're being really honest with yourself right now.",
        "That's a lot to carry.",
        "You're doing your best in a hard situation.",
        "I hear how much this matters to you.",
        "You're showing up even when it's difficult.",
        "That takes real strength to acknowledge.",
        "You're being incredibly vulnerable right now.",
        "You're facing this head-on.",
        "That kind of self-awareness is powerful."
    ]
    
    # Reflection starters for mirroring emotions
    REFLECTION_STARTERS = [
        "It sounds like you're feeling",
        "What I'm hearing is",
        "It seems like",
        "You're noticing that",
        "There's a sense that",
        "It feels like",
        "I hear",
        "What stands out is",
        "You're experiencing",
        "It appears that"
    ]
    
    # Summary starters for validation
    SUMMARY_STARTERS = [
        "So if I understand correctly",
        "Let me reflect back what you've shared",
        "From what you've told me",
        "It sounds like several things are happening",
        "What I'm taking from this is",
        "To summarize what you're going through"
    ]
    
    def __init__(self):
        self.last_responses = []  # Track to avoid repetition
        self.last_affirmations = []  # Track affirmations separately
        
    def validate_response(self, response: str) -> Dict[str, any]:
        """
        Check if response follows OARS principles.
        
        Args:
            response: The response to validate
            
        Returns:
            Dict with validation results
        """
        response_lower = response.lower()
        
        # Check for OARS elements
        has_open_question = any(q in response_lower for q in [
            "what", "how", "when", "where", "can you tell me", "would you"
        ])
        
        has_affirmation = any(phrase in response_lower for phrase in [
            "courage", "strength", "honest", "brave", "matters", "doing your best"
        ])
        
        has_reflection = any(r in response_lower for r in [
            "sounds like", "seems like", "hearing", "feels like", "sense that"
        ])
        
        has_summary = any(s in response_lower for s in [
            "understand", "reflect back", "from what", "summarize"
        ])
        
        # Calculate quality score
        score = sum([has_open_question, has_affirmation, has_reflection, has_summary])
        
        return {
            "valid": score >= 1,  # At least one OARS element
            "has_open_question": has_open_question,
            "has_affirmation": has_affirmation,
            "has_reflection": has_reflection,
            "has_summary": has_summary,
            "score": score,
            "quality": "high" if score >= 3 else "medium" if score >= 2 else "basic"
        }
    
    def get_reflection_template(self, emotion: str) -> str:
        """
        Get appropriate reflection for detected emotion.
        
        Args:
            emotion: Detected emotion (sadness, anger, etc.)
            
        Returns:
            Reflection string
        """
        templates = {
            "sadness": "It sounds like you're carrying a lot of sadness right now.",
            "anger": "I hear a lot of frustration in what you're sharing.",
            "anxiety": "It seems like worry is taking up a lot of space for you.",
            "fear": "I sense there's real fear underneath this.",
            "shame": "That sounds like it's bringing up some painful feelings about yourself.",
            "loneliness": "It sounds like feeling alone is really hard right now.",
            "betrayal": "I hear how deeply that hurt you.",
            "grief": "It sounds like you're grieving something important.",
            "overwhelm": "That sounds incredibly overwhelming.",
            "confusion": "It seems like you're trying to make sense of a lot right now.",
            "hopelessness": "I hear how heavy this feels for you.",
            "guilt": "It sounds like you're carrying a lot of guilt about this.",
        }
        
        return templates.get(emotion, "What I'm hearing is that this is really hard for you.")
    
    def check_repetition(self, response: str, max_history: int = 3) -> bool:
        """
        Check if response is too similar to recent responses.
        
        Args:
            response: New response to check
            max_history: How many past responses to check
            
        Returns:
            True if response is too repetitive
        """
        if not self.last_responses:
            return False
        
        # Check similarity with recent responses
        for prev in self.last_responses[-max_history:]:
            similarity = self._calculate_similarity(response, prev)
            if similarity > 0.7:  # 70% similar = too repetitive
                return True
                
        return False
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate word overlap similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     'of', 'with', 'by', 'from', 'is', 'was', 'are', 'were', 'been', 'be',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                     'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
        
        words1 = words1 - stop_words
        words2 = words2 - stop_words
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def track_response(self, response: str):
        """
        Add response to history for repetition checking.
        
        Args:
            response: Response to track
        """
        self.last_responses.append(response)
        if len(self.last_responses) > 10:
            self.last_responses.pop(0)  # Keep only last 10
    
    def suggest_followup(self, emotion: str, context: str) -> str:
        """
        Suggest appropriate follow-up question based on context.
        
        Args:
            emotion: Detected emotion
            context: User's message context
            
        Returns:
            Follow-up question
        """
        context_lower = context.lower()
        
        # Context-specific questions
        if any(word in context_lower for word in ["work", "job", "boss", "colleague"]):
            return "How is this affecting your work life?"
        elif any(word in context_lower for word in ["relationship", "partner", "spouse", "boyfriend", "girlfriend"]):
            return "What would you want to change about this situation?"
        elif any(word in context_lower for word in ["family", "mom", "dad", "parent", "sibling"]):
            return "How does your family fit into what you're experiencing?"
        elif any(word in context_lower for word in ["friend", "friends", "social"]):
            return "How are your friendships being affected by this?"
        elif any(word in context_lower for word in ["school", "college", "class", "student"]):
            return "How is this impacting your studies?"
        else:
            return random.choice(self.OPEN_QUESTIONS)
    
    def enhance_response(self, response: str, emotion: str, context: str) -> str:
        """
        Enhance response by adding OARS elements if missing.
        
        Args:
            response: Original response
            emotion: Detected emotion
            context: User context
            
        Returns:
            Enhanced response
        """
        validation = self.validate_response(response)
        
        # If already high quality, return as-is
        if validation["quality"] == "high":
            return response
        
        enhanced = response
        
        # Add reflection if missing
        if not validation["has_reflection"]:
            reflection = self.get_reflection_template(emotion)
            enhanced = f"{reflection} {enhanced}"
        
        # Add open question if missing
        if not validation["has_open_question"]:
            question = self.suggest_followup(emotion, context)
            enhanced = f"{enhanced}\n\n{question}"
        
        # Add affirmation if missing (but not every time)
        if not validation["has_affirmation"] and random.random() > 0.5:
            affirmation = random.choice(self.AFFIRMATIONS)
            # Avoid repeating recent affirmations
            while affirmation in self.last_affirmations[-3:]:
                affirmation = random.choice(self.AFFIRMATIONS)
            self.last_affirmations.append(affirmation)
            if len(self.last_affirmations) > 5:
                self.last_affirmations.pop(0)
            enhanced = f"{affirmation} {enhanced}"
        
        return enhanced
    
    def get_quality_feedback(self, response: str) -> str:
        """
        Get feedback on response quality for debugging.
        
        Args:
            response: Response to evaluate
            
        Returns:
            Quality feedback string
        """
        validation = self.validate_response(response)
        
        feedback = f"Quality: {validation['quality'].upper()} (Score: {validation['score']}/4)\n"
        feedback += f"✓ Open Question: {validation['has_open_question']}\n"
        feedback += f"✓ Affirmation: {validation['has_affirmation']}\n"
        feedback += f"✓ Reflection: {validation['has_reflection']}\n"
        feedback += f"✓ Summary: {validation['has_summary']}\n"
        
        return feedback


# Example usage
if __name__ == "__main__":
    oars = OARSPolicy()
    
    # Test response
    test_response = "That sounds really difficult. What has been the hardest part for you?"
    
    validation = oars.validate_response(test_response)
    print(f"Valid: {validation['valid']}")
    print(f"Quality: {validation['quality']}")
    print(f"Score: {validation['score']}/4")
    
    # Get quality feedback
    print("\n" + oars.get_quality_feedback(test_response))