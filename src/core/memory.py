# src/core/memory.py
"""
Memory module for SoulSync.
Handles session storage, emotion tracking, and chat management.
"""
from __future__ import annotations
import json
import os
import time
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime


# ══════════════════════════════════════════════════════════════
# PATHS
# ══════════════════════════════════════════════════════════════

DATA_DIR = Path(__file__).parent.parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


# ══════════════════════════════════════════════════════════════
# SESSION MANAGEMENT
# ══════════════════════════════════════════════════════════════

def save_session_turn(user_id: str, user_message: str, agent_response: str,
                     chat_id: str = "default", emotion: str = None,
                     room_type: str = "emotional_wellness",
                     topic: str = None, chat_title: str = None):
    """
    Save conversation turn with user_id.
    
    Args:
        user_id: User identifier (e.g., "krish", "john")
        user_message: What user said
        agent_response: What AI responded
        chat_id: Conversation ID
        emotion: Detected emotion (optional)
        room_type: Which therapy room
        topic: Optional topic classification
        chat_title: Optional chat title
    """
    # Create user-specific directory
    user_dir = DATA_DIR / "sessions" / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    
    session_data = {
        "user_id": user_id,
        "chat_id": chat_id,
        "room_type": room_type,
        "ts": time.time(),
        "timestamp": datetime.now().isoformat(),
        "user": user_message,
        "agent": agent_response,
        "emotion": emotion,
        "topic": topic,
        "chat_title": chat_title
    }
    
    # Save to user-specific file
    filepath = user_dir / f"session_{chat_id}.jsonl"
    with open(filepath, "a") as f:
        f.write(json.dumps(session_data) + "\n")


def load_sessions(user_id: str, limit: int = 100, chat_id: str = None) -> List[Dict]:
    """
    Load sessions for specific user.
    
    Args:
        user_id: User identifier
        limit: Maximum number of sessions
        chat_id: Optional specific chat to load
        
    Returns:
        List of session dictionaries
    """
    user_dir = DATA_DIR / "sessions" / user_id
    
    if not user_dir.exists():
        return []
    
    sessions = []
    
    # If specific chat requested
    if chat_id:
        filepath = user_dir / f"session_{chat_id}.jsonl"
        if filepath.exists():
            with open(filepath, "r") as f:
                for line in f:
                    try:
                        sessions.append(json.loads(line))
                    except:
                        pass
    else:
        # Load all sessions for user
        for filepath in user_dir.glob("session_*.jsonl"):
            with open(filepath, "r") as f:
                for line in f:
                    try:
                        sessions.append(json.loads(line))
                    except:
                        pass
    
    # Sort by timestamp and limit
    sessions.sort(key=lambda x: x.get("ts", 0), reverse=True)
    return sessions[:limit]


def get_all_chats(user_id: str) -> List[Dict]:
    """
    Get list of all chats for a user.
    
    Args:
        user_id: User identifier
        
    Returns:
        List of chat info dictionaries
    """
    user_dir = DATA_DIR / "sessions" / user_id
    
    if not user_dir.exists():
        return []
    
    chats = {}
    
    for filepath in user_dir.glob("session_*.jsonl"):
        chat_id = filepath.stem.replace("session_", "")
        
        # Get first and last message
        try:
            with open(filepath, "r") as f:
                lines = f.readlines()
                if lines:
                    first = json.loads(lines[0])
                    last = json.loads(lines[-1])
                    
                    chats[chat_id] = {
                        "chat_id": chat_id,
                        "message_count": len(lines),
                        "first_message": first.get("user", "")[:50],
                        "last_timestamp": last.get("timestamp", ""),
                        "room_type": last.get("room_type", "unknown"),
                        "chat_title": last.get("chat_title", "Untitled")
                    }
        except:
            pass
    
    # Sort by last timestamp
    chat_list = list(chats.values())
    chat_list.sort(key=lambda x: x.get("last_timestamp", ""), reverse=True)
    
    return chat_list


# ══════════════════════════════════════════════════════════════
# EMOTION LOGGING (JSONL - separate from SQLite)
# ══════════════════════════════════════════════════════════════

def save_emotion(user_id: str, emotion: str, intensity: int = 5,
                message_preview: str = "", topic: str = None):
    """
    Save emotion to JSONL file (lightweight logging).
    
    Args:
        user_id: User identifier
        emotion: Emotion name
        intensity: 1-10 scale
        message_preview: Preview of message
        topic: Optional topic
    """
    emotion_dir = DATA_DIR / "emotions"
    emotion_dir.mkdir(exist_ok=True)
    
    emotion_data = {
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "emotion": emotion,
        "intensity": intensity,
        "message_preview": message_preview[:100],
        "topic": topic
    }
    
    filepath = emotion_dir / f"{user_id}_emotions.jsonl"
    with open(filepath, "a") as f:
        f.write(json.dumps(emotion_data) + "\n")


def load_emotions(user_id: str, limit: int = 100) -> List[Dict]:
    """
    Load emotions for user from JSONL.
    
    Args:
        user_id: User identifier
        limit: Maximum number to load
        
    Returns:
        List of emotion dictionaries
    """
    filepath = DATA_DIR / "emotions" / f"{user_id}_emotions.jsonl"
    
    if not filepath.exists():
        return []
    
    emotions = []
    with open(filepath, "r") as f:
        for line in f:
            try:
                emotions.append(json.loads(line))
            except:
                pass
    
    # Sort by timestamp and limit
    emotions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return emotions[:limit]


# ══════════════════════════════════════════════════════════════
# DATA EXPORT & DELETION (GDPR)
# ══════════════════════════════════════════════════════════════

def export_user_data(user_id: str) -> Dict:
    """
    Export all user data (GDPR compliance).
    
    Args:
        user_id: User identifier
        
    Returns:
        Dictionary with all user data
    """
    return {
        "user_id": user_id,
        "sessions": load_sessions(user_id, limit=10000),
        "emotions": load_emotions(user_id, limit=10000),
        "chats": get_all_chats(user_id),
        "export_date": datetime.now().isoformat()
    }


def delete_user_data(user_id: str) -> Dict:
    """
    Delete all data for a user (GDPR compliance).
    
    Args:
        user_id: User identifier
        
    Returns:
        Dictionary with deletion stats
    """
    import shutil
    
    deleted_files = 0
    
    # Delete session directory
    user_dir = DATA_DIR / "sessions" / user_id
    if user_dir.exists():
        deleted_files = len(list(user_dir.glob("*.jsonl")))
        shutil.rmtree(user_dir)
    
    # Delete emotion file
    emotion_file = DATA_DIR / "emotions" / f"{user_id}_emotions.jsonl"
    if emotion_file.exists():
        emotion_file.unlink()
        deleted_files += 1
    
    # Delete from SQLite if using emotion_db
    try:
        from .emotion_db import EmotionDB
        db = EmotionDB()
        deleted_emotions = db.delete_user_emotions(user_id)
    except:
        deleted_emotions = 0
    
    return {
        "user_id": user_id,
        "deleted_files": deleted_files,
        "deleted_emotions": deleted_emotions,
        "success": True
    }


# ══════════════════════════════════════════════════════════════
# CHAT MANAGEMENT
# ══════════════════════════════════════════════════════════════

def create_new_chat(user_id: str, room_type: str = "emotional_wellness") -> str:
    """
    Create a new chat ID.
    
    Args:
        user_id: User identifier
        room_type: Therapy room type
        
    Returns:
        New chat ID
    """
    import hashlib
    chat_id = hashlib.md5(f"{user_id}{time.time()}".encode()).hexdigest()[:8]
    return chat_id


def get_chat_title(user_id: str, chat_id: str) -> str:
    """
    Get chat title from first message.
    
    Args:
        user_id: User identifier
        chat_id: Chat ID
        
    Returns:
        Chat title
    """
    sessions = load_sessions(user_id, chat_id=chat_id, limit=1)
    if sessions:
        first_message = sessions[0].get("user", "")
        # Generate title from first message
        words = first_message.split()[:5]
        return " ".join(words) if words else "Untitled Chat"
    return "Untitled Chat"


def delete_chat(user_id: str, chat_id: str) -> bool:
    """
    Delete a specific chat.
    
    Args:
        user_id: User identifier
        chat_id: Chat ID to delete
        
    Returns:
        True if successful
    """
    filepath = DATA_DIR / "sessions" / user_id / f"session_{chat_id}.jsonl"
    if filepath.exists():
        filepath.unlink()
        return True
    return False


# ══════════════════════════════════════════════════════════════
# BACKWARDS COMPATIBILITY (for old code)
# ══════════════════════════════════════════════════════════════

def save_session(user_id: str, user_message: str, agent_response: str, **kwargs):
    """Alias for backwards compatibility."""
    return save_session_turn(user_id, user_message, agent_response, **kwargs)


# ══════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Test save
    save_session_turn(
        user_id="test_user",
        user_message="I'm feeling sad today",
        agent_response="I hear that you're feeling sad. Tell me more about what's going on.",
        chat_id="test_chat_001",
        emotion="sadness",
        room_type="emotional_wellness"
    )
    
    # Test load
    sessions = load_sessions("test_user")
    print(f"Loaded {len(sessions)} sessions")
    
    # Test get chats
    chats = get_all_chats("test_user")
    print(f"Found {len(chats)} chats")
    
    # Test emotion logging
    save_emotion("test_user", "sadness", 7, "I'm feeling sad")
    emotions = load_emotions("test_user")
    print(f"Loaded {len(emotions)} emotions")