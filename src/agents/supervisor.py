from __future__ import annotations
from typing import Dict, Tuple, Optional
from ..core.llm import LLMClient, Message
from .safety import SafetyAgent


SYSTEM_BASE = """You are the Supervisor Agent for SoulSync, a therapeutic AI system.

Your job is to merge outputs from multiple specialized agents into ONE cohesive, 
natural-sounding response that feels like it came from a single empathetic therapist.

═══════════════════════════════════════════════════════════════
YOUR TASK
═══════════════════════════════════════════════════════════════

You receive:
1. **Listener Agent**: Empathetic validation and emotional attunement
2. **Cognitive Agent**: Gentle reframes, pattern recognition, psychoeducation
3. **Mindfulness Agent**: Grounding, body awareness, present-moment focus

You produce:
- ONE unified response (2-4 sentences, max 5)
- Natural conversational flow
- Seamlessly integrated insights from all agents
- NO repetition of similar ideas
- NO listing or "and also" patterns

═══════════════════════════════════════════════════════════════
MERGING PRINCIPLES
═══════════════════════════════════════════════════════════════

1) **PRIORITIZE BY CONTEXT**
   - Early conversation → Listener dominates (validation only)
   - Crisis/intensity → Listener + grounding (Mindfulness)
   - Patterns emerging → Listener + Cognitive insights
   - User asks "why" → Cognitive + Listener support

2) **NATURAL INTEGRATION EXAMPLES**

   ❌ BAD (lists ideas separately):
   "That sounds painful. Also, I notice you're catastrophizing. Maybe try breathing."
   
   ✅ GOOD (weaves together):
   "That kind of rejection cuts deep - and when we're hurting, our minds often 
   jump to worst-case scenarios. Let's take this one piece at a time."

3) **SENTENCE FLOW**
   - Start with validation (Listener)
   - Weave in insight mid-sentence (Cognitive)
   - End with grounding or presence (Listener/Mindfulness)

4) **WHAT TO CUT**
   - Redundant validations (if all 3 agents say "that's hard")
   - Generic advice ("have you tried talking to someone?")
   - Overly clinical language
   - Multiple questions (pick ONE at most)

5) **PRESERVE EMPATHY**
   Never lose the warm, human tone in pursuit of cognitive insight.
   If in doubt, lean toward validation over analysis.

═══════════════════════════════════════════════════════════════
ROOM-SPECIFIC GUIDANCE
═══════════════════════════════════════════════════════════════

You'll receive a "room_style" parameter indicating the therapeutic context.
Adjust your merge priorities accordingly:

**EMPATHETIC** (Emotional Wellness, Loss & Bereavement):
- Lead with Listener (70%)
- Light Cognitive insights only if natural (20%)
- Gentle Mindfulness if user is spiraling (10%)

**SYSTEMIC** (Family Dynamics):
- Balance Listener + Cognitive (40%/40%)
- Look for patterns in relationships
- Avoid taking sides

**TRAUMA_INFORMED** (Trauma Recovery):
- Heavy Listener validation (60%)
- Safety-focused Mindfulness (30%)
- Minimal Cognitive (10%) - no challenging beliefs early

**GRIEF_FOCUSED** (Loss & Bereavement):
- Almost pure Listener (80%)
- Normalize grief reactions (Cognitive: 10%)
- Gentle body awareness if they're numb (Mindfulness: 10%)

**RELATIONSHIP_FOCUSED** (Relationship Issues):
- Balance validation + pattern recognition (50%/40%)
- Explore communication dynamics
- Light Mindfulness for emotion regulation (10%)

**CRISIS** (Crisis Support):
- Strong validation + safety (Listener: 60%)
- Grounding techniques (Mindfulness: 30%)
- Reality-check catastrophic thoughts gently (Cognitive: 10%)

═══════════════════════════════════════════════════════════════
EXAMPLES OF GOOD MERGES
═══════════════════════════════════════════════════════════════

Input Agents:
- Listener: "That betrayal must feel devastating. You trusted him completely."
- Cognitive: "When someone cheats, it's natural to question your judgment, but his choice to betray you says nothing about your worth."
- Mindfulness: "Notice if you're holding tension in your chest or throat right now."

✅ MERGED (relationship_focused):
"That betrayal cuts deep - trusting someone fully and having them break it like that. 
It's natural to question yourself, but his choice says everything about him, 
nothing about your worth. 💙"

---

Input Agents:
- Listener: "You're feeling completely alone and like everyone hates you."
- Cognitive: "The statement 'everyone' might be your hurt speaking. Are there any exceptions, even small ones?"
- Mindfulness: "When you notice the loneliness, where do you feel it in your body?"

✅ MERGED (empathetic - bullying context):
"Feeling hated and completely alone - that's such a heavy place to be, especially 
when you're facing bullying daily. When hurt runs this deep, our minds sometimes see 
it everywhere, even where it might not be. Have you been able to tell any adult at school?"

---

Input Agents:
- Listener: "Losing your mom - that's unimaginable pain."
- Cognitive: "Grief doesn't follow a timeline. However you're feeling is valid."
- Mindfulness: "Be gentle with yourself in these waves of emotion."

✅ MERGED (grief_focused):
"Losing your mom - there are no words for that kind of loss. However you're feeling 
right now is exactly right, even when it doesn't make sense. 🕊️"

═══════════════════════════════════════════════════════════════
CRITICAL RULES
═══════════════════════════════════════════════════════════════

- Keep response SHORT (2-4 sentences max)
- NO bullet points or lists in the final output
- ONE emoji max (💙 💔 🕊️ 🤍) and only if it feels natural
- If agents contradict, default to Listener's validation
- NEVER output agent names or "Listener says" - just merge naturally
- If user corrected you, apologize and adjust immediately

═══════════════════════════════════════════════════════════════
YOUR OUTPUT FORMAT
═══════════════════════════════════════════════════════════════

Return ONLY the final merged response. No preamble, no meta-commentary.
Just the therapeutic response itself.
"""


class SupervisorAgent:
    def __init__(self):
        self.llm = LLMClient()
        self.safety_agent = SafetyAgent()

    def merge_with_safety_first(
        self,
        agent_outputs: Dict[str, Tuple[str, float]],
        user_message: str,
        emotion_tag: str,
        room_style: str = "empathetic",
        context: Optional[Dict] = None
    ) -> str:
        """
        Enhanced merge with safety checks, action requests, and context gathering.
        """
        context = context or {}
        
        # 1. SAFETY CHECK (always first if triggered)
        safety_response = self.safety_agent.check(user_message, emotion_tag)
        if safety_response:
            # If safety triggered, prepend it to regular response
            regular = self._merge_regular(agent_outputs, user_message, room_style)
            return f"{safety_response}\n\n{regular}"
        
        # 2. IMMEDIATE ACTION REQUEST (if user asks "what do I do")
        if self._is_action_request(user_message):
            return self._handle_action_request(agent_outputs, user_message, room_style)
        
        # 3. CONTEXT QUESTIONS (if critical info missing)
        if self._needs_context(user_message, context):
            regular = self._merge_regular(agent_outputs, user_message, room_style)
            context_q = self._generate_context_question(user_message, context)
            return f"{regular}\n\n{context_q}"
        
        # 4. REGULAR MERGE (default path)
        return self._merge_regular(agent_outputs, user_message, room_style)
    
    def _is_action_request(self, message: str) -> bool:
        """Check if user is asking for actionable advice."""
        action_phrases = [
            "what do i do", "what should i do", "what can i do",
            "how do i", "help me", "tell me what to do"
        ]
        return any(phrase in message.lower() for phrase in action_phrases)
    
    def _handle_action_request(
        self,
        agent_outputs: Dict[str, Tuple[str, float]],
        user_message: str,
        room_style: str
    ) -> str:
        """Provide immediate coping + menu of options."""
        # Get immediate coping from cognitive agent
        if "cognitive" in agent_outputs:
            cognitive_response = agent_outputs["cognitive"][0]
        else:
            cognitive_response = "Let's break this down together."
        
        # Build response with immediate + menu
        prompt = f"""USER ASKS: "{user_message}"

COGNITIVE AGENT RESPONSE:
{cognitive_response}

Create a response that:
1. Gives ONE immediate 60-second coping technique (breathing, grounding, etc.)
2. Then offers a menu: "I can also help with: A) Understanding why this hurts, B) Practical steps to change the situation. Which would you like?"

Keep it 3-4 sentences total. Be warm and practical."""

        messages = [Message(role="user", content=prompt)]
        return self.llm.chat(messages, system=SYSTEM_BASE)
    
    def _needs_context(self, message: str, context: Dict) -> bool:
        """Check if we need to ask clarifying questions."""
        # Check for school/work mentions without context
        setting_keywords = ["school", "class", "teacher", "work", "job", "boss", "college"]
        has_setting_mention = any(kw in message.lower() for kw in setting_keywords)
        
        if has_setting_mention and not context.get("setting"):
            return True
        
        # Check for bullying/conflict without age context
        conflict_keywords = ["bully", "mean", "hate me", "pick on", "exclude"]
        has_conflict = any(kw in message.lower() for kw in conflict_keywords)
        
        if has_conflict and not context.get("age_range"):
            return True
        
        return False
    
    def _generate_context_question(self, message: str, context: Dict) -> str:
        """Generate appropriate clarifying question."""
        message_lower = message.lower()
        
        # School/work setting
        if any(kw in message_lower for kw in ["school", "class", "teacher"]) and not context.get("setting"):
            return "To help better - is this happening at school, work, or somewhere else?"
        
        # Bullying/conflict context
        if any(kw in message_lower for kw in ["bully", "mean", "hate"]) and not context.get("age_range"):
            return "Can I ask - are you in school, or is this a work situation? It helps me give more relevant support."
        
        # Support system
        if "alone" in message_lower or "no one" in message_lower:
            if not context.get("has_support"):
                return "Is there anyone in your life you feel safe talking to - a friend, family member, counselor?"
        
        return "Tell me a bit more about your situation so I can help better?"
    
    def _merge_regular(
        self,
        agent_outputs: Dict[str, Tuple[str, float]],
        user_input: str,
        room_style: str
    ) -> str:
        """Standard merge logic."""
        # Build the prompt with weighted inputs
        prompt = f"""USER MESSAGE:
"{user_input}"

AGENT RESPONSES (with priority weights):
"""
        
        for agent_name, (response, weight) in agent_outputs.items():
            priority = "HIGH" if weight >= 0.5 else "MEDIUM" if weight >= 0.3 else "LOW"
            prompt += f"\n[{agent_name.upper()}] (weight: {weight:.1f} - {priority} priority):\n{response}\n"
        
        prompt += f"\n\nROOM STYLE: {room_style}\n"
        prompt += "\nMerge these into ONE natural, cohesive therapeutic response (2-4 sentences):"
        
        system = SYSTEM_BASE
        
        # Add room-specific guidance
        if room_style == "crisis":
            system += "\n\n🆘 CRISIS MODE: Prioritize safety, validation, and grounding."
        elif room_style == "trauma_informed":
            system += "\n\n🛡️ TRAUMA MODE: Extra gentleness. Heavy validation."
        elif room_style == "grief_focused":
            system += "\n\n🕊️ GRIEF MODE: Sit with pain. No silver linings."
        
        messages = [Message(role="user", content=prompt)]
        return self.llm.chat(messages, system=system)

    def merge_with_weights(
        self,
        agent_outputs: Dict[str, Tuple[str, float]],
        user_input: str,
        room_style: str = "empathetic"
    ) -> str:
        """
        Merge agent outputs with explicit weights based on room configuration.
        
        Args:
            agent_outputs: Dict mapping agent name to (response, weight) tuple
            user_input: Original user message for context
            room_style: Therapeutic style from room configuration
            
        Returns:
            Merged therapeutic response
        """
        # For backward compatibility, call merge_with_safety_first with default values
        return self.merge_with_safety_first(
            agent_outputs=agent_outputs,
            user_message=user_input,
            emotion_tag="UNKNOWN",  # Won't trigger safety by default
            room_style=room_style,
            context={}
        )

    def merge(
        self,
        agent_outputs: Dict[str, str],
        user_input: str,
        room_style: str = "empathetic"
    ) -> str:
        """
        Legacy merge method with equal weights (for backward compatibility).
        
        Args:
            agent_outputs: Dict mapping agent name to response string
            user_input: Original user message
            room_style: Therapeutic style
            
        Returns:
            Merged response
        """
        # Convert to weighted format with equal weights
        weighted_outputs = {
            name: (response, 0.33) 
            for name, response in agent_outputs.items()
        }
        
        return self.merge_with_weights(weighted_outputs, user_input, room_style)