# src/core/topics.py
from __future__ import annotations
from typing import Optional

def detect_topic(text: Optional[str]) -> str:
    t = (text or "").lower()
    # relationship / cheating
    if any(k in t for k in ["cheat on me", "cheating", "affair", "unfaithful", "texts another", "dm another"]):
        return "relationship_cheating"
    if any(k in t for k in ["break up", "broke up", "fight with my boyfriend", "fight with my girlfriend", "relationship fight", "partner ignored me"]):
        return "relationship_conflict"

    # exclusion / left out
    if any(k in t for k in ["no one invites", "nobody invites", "left out", "don’t get invited", "dont get invited", "alone on weekends"]):
        return "left_out"

    # bullying / appearance shaming
    if any(k in t for k in ["bully", "bullying", "called ugly", "ugly", "name calling", "school", "classmates"]):
        return "bullying"
        t = (text or "").lower()
        
    # breakup / heartbreak
    if any(k in t for k in ["broke up", "break up", "breakup", "boyfriend just left", "girlfriend just left", "we're over", "we are over", "heartbroken", "broke my heart"]):
        return "relationship_breakup"

    # self-blame / shame
    if any(k in t for k in ["it's my fault","its my fault","i ruin","i'm the problem","im the problem","i'm worthless","im worthless","not good enough"]):
        return "self_blame"

    # panic / overwhelm
    if any(k in t for k in ["panic","panicking","can't breathe","cant breathe","shaking","overwhelmed","freaking out","spiral","spiraling"]):
        return "panic"

    # rumination / overthinking
    if any(k in t for k in ["overthink","overthinking","stuck in my head","escape my thoughts","can't stop thinking","cant stop thinking","looping thoughts","rumination"]):
        return "rumination"

    # burnout / emptiness
    if any(k in t for k in ["burnout","burned out","numb","empty","done with everything","exhausted","tired of everything"]):
        return "burnout"
    
    if any(k in t for k in ["panic","panicking","can't breathe","shaking","overwhelmed"]):
        return "panic"
    if any(k in t for k in ["sad","low","bad day"]):
        return "sadness"
    return "general"
