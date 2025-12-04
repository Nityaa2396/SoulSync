# src/core/router.py
"""
Smart Router: Detects the primary mental health concern and activates appropriate specialist agents.
Based on clinical triage principles used in psychiatric emergency departments.
"""
from __future__ import annotations
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class IssueDetection:
    """Result of issue classification"""
    primary_issue: str  # Main concern (e.g., "relationship_breakup")
    severity: str  # "crisis", "urgent", "moderate", "mild"
    specialist_needed: Optional[str]  # Which specialist agent to activate
    crisis_keywords: List[str]  # Any crisis indicators found
    confidence: float  # 0.0 to 1.0


# === CRISIS DETECTION (Highest Priority) ===
CRISIS_INDICATORS = {
    "suicide": [
        "kill myself", "end my life", "want to die", "better off dead",
        "suicide", "suicidal", "no reason to live", "can't go on",
        "goodbye forever", "final goodbye"
    ],
    "self_harm": [
        "cut myself", "hurt myself", "harm myself", "burning myself",
        "self harm", "self-harm", "cutting", "razor"
    ],
    "violence": [
        "kill them", "hurt someone", "going to hurt", "violent thoughts",
        "kill him", "kill her", "harm others"
    ],
    "psychosis": [
        "voices telling me", "hearing voices", "people watching me",
        "they're following", "government tracking", "not real",
        "hallucinating", "seeing things"
    ],
    "substance_overdose": [
        "took too many", "overdose", "pills", "took everything",
        "empty bottle"
    ]
}

# === SPECIALIST ISSUE CATEGORIES ===
# Based on mental health triage research - these require specific approaches

RELATIONSHIP_ISSUES = {
    "relationship_breakup": [
        "broke up", "break up", "breakup", "boyfriend left", "girlfriend left",
        "we're over", "ended things", "broke my heart", "heartbroken",
        "left me", "dumped me"
    ],
    "relationship_cheating": [
        "cheated on me", "cheating", "affair", "unfaithful",
        "seeing someone else", "dating someone else", "caught him",
        "texts another", "flirting with"
    ],
    "relationship_conflict": [
        "fight with my boyfriend", "fight with my girlfriend",
        "argument with partner", "relationship fight", "we fought",
        "partner ignored me", "won't talk to me"
    ],
    "relationship_abuse": [
        "hits me", "hurts me", "controlling", "threatened me",
        "scared of him", "scared of her", "abusive", "violence"
    ]
}

GRIEF_LOSS = {
    "death_loved_one": [
        "died", "passed away", "lost my mom", "lost my dad",
        "funeral", "death", "grief", "mourning"
    ],
    "pet_loss": [
        "my dog died", "my cat died", "put down", "pet died"
    ],
    "miscarriage": [
        "miscarriage", "lost the baby", "pregnancy loss"
    ]
}

TRAUMA_ABUSE = {
    "past_abuse": [
        "was abused", "molested", "assaulted", "raped",
        "trauma", "ptsd", "flashbacks"
    ],
    "bullying": [
        "bully", "bullying", "called ugly", "made fun of",
        "name calling", "picked on", "teased"
    ]
}

MENTAL_HEALTH_CONDITIONS = {
    "eating_disorder": [
        "anorexia", "bulimia", "binge", "purge", "throwing up",
        "starving myself", "fat", "weight", "calories"
    ],
    "addiction": [
        "addicted", "can't stop drinking", "drugs", "alcohol problem",
        "using again", "relapse", "sober"
    ],
    "panic_anxiety": [
        "panic attack", "can't breathe", "heart racing", "shaking",
        "freaking out", "anxiety", "overwhelmed"
    ],
    "depression": [
        "depressed", "hopeless", "numb", "empty", "worthless",
        "nothing matters", "no point"
    ]
}

SOCIAL_ISSUES = {
    "loneliness": [
        "no friends", "alone", "lonely", "no one likes me",
        "left out", "not invited", "isolated"
    ],
    "family_conflict": [
        "fight with parents", "mom hates me", "dad yells",
        "family problems", "kicked out", "running away"
    ]
}

STRESS_BURNOUT = {
    "academic_stress": [
        "failing school", "exams", "grades", "college stress",
        "homework", "school pressure"
    ],
    "work_burnout": [
        "hate my job", "work stress", "burnout", "exhausted",
        "can't keep up", "too much work"
    ]
}


def detect_crisis_level(text: str) -> Tuple[bool, List[str]]:
    """
    Check for crisis indicators that require immediate intervention.
    Returns: (is_crisis, list_of_crisis_keywords_found)
    """
    t = text.lower()
    found = []
    
    for category, keywords in CRISIS_INDICATORS.items():
        for kw in keywords:
            if kw in t:
                found.append(category)
                break
    
    return (len(found) > 0, found)


def detect_primary_issue(text: str, conversation_history: Optional[List[str]] = None) -> IssueDetection:
    """
    Analyze user text and classify the primary mental health concern.
    Based on clinical mental health triage principles.
    
    Args:
        text: Current user message
        conversation_history: Previous user messages for context
        
    Returns:
        IssueDetection with classification and specialist recommendation
    """
    t = text.lower()
    
    # Combine current + recent history for better context
    full_context = t
    if conversation_history:
        full_context = " ".join(conversation_history[-3:] + [t]).lower()
    
    # === STEP 1: CRISIS SCREENING (highest priority) ===
    is_crisis, crisis_kws = detect_crisis_level(full_context)
    if is_crisis:
        return IssueDetection(
            primary_issue="crisis",
            severity="crisis",
            specialist_needed="crisis_agent",  # Must escalate to safety protocol
            crisis_keywords=crisis_kws,
            confidence=1.0
        )
    
    # === STEP 2: SPECIALIST ISSUE DETECTION ===
    # Score each category based on keyword matches
    scores: Dict[str, int] = {}
    
    def score_category(category_dict: Dict[str, List[str]], category_name: str):
        for issue, keywords in category_dict.items():
            count = sum(1 for kw in keywords if kw in full_context)
            if count > 0:
                scores[issue] = scores.get(issue, 0) + count
    
    # Score all categories
    score_category(RELATIONSHIP_ISSUES, "relationship")
    score_category(GRIEF_LOSS, "grief")
    score_category(TRAUMA_ABUSE, "trauma")
    score_category(MENTAL_HEALTH_CONDITIONS, "mental_health")
    score_category(SOCIAL_ISSUES, "social")
    score_category(STRESS_BURNOUT, "stress")
    
    # === STEP 3: DETERMINE PRIMARY ISSUE ===
    if not scores:
        # No specific issue detected - general emotional support
        return IssueDetection(
            primary_issue="general",
            severity="mild",
            specialist_needed=None,
            crisis_keywords=[],
            confidence=0.5
        )
    
    # Get highest scoring issue
    primary = max(scores, key=scores.get)
    max_score = scores[primary]
    confidence = min(1.0, max_score / 5.0)  # Normalize to 0-1
    
    # === STEP 4: DETERMINE SEVERITY ===
    severity = "mild"
    if max_score >= 3:
        severity = "moderate"
    if max_score >= 5:
        severity = "urgent"
    
    # Check for intensity words
    intensity_words = ["extreme", "can't take", "unbearable", "intense", "severe"]
    if any(word in t for word in intensity_words):
        if severity == "mild":
            severity = "moderate"
        elif severity == "moderate":
            severity = "urgent"
    
    # === STEP 5: ASSIGN SPECIALIST ===
    specialist_map = {
        # Relationship issues
        "relationship_breakup": "relationship_agent",
        "relationship_cheating": "relationship_agent",
        "relationship_conflict": "relationship_agent",
        "relationship_abuse": "crisis_agent",  # Abuse = crisis
        
        # Grief
        "death_loved_one": "grief_agent",
        "pet_loss": "grief_agent",
        "miscarriage": "grief_agent",
        
        # Trauma
        "past_abuse": "trauma_agent",
        "bullying": "social_agent",
        
        # Mental health conditions
        "eating_disorder": "eating_disorder_agent",
        "addiction": "addiction_agent",
        "panic_anxiety": "anxiety_agent",
        "depression": "general",  # Current Listener handles this well
        
        # Social/stress
        "loneliness": "general",
        "family_conflict": "family_agent",
        "academic_stress": "general",
        "work_burnout": "general"
    }
    
    specialist = specialist_map.get(primary, None)
    
    return IssueDetection(
        primary_issue=primary,
        severity=severity,
        specialist_needed=specialist,
        crisis_keywords=[],
        confidence=confidence
    )


# === HELPER: GET FRIENDLY NAMES ===
def get_issue_description(issue: str) -> str:
    """Return human-readable description of the issue"""
    descriptions = {
        "crisis": "Crisis situation requiring immediate support",
        "relationship_breakup": "Heartbreak and relationship ending",
        "relationship_cheating": "Infidelity concerns",
        "relationship_conflict": "Relationship conflict",
        "relationship_abuse": "Relationship abuse",
        "death_loved_one": "Grief from losing someone",
        "pet_loss": "Pet loss grief",
        "past_abuse": "Past trauma or abuse",
        "bullying": "Bullying or social cruelty",
        "eating_disorder": "Eating or body image concerns",
        "addiction": "Substance use concerns",
        "panic_anxiety": "Panic or severe anxiety",
        "depression": "Depression or hopelessness",
        "loneliness": "Loneliness and isolation",
        "family_conflict": "Family relationship problems",
        "general": "General emotional support"
    }
    return descriptions.get(issue, "Emotional support needed")