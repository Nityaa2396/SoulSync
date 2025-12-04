"""
Emotion Database - SQLite storage for emotion tracking
Stores emotions, intensities, and patterns over time.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path


# Database path
DB_PATH = Path(__file__).parent.parent.parent / "data" / "soulsync.db"


class EmotionDB:
    """Manages emotion storage and retrieval in SQLite."""
    
    def __init__(self, db_path: str = None):
        """
        Initialize emotion database.
        
        Args:
            db_path: Path to SQLite database (optional)
        """
        self.db_path = db_path or str(DB_PATH)
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Emotions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emotions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                emotion TEXT NOT NULL,
                intensity INTEGER CHECK(intensity >= 1 AND intensity <= 10),
                topic TEXT,
                message_preview TEXT,
                session_id TEXT,
                chat_id TEXT
            )
        """)
        
        # Indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_timestamp 
            ON emotions(user_id, timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_emotion 
            ON emotions(emotion)
        """)
        
        conn.commit()
        conn.close()
    
    def save_emotion(self, user_id: str, emotion: str, intensity: int,
                    message_preview: str, topic: Optional[str] = None,
                    session_id: Optional[str] = None, 
                    chat_id: Optional[str] = "default") -> int:
        """
        Save an emotion entry.
        
        Args:
            user_id: User identifier
            emotion: Emotion name (e.g., "sadness", "anger")
            intensity: 1-10 scale
            message_preview: First 100 chars of message
            topic: Optional topic classification
            session_id: Optional session ID
            chat_id: Optional chat ID
            
        Returns:
            Row ID of inserted emotion
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO emotions 
            (user_id, emotion, intensity, message_preview, topic, session_id, chat_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, emotion, intensity, message_preview[:100], topic, session_id, chat_id))
        
        row_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return row_id
    
    def get_emotions(self, user_id: str, days: int = 30, 
                    limit: int = 100) -> List[Dict]:
        """
        Get emotion history for a user.
        
        Args:
            user_id: User identifier
            days: Number of days to look back
            limit: Maximum number of records
            
        Returns:
            List of emotion dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return dict-like rows
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute("""
            SELECT * FROM emotions
            WHERE user_id = ? AND timestamp >= ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (user_id, cutoff_date.isoformat(), limit))
        
        emotions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return emotions
    
    def get_emotion_counts(self, user_id: str, days: int = 30) -> Dict[str, int]:
        """
        Get count of each emotion type.
        
        Args:
            user_id: User identifier
            days: Number of days to look back
            
        Returns:
            Dictionary of emotion -> count
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute("""
            SELECT emotion, COUNT(*) as count
            FROM emotions
            WHERE user_id = ? AND timestamp >= ?
            GROUP BY emotion
            ORDER BY count DESC
        """, (user_id, cutoff_date.isoformat()))
        
        counts = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        
        return counts
    
    def get_emotion_trends(self, user_id: str, emotion: str, 
                          days: int = 30) -> List[Tuple[str, float]]:
        """
        Get intensity trend for a specific emotion over time.
        
        Args:
            user_id: User identifier
            emotion: Emotion to track
            days: Number of days to look back
            
        Returns:
            List of (date, avg_intensity) tuples
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute("""
            SELECT DATE(timestamp) as date, AVG(intensity) as avg_intensity
            FROM emotions
            WHERE user_id = ? AND emotion = ? AND timestamp >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date
        """, (user_id, emotion, cutoff_date.isoformat()))
        
        trends = [(row[0], row[1]) for row in cursor.fetchall()]
        conn.close()
        
        return trends
    
    def get_average_intensity(self, user_id: str, days: int = 7) -> float:
        """
        Get average emotion intensity across all emotions.
        
        Args:
            user_id: User identifier
            days: Number of days to look back
            
        Returns:
            Average intensity (0-10)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute("""
            SELECT AVG(intensity) as avg_intensity
            FROM emotions
            WHERE user_id = ? AND timestamp >= ?
        """, (user_id, cutoff_date.isoformat()))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result[0] else 0.0
    
    def get_dominant_emotion(self, user_id: str, days: int = 7) -> Optional[str]:
        """
        Get the most common emotion in recent period.
        
        Args:
            user_id: User identifier
            days: Number of days to look back
            
        Returns:
            Most common emotion or None
        """
        counts = self.get_emotion_counts(user_id, days)
        
        if not counts:
            return None
        
        return max(counts, key=counts.get)
    
    def get_emotions_by_date(self, user_id: str, 
                            start_date: str, end_date: str) -> List[Dict]:
        """
        Get emotions within a date range.
        
        Args:
            user_id: User identifier
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            
        Returns:
            List of emotion dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM emotions
            WHERE user_id = ? 
            AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
        """, (user_id, start_date, end_date))
        
        emotions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return emotions
    
    def get_high_intensity_emotions(self, user_id: str, 
                                   threshold: int = 8, 
                                   days: int = 7) -> List[Dict]:
        """
        Get high-intensity emotions (potential crisis indicators).
        
        Args:
            user_id: User identifier
            threshold: Intensity threshold (default 8)
            days: Number of days to look back
            
        Returns:
            List of high-intensity emotion dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute("""
            SELECT * FROM emotions
            WHERE user_id = ? 
            AND intensity >= ?
            AND timestamp >= ?
            ORDER BY timestamp DESC
        """, (user_id, threshold, cutoff_date.isoformat()))
        
        emotions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return emotions
    
    def delete_user_emotions(self, user_id: str) -> int:
        """
        Delete all emotions for a user (GDPR compliance).
        
        Args:
            user_id: User identifier
            
        Returns:
            Number of rows deleted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM emotions WHERE user_id = ?", (user_id,))
        
        rows_deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return rows_deleted
    
    def get_emotion_summary(self, user_id: str, days: int = 7) -> Dict:
        """
        Get comprehensive emotion summary.
        
        Args:
            user_id: User identifier
            days: Number of days to look back
            
        Returns:
            Dictionary with summary statistics
        """
        emotions = self.get_emotions(user_id, days)
        
        if not emotions:
            return {
                "total_entries": 0,
                "avg_intensity": 0,
                "dominant_emotion": None,
                "emotion_counts": {},
                "high_intensity_count": 0
            }
        
        return {
            "total_entries": len(emotions),
            "avg_intensity": self.get_average_intensity(user_id, days),
            "dominant_emotion": self.get_dominant_emotion(user_id, days),
            "emotion_counts": self.get_emotion_counts(user_id, days),
            "high_intensity_count": len([e for e in emotions if e['intensity'] >= 8])
        }


# Convenience functions
def save_emotion(user_id: str, emotion: str, intensity: int, 
                message_preview: str, **kwargs) -> int:
    """Save emotion entry (convenience function)."""
    db = EmotionDB()
    return db.save_emotion(user_id, emotion, intensity, message_preview, **kwargs)


def get_emotions(user_id: str, days: int = 30) -> List[Dict]:
    """Get emotion history (convenience function)."""
    db = EmotionDB()
    return db.get_emotions(user_id, days)


def get_emotion_summary(user_id: str, days: int = 7) -> Dict:
    """Get emotion summary (convenience function)."""
    db = EmotionDB()
    return db.get_emotion_summary(user_id, days)


# Example usage
if __name__ == "__main__":
    db = EmotionDB()
    
    # Test save
    emotion_id = db.save_emotion(
        user_id="test_user",
        emotion="sadness",
        intensity=7,
        message_preview="I'm feeling really down today",
        topic="mental_health"
    )
    print(f"Saved emotion with ID: {emotion_id}")
    
    # Test retrieve
    emotions = db.get_emotions("test_user", days=30)
    print(f"\nFound {len(emotions)} emotions")
    
    # Test summary
    summary = db.get_emotion_summary("test_user", days=7)
    print(f"\nSummary: {json.dumps(summary, indent=2)}")