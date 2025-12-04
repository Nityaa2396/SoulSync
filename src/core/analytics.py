"""
Emotion Analytics
Advanced analysis functions for emotion data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import Counter, defaultdict
import json


class EmotionAnalytics:
    """
    Advanced analytics for emotion data.
    Provides insights, patterns, and recommendations.
    """
    
    def __init__(self, emotions_data: List[Dict]):
        """
        Initialize analytics with emotion data.
        
        Args:
            emotions_data: List of emotion dictionaries from emotion_db
        """
        self.emotions = emotions_data
        self.df = pd.DataFrame(emotions_data) if emotions_data else pd.DataFrame()
        
        if not self.df.empty and 'timestamp' in self.df.columns:
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
            self.df['date'] = self.df['timestamp'].dt.date
            self.df['hour'] = self.df['timestamp'].dt.hour
            self.df['day_name'] = self.df['timestamp'].dt.day_name()
            self.df['week'] = self.df['timestamp'].dt.isocalendar().week
    
    def identify_patterns(self) -> Dict:
        """
        Identify recurring emotional patterns.
        
        Returns:
            Dictionary with identified patterns
        """
        if self.df.empty:
            return {"patterns": [], "insights": []}
        
        patterns = []
        insights = []
        
        # Pattern 1: Time-based patterns
        hourly_avg = self.df.groupby('hour')['intensity'].mean()
        if not hourly_avg.empty:
            worst_hour = hourly_avg.idxmax()
            best_hour = hourly_avg.idxmin()
            
            patterns.append({
                "type": "time_of_day",
                "description": f"Emotions tend to be most intense around {worst_hour}:00",
                "severity": "medium" if hourly_avg.max() > 7 else "low"
            })
            
            insights.append(f"Your emotions are typically calmer around {best_hour}:00")
        
        # Pattern 2: Day-based patterns
        daily_avg = self.df.groupby('day_name')['intensity'].mean()
        if not daily_avg.empty:
            worst_day = daily_avg.idxmax()
            
            patterns.append({
                "type": "day_of_week",
                "description": f"{worst_day}s tend to be more emotionally intense",
                "severity": "medium"
            })
        
        # Pattern 3: Emotion clustering
        emotion_counts = self.df['emotion'].value_counts()
        if len(emotion_counts) > 0:
            dominant_emotion = emotion_counts.index[0]
            percentage = (emotion_counts.iloc[0] / len(self.df)) * 100
            
            if percentage > 40:
                patterns.append({
                    "type": "dominant_emotion",
                    "description": f"{dominant_emotion} is your most common emotion ({percentage:.0f}%)",
                    "severity": "high" if dominant_emotion in ["SAD", "ANXIOUS", "ANGRY"] else "low"
                })
        
        # Pattern 4: Intensity trends
        if len(self.df) > 7:
            recent_avg = self.df.tail(7)['intensity'].mean()
            older_avg = self.df.head(7)['intensity'].mean()
            
            if recent_avg > older_avg + 1:
                patterns.append({
                    "type": "increasing_intensity",
                    "description": "Your emotional intensity has been increasing recently",
                    "severity": "high"
                })
                insights.append("Consider reaching out to a professional if emotions feel overwhelming")
            elif recent_avg < older_avg - 1:
                patterns.append({
                    "type": "decreasing_intensity",
                    "description": "Your emotional intensity has been decreasing - this is positive progress!",
                    "severity": "positive"
                })
        
        return {
            "patterns": patterns,
            "insights": insights
        }
    
    def calculate_emotional_diversity(self) -> Dict:
        """
        Calculate how diverse the user's emotional experiences are.
        
        Returns:
            Dictionary with diversity metrics
        """
        if self.df.empty:
            return {"diversity_score": 0, "interpretation": "No data"}
        
        emotion_counts = self.df['emotion'].value_counts()
        total_emotions = len(emotion_counts)
        
        # Shannon entropy for diversity
        proportions = emotion_counts / len(self.df)
        entropy = -sum(p * np.log(p) for p in proportions if p > 0)
        max_entropy = np.log(total_emotions) if total_emotions > 1 else 1
        diversity_score = (entropy / max_entropy) * 100 if max_entropy > 0 else 0
        
        # Interpretation
        if diversity_score > 75:
            interpretation = "High emotional diversity - you experience a wide range of emotions"
        elif diversity_score > 50:
            interpretation = "Moderate emotional diversity - you have varied emotional experiences"
        else:
            interpretation = "Low emotional diversity - emotions tend to be similar"
        
        return {
            "diversity_score": round(diversity_score, 1),
            "unique_emotions": total_emotions,
            "interpretation": interpretation,
            "dominant_emotions": emotion_counts.head(3).to_dict()
        }
    
    def detect_triggers(self) -> List[Dict]:
        """
        Detect potential emotional triggers based on message previews.
        
        Returns:
            List of potential triggers
        """
        if self.df.empty or 'message_preview' not in self.df.columns:
            return []
        
        triggers = []
        
        # Common trigger keywords
        trigger_keywords = {
            "work": ["work", "job", "boss", "colleague", "office", "deadline"],
            "relationships": ["boyfriend", "girlfriend", "partner", "relationship", "breakup"],
            "family": ["mom", "dad", "parent", "family", "sibling", "brother", "sister"],
            "health": ["sick", "pain", "doctor", "health", "anxiety", "panic"],
            "financial": ["money", "debt", "bills", "broke", "financial"],
            "social": ["friends", "lonely", "alone", "isolated", "rejected"]
        }
        
        # Analyze message previews
        for category, keywords in trigger_keywords.items():
            matching_rows = self.df[
                self.df['message_preview'].str.lower().str.contains('|'.join(keywords), na=False)
            ]
            
            if len(matching_rows) > 2:  # At least 3 occurrences
                avg_intensity = matching_rows['intensity'].mean()
                
                if avg_intensity > 6:
                    triggers.append({
                        "category": category,
                        "frequency": len(matching_rows),
                        "avg_intensity": round(avg_intensity, 1),
                        "severity": "high" if avg_intensity > 7.5 else "medium"
                    })
        
        return sorted(triggers, key=lambda x: x['avg_intensity'], reverse=True)
    
    def generate_recommendations(self) -> List[str]:
        """
        Generate personalized recommendations based on emotion patterns.
        
        Returns:
            List of recommendation strings
        """
        if self.df.empty:
            return ["Start logging your emotions to receive personalized insights"]
        
        recommendations = []
        
        # Analyze patterns
        patterns = self.identify_patterns()
        diversity = self.calculate_emotional_diversity()
        triggers = self.detect_triggers()
        
        # Recommendation 1: Based on dominant emotion
        if self.df['emotion'].mode().iloc[0] in ["ANXIOUS", "STRESSED"]:
            recommendations.append("🧘 Try daily mindfulness or breathing exercises to manage anxiety")
        
        # Recommendation 2: Based on intensity
        avg_intensity = self.df['intensity'].mean()
        if avg_intensity > 7:
            recommendations.append("💬 Your emotions are running high. Consider talking to a professional therapist")
        
        # Recommendation 3: Based on diversity
        if diversity['diversity_score'] < 50:
            recommendations.append("📝 Try exploring different activities to broaden your emotional experiences")
        
        # Recommendation 4: Based on time patterns
        hourly_avg = self.df.groupby('hour')['intensity'].mean()
        if not hourly_avg.empty:
            worst_hour = hourly_avg.idxmax()
            if hourly_avg.max() > 7:
                recommendations.append(f"⏰ Schedule self-care activities around {worst_hour}:00 when emotions peak")
        
        # Recommendation 5: Based on triggers
        if triggers:
            top_trigger = triggers[0]
            recommendations.append(f"🎯 {top_trigger['category'].capitalize()} appears to be a trigger. Develop coping strategies for this area")
        
        # Recommendation 6: Positive reinforcement
        if len(self.df) > 20:
            recent_avg = self.df.tail(7)['intensity'].mean()
            older_avg = self.df.head(7)['intensity'].mean()
            
            if recent_avg < older_avg:
                recommendations.append("✨ You're showing positive progress! Keep up the good work")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def calculate_resilience_score(self) -> Dict:
        """
        Calculate emotional resilience based on recovery patterns.
        
        Returns:
            Dictionary with resilience metrics
        """
        if len(self.df) < 14:
            return {
                "score": None,
                "interpretation": "Need at least 2 weeks of data to calculate resilience"
            }
        
        # Sort by timestamp
        df_sorted = self.df.sort_values('timestamp')
        
        # Find high-intensity episodes (intensity >= 8)
        high_intensity_mask = df_sorted['intensity'] >= 8
        
        if not high_intensity_mask.any():
            return {
                "score": 85,
                "interpretation": "High resilience - you maintain emotional stability well"
            }
        
        # Calculate recovery time after high-intensity emotions
        recovery_times = []
        
        for idx in df_sorted[high_intensity_mask].index:
            position = df_sorted.index.get_loc(idx)
            
            # Look at next 5 entries
            if position + 5 < len(df_sorted):
                future_intensities = df_sorted.iloc[position+1:position+6]['intensity'].values
                
                # How quickly does intensity drop below 6?
                for i, intensity in enumerate(future_intensities):
                    if intensity < 6:
                        recovery_times.append(i + 1)
                        break
        
        if recovery_times:
            avg_recovery = np.mean(recovery_times)
            
            # Score: faster recovery = higher resilience
            if avg_recovery <= 1:
                score = 90
                interpretation = "Excellent resilience - you recover quickly from emotional highs"
            elif avg_recovery <= 2:
                score = 75
                interpretation = "Good resilience - you generally bounce back well"
            elif avg_recovery <= 3:
                score = 60
                interpretation = "Moderate resilience - recovery takes some time"
            else:
                score = 45
                interpretation = "Building resilience - consider developing coping strategies"
        else:
            score = 70
            interpretation = "Resilience assessment inconclusive - continue tracking"
        
        return {
            "score": score,
            "interpretation": interpretation,
            "avg_recovery_time": round(np.mean(recovery_times), 1) if recovery_times else None
        }
    
    def generate_weekly_comparison(self) -> Dict:
        """
        Compare this week to previous weeks.
        
        Returns:
            Dictionary with comparison data
        """
        if len(self.df) < 14:
            return {
                "comparison_available": False,
                "message": "Need at least 2 weeks of data for comparison"
            }
        
        # Get current week and previous week
        current_week = self.df['week'].max()
        this_week_data = self.df[self.df['week'] == current_week]
        last_week_data = self.df[self.df['week'] == current_week - 1]
        
        if this_week_data.empty or last_week_data.empty:
            return {
                "comparison_available": False,
                "message": "Insufficient data for weekly comparison"
            }
        
        # Calculate metrics
        this_week_avg = this_week_data['intensity'].mean()
        last_week_avg = last_week_data['intensity'].mean()
        
        change = this_week_avg - last_week_avg
        change_pct = (change / last_week_avg) * 100 if last_week_avg > 0 else 0
        
        # Most common emotions
        this_week_top = this_week_data['emotion'].value_counts().head(3).to_dict()
        last_week_top = last_week_data['emotion'].value_counts().head(3).to_dict()
        
        return {
            "comparison_available": True,
            "this_week": {
                "avg_intensity": round(this_week_avg, 1),
                "total_emotions": len(this_week_data),
                "top_emotions": this_week_top
            },
            "last_week": {
                "avg_intensity": round(last_week_avg, 1),
                "total_emotions": len(last_week_data),
                "top_emotions": last_week_top
            },
            "change": round(change, 1),
            "change_percentage": round(change_pct, 1),
            "trend": "improving" if change < -0.5 else "worsening" if change > 0.5 else "stable"
        }
    
    def export_summary_report(self) -> str:
        """
        Generate a comprehensive text summary report.
        
        Returns:
            Formatted text report
        """
        if self.df.empty:
            return "No emotion data available for report generation."
        
        # Gather all analytics
        patterns = self.identify_patterns()
        diversity = self.calculate_emotional_diversity()
        triggers = self.detect_triggers()
        recommendations = self.generate_recommendations()
        resilience = self.calculate_resilience_score()
        
        # Build report
        report = f"""
═══════════════════════════════════════════════════════
                EMOTIONAL WELLNESS REPORT
═══════════════════════════════════════════════════════

📊 OVERVIEW
───────────────────────────────────────────────────────
Total Emotions Logged: {len(self.df)}
Date Range: {self.df['timestamp'].min().date()} to {self.df['timestamp'].max().date()}
Average Intensity: {self.df['intensity'].mean():.1f}/10

💡 EMOTIONAL DIVERSITY
───────────────────────────────────────────────────────
Diversity Score: {diversity['diversity_score']:.1f}%
{diversity['interpretation']}

Unique Emotions: {diversity['unique_emotions']}
Top Emotions: {', '.join(f"{k} ({v})" for k, v in list(diversity['dominant_emotions'].items())[:3])}

🔄 PATTERNS IDENTIFIED
───────────────────────────────────────────────────────
"""
        
        for i, pattern in enumerate(patterns['patterns'][:5], 1):
            report += f"{i}. {pattern['description']}\n"
        
        if triggers:
            report += "\n🎯 POTENTIAL TRIGGERS\n"
            report += "───────────────────────────────────────────────────────\n"
            for trigger in triggers[:3]:
                report += f"• {trigger['category'].capitalize()}: {trigger['frequency']} occurrences (avg intensity: {trigger['avg_intensity']})\n"
        
        if resilience['score']:
            report += f"\n💪 RESILIENCE SCORE\n"
            report += "───────────────────────────────────────────────────────\n"
            report += f"Score: {resilience['score']}/100\n"
            report += f"{resilience['interpretation']}\n"
        
        report += "\n✨ RECOMMENDATIONS\n"
        report += "───────────────────────────────────────────────────────\n"
        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n"
        
        report += "\n═══════════════════════════════════════════════════════\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        report += "═══════════════════════════════════════════════════════\n"
        
        return report


# ════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ════════════════════════════════════════════════════════════

def quick_insights(emotions_data: List[Dict]) -> str:
    """
    Generate quick insights from emotion data.
    
    Args:
        emotions_data: List of emotion dictionaries
        
    Returns:
        Quick insight string
    """
    if not emotions_data:
        return "No data available"
    
    analytics = EmotionAnalytics(emotions_data)
    
    avg_intensity = analytics.df['intensity'].mean()
    most_common = analytics.df['emotion'].mode().iloc[0]
    total = len(emotions_data)
    
    return f"📊 {total} emotions logged | 🎯 Most common: {most_common} | 💯 Avg intensity: {avg_intensity:.1f}/10"