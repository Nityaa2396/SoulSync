"""
Crisis Handler - Detects and responds to crisis situations
Provides appropriate escalation and resources.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re


class CrisisHandler:
    """Handles crisis detection and appropriate escalation."""
    
    # Crisis keywords by severity
    CRITICAL_KEYWORDS = [
        "kill myself", "end my life", "suicide", "want to die",
        "better off dead", "no reason to live", "plan to die",
        "hurt myself", "end it all", "can't go on"
    ]
    
    HIGH_KEYWORDS = [
        "self harm", "cutting", "overdose", "hurting myself",
        "harm others", "kill someone", "hurt them", "get revenge",
        "not safe", "danger", "violent thoughts"
    ]
    
    MEDIUM_KEYWORDS = [
        "hopeless", "can't take it", "give up", "pointless",
        "worthless", "burden", "everyone better without me",
        "don't want to be here", "rather not exist"
    ]
    
    LOW_KEYWORDS = [
        "depressed", "really down", "struggling", "hard to cope",
        "overwhelmed", "can't handle", "too much"
    ]
    
    def __init__(self):
        """Initialize crisis handler."""
        self.crisis_log = []
    
    def detect_crisis(self, message: str, user_id: str = None) -> Dict:
        """
        Detect if message indicates crisis situation.
        
        Args:
            message: User's message
            user_id: Optional user identifier
            
        Returns:
            Dictionary with crisis assessment
        """
        message_lower = message.lower()
        
        # Check for crisis keywords
        critical_found = [kw for kw in self.CRITICAL_KEYWORDS if kw in message_lower]
        high_found = [kw for kw in self.HIGH_KEYWORDS if kw in message_lower]
        medium_found = [kw for kw in self.MEDIUM_KEYWORDS if kw in message_lower]
        low_found = [kw for kw in self.LOW_KEYWORDS if kw in message_lower]
        
        # Determine severity
        if critical_found:
            severity = "critical"
            keywords = critical_found
        elif high_found:
            severity = "high"
            keywords = high_found
        elif medium_found:
            severity = "medium"
            keywords = medium_found
        elif low_found:
            severity = "low"
            keywords = low_found
        else:
            severity = "none"
            keywords = []
        
        # Log if crisis detected
        if severity != "none":
            self.crisis_log.append({
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "severity": severity,
                "keywords": keywords,
                "message_hash": hash(message)  # Don't store full message for privacy
            })
        
        return {
            "is_crisis": severity != "none",
            "severity": severity,
            "keywords_found": keywords,
            "requires_escalation": severity in ["critical", "high"],
            "action": self._get_action(severity)
        }
    
    def _get_action(self, severity: str) -> str:
        """Get recommended action based on severity."""
        actions = {
            "critical": "immediate_escalation",
            "high": "escalation_with_resources",
            "medium": "supportive_resources",
            "low": "monitor_and_support",
            "none": "continue_conversation"
        }
        return actions.get(severity, "continue_conversation")
    
    def get_crisis_response(self, severity: str, context: str = None) -> str:
        """
        Generate appropriate crisis response.
        
        Args:
            severity: Crisis severity level
            context: Optional context about the situation
            
        Returns:
            Crisis response message
        """
        if severity == "critical":
            return self._get_critical_response()
        elif severity == "high":
            return self._get_high_response()
        elif severity == "medium":
            return self._get_medium_response()
        elif severity == "low":
            return self._get_low_response()
        else:
            return ""
    
    def _get_critical_response(self) -> str:
        """Response for critical situations (suicidal/homicidal ideation)."""
        return """I hear that you're in a lot of pain right now, and I want you to know that your life matters.

**If you're thinking about harming yourself or someone else, please reach out for immediate help:**

🆘 **Crisis Resources:**
• **988 Suicide & Crisis Lifeline**: Call or text 988 (24/7)
• **Crisis Text Line**: Text HOME to 741741
• **Emergency Services**: Call 911 or go to your nearest emergency room

**International:**
• **International Association for Suicide Prevention**: https://www.iasp.info/resources/Crisis_Centres/

You don't have to face this alone. These trained professionals can provide the support you need right now.

If you're in immediate danger, please call emergency services (911 in the US) or go to your nearest emergency room.

Would you be willing to reach out to one of these resources? I'm here to support you through this."""

    def _get_high_response(self) -> str:
        """Response for high-risk situations (self-harm, violence)."""
        return """I'm concerned about what you're sharing. It sounds like you're going through something really serious.

**Please consider reaching out for professional support:**

📞 **Crisis Resources:**
• **988 Suicide & Crisis Lifeline**: Call or text 988
• **Crisis Text Line**: Text HOME to 741741
• **SAMHSA National Helpline**: 1-800-662-4357 (substance abuse and mental health)

**If you're in immediate danger, call 911 or go to your nearest emergency room.**

These feelings can be overwhelming, but help is available. Would you be open to talking to a crisis counselor who is trained to help with situations like yours?

I'm here to listen, but I want to make sure you have access to the professional support you deserve."""

    def _get_medium_response(self) -> str:
        """Response for medium-risk situations (hopelessness, despair)."""
        return """I hear how much pain you're carrying, and I'm really glad you're sharing this with me. What you're feeling matters.

While I'm here to listen and support you, I want to make sure you have access to additional resources:

💙 **Support Resources:**
• **988 Suicide & Crisis Lifeline**: Call or text 988 (if feelings intensify)
• **NAMI Helpline**: 1-800-950-6264 (mental health support)
• **Therapy/Counseling**: Consider reaching out to a licensed therapist

**Online Support:**
• r/SuicideWatch (Reddit community)
• 7 Cups (free emotional support chat)

These feelings of hopelessness are real, but they can change with the right support. You deserve to feel better.

Would you like to talk more about what's contributing to these feelings?"""

    def _get_low_response(self) -> str:
        """Response for low-risk situations (general distress)."""
        return """I hear that you're struggling, and I want you to know that reaching out is a brave thing to do.

If things feel like they're getting harder to manage, here are some resources that might help:

🌟 **Support Resources:**
• **NAMI Helpline**: 1-800-950-6264 (mental health support and information)
• **Psychology Today**: Find a therapist near you
• **Local support groups**: Check community centers or online platforms

**Self-Care:**
• Focus on basic needs (sleep, food, water)
• Reach out to trusted friends or family
• Consider journaling or creative expression
• Try grounding techniques when feeling overwhelmed

Remember, asking for help is a sign of strength, not weakness. Would you like to talk more about what you're experiencing?"""
    
    def get_resources(self, category: str = "general") -> List[Dict]:
        """
        Get relevant mental health resources.
        
        Args:
            category: Resource category (crisis, therapy, support_groups, etc.)
            
        Returns:
            List of resource dictionaries
        """
        resources = {
            "crisis": [
                {
                    "name": "988 Suicide & Crisis Lifeline",
                    "contact": "Call or text 988",
                    "description": "24/7 crisis support",
                    "availability": "24/7"
                },
                {
                    "name": "Crisis Text Line",
                    "contact": "Text HOME to 741741",
                    "description": "Free 24/7 text crisis support",
                    "availability": "24/7"
                },
                {
                    "name": "Emergency Services",
                    "contact": "911",
                    "description": "Immediate emergency response",
                    "availability": "24/7"
                }
            ],
            "therapy": [
                {
                    "name": "Psychology Today",
                    "contact": "psychologytoday.com/us/therapists",
                    "description": "Find licensed therapists near you",
                    "availability": "Directory"
                },
                {
                    "name": "BetterHelp",
                    "contact": "betterhelp.com",
                    "description": "Online therapy platform",
                    "availability": "Online"
                },
                {
                    "name": "Open Path Collective",
                    "contact": "openpathcollective.org",
                    "description": "Affordable therapy ($30-$80/session)",
                    "availability": "Directory"
                }
            ],
            "support_groups": [
                {
                    "name": "NAMI Support Groups",
                    "contact": "nami.org/Support-Education/Support-Groups",
                    "description": "Peer support groups for mental health",
                    "availability": "Varies by location"
                },
                {
                    "name": "DBSA Support Groups",
                    "contact": "dbsalliance.org/support/chapters-and-support-groups",
                    "description": "Depression and bipolar support",
                    "availability": "Varies by location"
                },
                {
                    "name": "7 Cups",
                    "contact": "7cups.com",
                    "description": "Free emotional support chat",
                    "availability": "24/7 online"
                }
            ],
            "general": [
                {
                    "name": "SAMHSA National Helpline",
                    "contact": "1-800-662-4357",
                    "description": "Substance abuse and mental health",
                    "availability": "24/7"
                },
                {
                    "name": "NAMI Helpline",
                    "contact": "1-800-950-6264",
                    "description": "Mental health information and support",
                    "availability": "Mon-Fri 10am-10pm ET"
                },
                {
                    "name": "MentalHealth.gov",
                    "contact": "mentalhealth.gov",
                    "description": "Federal mental health resources",
                    "availability": "Online resource"
                }
            ]
        }
        
        return resources.get(category, resources["general"])
    
    def should_restrict_conversation(self, severity: str) -> bool:
        """
        Determine if conversation should be restricted (only crisis resources).
        
        Args:
            severity: Crisis severity level
            
        Returns:
            True if conversation should focus only on crisis resources
        """
        return severity in ["critical", "high"]
    
    def get_follow_up_message(self, severity: str) -> str:
        """
        Get appropriate follow-up message after crisis response.
        
        Args:
            severity: Crisis severity level
            
        Returns:
            Follow-up message
        """
        if severity == "critical":
            return "Have you been able to reach out to any of the crisis resources? I'm here with you."
        elif severity == "high":
            return "I'm here to listen. Have you considered reaching out to the crisis line?"
        elif severity == "medium":
            return "How are you feeling now? Would you like to talk more about what's going on?"
        elif severity == "low":
            return "What would be most helpful for you right now?"
        else:
            return ""
    
    def log_crisis_event(self, user_id: str, severity: str, 
                        action_taken: str, resolved: bool = False):
        """
        Log crisis event for tracking and analysis.
        
        Args:
            user_id: User identifier
            severity: Crisis severity
            action_taken: What action was taken
            resolved: Whether crisis was resolved
        """
        self.crisis_log.append({
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "severity": severity,
            "action_taken": action_taken,
            "resolved": resolved
        })
    
    def get_crisis_statistics(self, user_id: Optional[str] = None) -> Dict:
        """
        Get statistics about crisis events.
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            Dictionary with crisis statistics
        """
        logs = self.crisis_log
        
        if user_id:
            logs = [log for log in logs if log.get("user_id") == user_id]
        
        if not logs:
            return {
                "total_events": 0,
                "by_severity": {},
                "resolved_count": 0
            }
        
        by_severity = {}
        for log in logs:
            severity = log.get("severity", "unknown")
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        resolved_count = len([log for log in logs if log.get("resolved", False)])
        
        return {
            "total_events": len(logs),
            "by_severity": by_severity,
            "resolved_count": resolved_count,
            "resolution_rate": resolved_count / len(logs) if logs else 0
        }


# Example usage
if __name__ == "__main__":
    handler = CrisisHandler()
    
    # Test crisis detection
    test_messages = [
        "I want to kill myself",
        "I'm thinking about self harm",
        "I feel so hopeless",
        "I'm just feeling down today"
    ]
    
    for msg in test_messages:
        result = handler.detect_crisis(msg, user_id="test_user")
        print(f"\nMessage: '{msg}'")
        print(f"Crisis: {result['is_crisis']}")
        print(f"Severity: {result['severity']}")
        
        if result['is_crisis']:
            response = handler.get_crisis_response(result['severity'])
            print(f"\nResponse:\n{response[:200]}...")