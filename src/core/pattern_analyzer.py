"""
Pattern Analyzer - Detects patterns in emotional data
Identifies trends, cycles, and concerning patterns.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter
import statistics


class PatternAnalyzer:
    """Analyzes emotional patterns over time."""
    
    def __init__(self, emotion_db):
        """
        Initialize pattern analyzer.
        
        Args:
            emotion_db: EmotionDB instance
        """
        self.db = emotion_db
    
    def detect_trends(self, user_id: str, emotion: str, days: int = 30) -> Dict:
        """
        Detect if emotion is increasing, decreasing, or stable.
        
        Args:
            user_id: User identifier
            emotion: Emotion to analyze
            days: Number of days to analyze
            
        Returns:
            Dict with trend analysis
        """
        trends = self.db.get_emotion_trends(user_id, emotion, days)
        
        if len(trends) < 3:
            return {
                "trend": "insufficient_data",
                "direction": None,
                "confidence": 0.0,
                "data_points": len(trends)
            }
        
        # Calculate trend using simple linear regression approach
        dates = [i for i in range(len(trends))]
        intensities = [intensity for _, intensity in trends]
        
        # Calculate slope
        mean_x = statistics.mean(dates)
        mean_y = statistics.mean(intensities)
        
        numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(dates, intensities))
        denominator = sum((x - mean_x) ** 2 for x in dates)
        
        slope = numerator / denominator if denominator != 0 else 0
        
        # Determine trend
        if abs(slope) < 0.1:
            direction = "stable"
        elif slope > 0:
            direction = "increasing"
        else:
            direction = "decreasing"
        
        # Confidence based on data points and slope magnitude
        confidence = min(len(trends) / 30, 1.0) * min(abs(slope), 1.0)
        
        return {
            "trend": direction,
            "direction": direction,
            "slope": slope,
            "confidence": confidence,
            "data_points": len(trends),
            "avg_intensity": mean_y,
            "recent_intensity": intensities[-1] if intensities else 0
        }
    
    def detect_emotion_clusters(self, user_id: str, days: int = 7) -> List[Dict]:
        """
        Detect clusters of related emotions.
        
        Args:
            user_id: User identifier
            days: Number of days to analyze
            
        Returns:
            List of emotion clusters
        """
        emotions = self.db.get_emotions(user_id, days)
        
        # Group related emotions
        emotion_groups = {
            "distress": ["sadness", "grief", "depression", "hopelessness"],
            "anxiety": ["anxiety", "fear", "worry", "panic", "stress"],
            "anger": ["anger", "frustration", "rage", "irritation"],
            "shame": ["shame", "guilt", "embarrassment", "inadequacy"],
            "isolation": ["loneliness", "isolation", "rejection", "abandonment"],
            "positive": ["joy", "happiness", "contentment", "gratitude", "hope"]
        }
        
        clusters = []
        
        for cluster_name, emotion_list in emotion_groups.items():
            cluster_emotions = [e for e in emotions if e['emotion'] in emotion_list]
            
            if cluster_emotions:
                avg_intensity = statistics.mean([e['intensity'] for e in cluster_emotions])
                
                clusters.append({
                    "cluster": cluster_name,
                    "count": len(cluster_emotions),
                    "emotions": list(set([e['emotion'] for e in cluster_emotions])),
                    "avg_intensity": avg_intensity,
                    "percentage": len(cluster_emotions) / len(emotions) * 100
                })
        
        # Sort by count
        clusters.sort(key=lambda x: x['count'], reverse=True)
        
        return clusters
    
    def detect_concerning_patterns(self, user_id: str, days: int = 7) -> List[Dict]:
        """
        Detect patterns that may indicate crisis or need for escalation.
        
        Args:
            user_id: User identifier
            days: Number of days to analyze
            
        Returns:
            List of concerning patterns
        """
        emotions = self.db.get_emotions(user_id, days)
        concerns = []
        
        if not emotions:
            return concerns
        
        # 1. High frequency of high-intensity emotions
        high_intensity = [e for e in emotions if e['intensity'] >= 8]
        if len(high_intensity) >= 5:
            concerns.append({
                "type": "high_intensity_frequency",
                "severity": "high" if len(high_intensity) >= 10 else "medium",
                "description": f"{len(high_intensity)} high-intensity emotions in {days} days",
                "recommendation": "Consider reaching out for professional support"
            })
        
        # 2. Sustained hopelessness/depression
        hopeless_emotions = [e for e in emotions if e['emotion'] in 
                           ['hopelessness', 'depression', 'despair', 'worthlessness']]
        if len(hopeless_emotions) >= 3:
            avg_intensity = statistics.mean([e['intensity'] for e in hopeless_emotions])
            if avg_intensity >= 7:
                concerns.append({
                    "type": "sustained_hopelessness",
                    "severity": "high",
                    "description": f"Consistent feelings of hopelessness (avg intensity: {avg_intensity:.1f})",
                    "recommendation": "Professional support strongly recommended"
                })
        
        # 3. Increasing anxiety trend
        anxiety_emotions = [e for e in emotions if e['emotion'] in 
                          ['anxiety', 'panic', 'fear', 'worry']]
        if len(anxiety_emotions) >= 3:
            # Check if intensities are increasing
            recent = anxiety_emotions[:len(anxiety_emotions)//2]
            older = anxiety_emotions[len(anxiety_emotions)//2:]
            
            if recent and older:
                recent_avg = statistics.mean([e['intensity'] for e in recent])
                older_avg = statistics.mean([e['intensity'] for e in older])
                
                if recent_avg > older_avg + 1:
                    concerns.append({
                        "type": "escalating_anxiety",
                        "severity": "medium",
                        "description": f"Anxiety appears to be increasing over time",
                        "recommendation": "Consider anxiety management techniques or professional help"
                    })
        
        # 4. Social isolation indicators
        isolation_emotions = [e for e in emotions if e['emotion'] in 
                            ['loneliness', 'isolation', 'rejection', 'abandonment']]
        if len(isolation_emotions) >= 4:
            concerns.append({
                "type": "social_isolation",
                "severity": "medium",
                "description": f"Frequent feelings of isolation ({len(isolation_emotions)} instances)",
                "recommendation": "Focus on social connection and support systems"
            })
        
        return concerns
    
    def get_emotion_diversity(self, user_id: str, days: int = 7) -> Dict:
        """
        Calculate emotional diversity (variety of emotions experienced).
        
        Args:
            user_id: User identifier
            days: Number of days to analyze
            
        Returns:
            Diversity metrics
        """
        emotions = self.db.get_emotions(user_id, days)
        
        if not emotions:
            return {
                "diversity_score": 0,
                "unique_emotions": 0,
                "total_emotions": 0,
                "most_common": None
            }
        
        emotion_names = [e['emotion'] for e in emotions]
        unique_emotions = set(emotion_names)
        emotion_counts = Counter(emotion_names)
        
        # Diversity score: ratio of unique to total, weighted by distribution
        diversity_score = len(unique_emotions) / len(emotions)
        
        return {
            "diversity_score": diversity_score,
            "unique_emotions": len(unique_emotions),
            "total_emotions": len(emotions),
            "most_common": emotion_counts.most_common(1)[0] if emotion_counts else None,
            "emotion_distribution": dict(emotion_counts)
        }
    
    def get_intensity_volatility(self, user_id: str, days: int = 7) -> Dict:
        """
        Measure how much emotion intensity varies (emotional stability).
        
        Args:
            user_id: User identifier
            days: Number of days to analyze
            
        Returns:
            Volatility metrics
        """
        emotions = self.db.get_emotions(user_id, days)
        
        if len(emotions) < 2:
            return {
                "volatility": 0,
                "stability": "insufficient_data",
                "std_dev": 0,
                "range": 0
            }
        
        intensities = [e['intensity'] for e in emotions]
        
        mean_intensity = statistics.mean(intensities)
        std_dev = statistics.stdev(intensities) if len(intensities) > 1 else 0
        intensity_range = max(intensities) - min(intensities)
        
        # Volatility score (0-1, higher = more volatile)
        volatility = min(std_dev / 5, 1.0)  # Normalize to 0-1
        
        if volatility < 0.3:
            stability = "stable"
        elif volatility < 0.6:
            stability = "moderate"
        else:
            stability = "volatile"
        
        return {
            "volatility": volatility,
            "stability": stability,
            "std_dev": std_dev,
            "range": intensity_range,
            "mean_intensity": mean_intensity
        }
    
    def generate_weekly_summary(self, user_id: str) -> Dict:
        """
        Generate comprehensive weekly emotional summary.
        
        Args:
            user_id: User identifier
            
        Returns:
            Weekly summary dictionary
        """
        # Get data
        emotions = self.db.get_emotions(user_id, days=7)
        
        if not emotions:
            return {
                "period": "7 days",
                "total_entries": 0,
                "message": "No emotion data available for this period"
            }
        
        # Basic stats
        summary = self.db.get_emotion_summary(user_id, days=7)
        
        # Patterns
        clusters = self.detect_emotion_clusters(user_id, days=7)
        concerns = self.detect_concerning_patterns(user_id, days=7)
        diversity = self.get_emotion_diversity(user_id, days=7)
        volatility = self.get_intensity_volatility(user_id, days=7)
        
        # Trends for dominant emotions
        trends = {}
        if summary['emotion_counts']:
            top_emotions = sorted(summary['emotion_counts'].items(), 
                                key=lambda x: x[1], reverse=True)[:3]
            for emotion, _ in top_emotions:
                trends[emotion] = self.detect_trends(user_id, emotion, days=7)
        
        return {
            "period": "7 days",
            "total_entries": summary['total_entries'],
            "avg_intensity": summary['avg_intensity'],
            "dominant_emotion": summary['dominant_emotion'],
            "emotion_counts": summary['emotion_counts'],
            "clusters": clusters,
            "diversity": diversity,
            "volatility": volatility,
            "trends": trends,
            "concerns": concerns,
            "high_intensity_count": summary['high_intensity_count']
        }
    
    def get_insights(self, user_id: str, days: int = 7) -> List[str]:
        """
        Generate human-readable insights from patterns.
        
        Args:
            user_id: User identifier
            days: Number of days to analyze
            
        Returns:
            List of insight strings
        """
        insights = []
        
        summary = self.db.get_emotion_summary(user_id, days)
        
        if summary['total_entries'] == 0:
            return ["Not enough data to generate insights yet. Keep tracking your emotions!"]
        
        # Dominant emotion
        if summary['dominant_emotion']:
            insights.append(
                f"Your most frequent emotion this week has been {summary['dominant_emotion']}."
            )
        
        # Intensity
        if summary['avg_intensity'] >= 7:
            insights.append(
                "Your emotions have been quite intense lately. This might be a good time for self-care."
            )
        elif summary['avg_intensity'] <= 4:
            insights.append(
                "Your emotional intensity has been relatively low, which could indicate stability or numbness."
            )
        
        # Diversity
        diversity = self.get_emotion_diversity(user_id, days)
        if diversity['diversity_score'] < 0.3:
            insights.append(
                "You've experienced a narrow range of emotions. This might indicate being stuck in a particular state."
            )
        elif diversity['diversity_score'] > 0.6:
            insights.append(
                "You've experienced a wide range of emotions, which shows emotional flexibility."
            )
        
        # Volatility
        volatility = self.get_intensity_volatility(user_id, days)
        if volatility['stability'] == "volatile":
            insights.append(
                "Your emotional intensity has varied significantly. Consider what triggers these shifts."
            )
        elif volatility['stability'] == "stable":
            insights.append(
                "Your emotions have been relatively stable, which can be a sign of good regulation."
            )
        
        # Concerns
        concerns = self.detect_concerning_patterns(user_id, days)
        if concerns:
            high_severity = [c for c in concerns if c['severity'] == 'high']
            if high_severity:
                insights.append(
                    "⚠️ Some concerning patterns detected. Consider reaching out for professional support."
                )
        
        return insights


# Example usage
if __name__ == "__main__":
    from emotion_db import EmotionDB
    
    db = EmotionDB()
    analyzer = PatternAnalyzer(db)
    
    # Generate weekly summary
    summary = analyzer.generate_weekly_summary("test_user")
    print("Weekly Summary:")
    print(f"Total entries: {summary['total_entries']}")
    print(f"Average intensity: {summary['avg_intensity']:.1f}")
    print(f"Dominant emotion: {summary['dominant_emotion']}")
    
    # Get insights
    insights = analyzer.get_insights("test_user", days=7)
    print("\nInsights:")
    for insight in insights:
        print(f"• {insight}")