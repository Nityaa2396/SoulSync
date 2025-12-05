"""
Supabase Database Client for SoulSync
Handles all database operations with Supabase PostgreSQL
"""

import os
from datetime import datetime
from typing import Optional, Dict, List, Any
from supabase import create_client, Client
import hashlib


class SupabaseClient:
    """
    Manages all Supabase database operations.
    Replaces local JSON file storage with cloud database.
    """
    
    def __init__(self):
        """Initialize Supabase client with credentials from environment."""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError(
                "Missing Supabase credentials! Add SUPABASE_URL and SUPABASE_KEY to .env or Streamlit secrets"
            )
        
        self.client: Client = create_client(supabase_url, supabase_key)
    
    # ═══════════════════════════════════════════════════════════
    # USER AUTHENTICATION
    # ═══════════════════════════════════════════════════════════
    
    def create_user(self, email: str, password: str, provider: str = "email") -> Dict:
        """
        Create new user account.
        
        Args:
            email: User's email
            password: Plain text password (will be hashed)
            provider: 'email', 'google', 'github', etc.
            
        Returns:
            User dict with id, email, created_at
        """
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            result = self.client.table("users").insert({
                "email": email,
                "password_hash": password_hash,
                "provider": provider,
                "created_at": datetime.utcnow().isoformat()
            }).execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            if "duplicate key" in str(e).lower():
                raise ValueError("Email already exists")
            raise e
    
    def verify_user(self, email: str, password: str) -> Optional[Dict]:
        """
        Verify user login credentials.
        
        Args:
            email: User's email
            password: Plain text password
            
        Returns:
            User dict if valid, None if invalid
        """
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        result = self.client.table("users").select("*").eq(
            "email", email
        ).eq("password_hash", password_hash).execute()
        
        if result.data:
            # Update last login
            user_id = result.data[0]["id"]
            self.client.table("users").update({
                "last_login": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()
            
            return result.data[0]
        
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email."""
        result = self.client.table("users").select("*").eq("email", email).execute()
        return result.data[0] if result.data else None
    
    def update_user_password(self, email: str, new_password: str) -> bool:
        """Update user's password."""
        password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        
        result = self.client.table("users").update({
            "password_hash": password_hash
        }).eq("email", email).execute()
        
        return bool(result.data)
    
    # ═══════════════════════════════════════════════════════════
    # OAUTH USERS
    # ═══════════════════════════════════════════════════════════
    
    def create_oauth_user(self, email: str, provider: str, provider_id: str) -> Dict:
        """
        Create user from OAuth (Google, GitHub, etc.).
        No password needed.
        
        Args:
            email: User's email from OAuth
            provider: 'google', 'github', 'apple'
            provider_id: Unique ID from OAuth provider
            
        Returns:
            User dict
        """
        try:
            result = self.client.table("users").insert({
                "email": email,
                "password_hash": "",  # No password for OAuth
                "provider": provider,
                "provider_id": provider_id,
                "created_at": datetime.utcnow().isoformat()
            }).execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            if "duplicate key" in str(e).lower():
                # User exists, return existing user
                return self.get_user_by_email(email)
            raise e
    
    def get_oauth_user(self, provider: str, provider_id: str) -> Optional[Dict]:
        """Get user by OAuth provider ID."""
        result = self.client.table("users").select("*").eq(
            "provider", provider
        ).eq("provider_id", provider_id).execute()
        
        return result.data[0] if result.data else None
    
    # ═══════════════════════════════════════════════════════════
    # SESSIONS (Chat Sessions)
    # ═══════════════════════════════════════════════════════════
    
    def create_session(self, user_id: str, chat_id: str, room_type: str) -> Dict:
        """Create new chat session."""
        result = self.client.table("user_sessions").insert({
            "user_id": user_id,
            "chat_id": chat_id,
            "room_type": room_type,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }).execute()
        
        return result.data[0] if result.data else None
    
    def get_user_sessions(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get all sessions for a user."""
        result = self.client.table("user_sessions").select("*").eq(
            "user_id", user_id
        ).order("updated_at", desc=True).limit(limit).execute()
        
        return result.data or []
    
    def update_session(self, session_id: str) -> bool:
        """Update session timestamp."""
        result = self.client.table("user_sessions").update({
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", session_id).execute()
        
        return bool(result.data)
    
    # ═══════════════════════════════════════════════════════════
    # MESSAGES
    # ═══════════════════════════════════════════════════════════
    
    def save_message(self, user_id: str, session_id: str, role: str, content: str) -> Dict:
        """
        Save chat message.
        
        Args:
            user_id: User's ID
            session_id: Session ID
            role: 'user' or 'assistant'
            content: Message content
        """
        result = self.client.table("messages").insert({
            "user_id": user_id,
            "session_id": session_id,
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }).execute()
        
        return result.data[0] if result.data else None
    
    def get_session_messages(self, session_id: str, limit: int = 100) -> List[Dict]:
        """Get all messages for a session."""
        result = self.client.table("messages").select("*").eq(
            "session_id", session_id
        ).order("timestamp", desc=False).limit(limit).execute()
        
        return result.data or []
    
    def get_user_messages(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get recent messages for a user across all sessions."""
        result = self.client.table("messages").select("*").eq(
            "user_id", user_id
        ).order("timestamp", desc=True).limit(limit).execute()
        
        return result.data or []
    
    # ═══════════════════════════════════════════════════════════
    # EMOTIONS
    # ═══════════════════════════════════════════════════════════
    
    def save_emotion(self, user_id: str, emotion: str, intensity: float, 
                     message_preview: str = "") -> Dict:
        """
        Save detected emotion.
        
        Args:
            user_id: User's ID
            emotion: Emotion name (HAPPY, SAD, ANXIOUS, etc.)
            intensity: 0-10 scale
            message_preview: First 100 chars of message
        """
        result = self.client.table("emotions").insert({
            "user_id": user_id,
            "emotion": emotion,
            "intensity": intensity,
            "message_preview": message_preview[:100],
            "timestamp": datetime.utcnow().isoformat()
        }).execute()
        
        return result.data[0] if result.data else None
    
    def get_user_emotions(self, user_id: str, days: int = 30, limit: int = 1000) -> List[Dict]:
        """
        Get user's emotions for emotion dashboard.
        
        Args:
            user_id: User's ID
            days: Number of days to look back
            limit: Max emotions to return
        """
        from datetime import timedelta
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        result = self.client.table("emotions").select("*").eq(
            "user_id", user_id
        ).gte("timestamp", cutoff_date).order(
            "timestamp", desc=True
        ).limit(limit).execute()
        
        return result.data or []
    
    def get_emotion_counts(self, user_id: str, days: int = 7) -> Dict[str, int]:
        """Get emotion counts for quick stats."""
        emotions = self.get_user_emotions(user_id, days=days)
        
        counts = {}
        for emotion_entry in emotions:
            emotion = emotion_entry["emotion"]
            counts[emotion] = counts.get(emotion, 0) + 1
        
        return counts
    
    # ═══════════════════════════════════════════════════════════
    # DATA EXPORT & DELETION (GDPR Compliance)
    # ═══════════════════════════════════════════════════════════
    
    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export all user data for download."""
        return {
            "user": self.client.table("users").select("*").eq("id", user_id).execute().data,
            "sessions": self.get_user_sessions(user_id, limit=1000),
            "messages": self.get_user_messages(user_id, limit=5000),
            "emotions": self.get_user_emotions(user_id, days=365, limit=5000),
            "exported_at": datetime.utcnow().isoformat()
        }
    
    def delete_user_account(self, user_id: str) -> bool:
        """
        Delete user and ALL their data permanently.
        Cascade delete handles sessions, messages, emotions.
        """
        result = self.client.table("users").delete().eq("id", user_id).execute()
        return bool(result.data)


# ═══════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════

def get_supabase_client() -> SupabaseClient:
    """Get singleton Supabase client instance."""
    if not hasattr(get_supabase_client, "_instance"):
        get_supabase_client._instance = SupabaseClient()
    return get_supabase_client._instance