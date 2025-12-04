"""
Emotion Graph Generator
Generates visualizations and analytics from emotion data stored in emotion_db.py
"""

import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import Counter, defaultdict
import pandas as pd
from pathlib import Path

# Import existing emotion database
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.core.emotion_db import EmotionDB
except ImportError:
    # Fallback if emotion_db doesn't exist yet
    print("⚠️ emotion_db.py not found, using mock data for development")
    EmotionDB = None


class EmotionGraphGenerator:
    """
    Generates interactive visualizations from emotion data.
    Uses emotion_db.py to retrieve stored emotions.
    """
    
    def __init__(self, user_id: str):
        """
        Initialize graph generator for a specific user.
        
        Args:
            user_id: User identifier (email)
        """
        self.user_id = user_id
        self.db = EmotionDB() if EmotionDB else None
        
        # Color scheme for emotions
        self.emotion_colors = {
            "HAPPY": "#10b981",      # Green
            "SAD": "#3b82f6",        # Blue
            "ANXIOUS": "#f59e0b",    # Orange
            "ANGRY": "#ef4444",      # Red
            "FEARFUL": "#8b5cf6",    # Purple
            "HOPEFUL": "#06b6d4",    # Cyan
            "CALM": "#22c55e",       # Light green
            "EXCITED": "#f97316",    # Orange-red
            "LONELY": "#6b7280",     # Gray
            "GRATEFUL": "#84cc16",   # Lime
            "CONFUSED": "#a855f7",   # Purple
            "STRESSED": "#dc2626",   # Dark red
        }
    
    def generate_timeline_chart(self, days: int = 30) -> go.Figure:
        """
        Generate timeline showing emotion intensity over time.
        
        Args:
            days: Number of days to display
            
        Returns:
            Plotly figure object
        """
        if not self.db:
            return self._create_mock_timeline(days)
        
        # Get emotions from database
        emotions = self.db.get_emotions(self.user_id, days=days, limit=1000)
        
        if not emotions:
            return self._create_empty_chart("No emotion data available")
        
        # Convert to DataFrame
        df = pd.DataFrame(emotions)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        
        # Create figure
        fig = go.Figure()
        
        # Add trace for each emotion type
        for emotion in df['emotion'].unique():
            emotion_data = df[df['emotion'] == emotion]
            
            fig.add_trace(go.Scatter(
                x=emotion_data['timestamp'],
                y=emotion_data['intensity'],
                mode='lines+markers',
                name=emotion,
                line=dict(
                    color=self.emotion_colors.get(emotion, '#6b7280'),
                    width=2
                ),
                marker=dict(size=8),
                hovertemplate=(
                    f"<b>{emotion}</b><br>" +
                    "Intensity: %{y}<br>" +
                    "Time: %{x}<br>" +
                    "<extra></extra>"
                )
            ))
        
        # Update layout
        fig.update_layout(
            title=f"Emotional Journey - Last {days} Days",
            xaxis_title="Date",
            yaxis_title="Intensity (1-10)",
            hovermode='closest',
            template='plotly_white',
            height=500,
            font=dict(family="Arial, sans-serif", size=12),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            yaxis=dict(range=[0, 10.5])
        )
        
        return fig
    
    def generate_distribution_pie(self, days: int = 30) -> go.Figure:
        """
        Generate pie chart showing emotion distribution.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Plotly figure object
        """
        if not self.db:
            return self._create_mock_pie(days)
        
        # Get emotion counts
        counts = self.db.get_emotion_counts(self.user_id, days=days)
        
        if not counts:
            return self._create_empty_chart("No emotion data available")
        
        # Prepare data
        emotions = list(counts.keys())
        values = list(counts.values())
        colors = [self.emotion_colors.get(e, '#6b7280') for e in emotions]
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=emotions,
            values=values,
            marker=dict(colors=colors),
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
            textinfo='label+percent',
            textposition='auto'
        )])
        
        fig.update_layout(
            title=f"Emotion Distribution - Last {days} Days",
            template='plotly_white',
            height=500,
            font=dict(family="Arial, sans-serif", size=12),
            showlegend=True
        )
        
        return fig
    
    def generate_intensity_heatmap(self, days: int = 30) -> go.Figure:
        """
        Generate heatmap showing emotion patterns by day and time.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Plotly figure object
        """
        if not self.db:
            return self._create_mock_heatmap(days)
        
        emotions = self.db.get_emotions(self.user_id, days=days, limit=1000)
        
        if not emotions:
            return self._create_empty_chart("No emotion data available")
        
        # Convert to DataFrame
        df = pd.DataFrame(emotions)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['day_name'] = df['timestamp'].dt.day_name()
        
        # Calculate average intensity by hour and day
        heatmap_data = df.groupby(['day_name', 'hour'])['intensity'].mean().reset_index()
        
        # Pivot for heatmap format
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        pivot = heatmap_data.pivot(index='day_name', columns='hour', values='intensity')
        pivot = pivot.reindex(days_order)
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=[f"{h}:00" for h in range(24)],
            y=days_order,
            colorscale='RdYlGn_r',  # Red (high) to Green (low)
            hovertemplate='Day: %{y}<br>Hour: %{x}<br>Avg Intensity: %{z:.1f}<extra></extra>',
            colorbar=dict(title="Intensity")
        ))
        
        fig.update_layout(
            title=f"Emotion Intensity Patterns - Last {days} Days",
            xaxis_title="Hour of Day",
            yaxis_title="Day of Week",
            template='plotly_white',
            height=400,
            font=dict(family="Arial, sans-serif", size=12)
        )
        
        return fig
    
    def generate_weekly_summary(self) -> Dict:
        """
        Generate summary statistics for the past week.
        
        Returns:
            Dictionary with summary statistics
        """
        if not self.db:
            return self._create_mock_summary()
        
        emotions = self.db.get_emotions(self.user_id, days=7, limit=1000)
        
        if not emotions:
            return {
                "total_emotions": 0,
                "most_common": "N/A",
                "avg_intensity": 0,
                "trend": "neutral"
            }
        
        df = pd.DataFrame(emotions)
        
        # Calculate statistics
        emotion_counts = Counter(df['emotion'])
        most_common = emotion_counts.most_common(1)[0][0] if emotion_counts else "N/A"
        avg_intensity = df['intensity'].mean()
        
        # Calculate trend (comparing first half vs second half of week)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        midpoint = len(df) // 2
        
        first_half_avg = df.iloc[:midpoint]['intensity'].mean()
        second_half_avg = df.iloc[midpoint:]['intensity'].mean()
        
        if second_half_avg > first_half_avg + 0.5:
            trend = "improving"
        elif second_half_avg < first_half_avg - 0.5:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "total_emotions": len(emotions),
            "most_common": most_common,
            "avg_intensity": round(avg_intensity, 1),
            "trend": trend,
            "emotion_counts": dict(emotion_counts)
        }
    
    def generate_emotion_correlation(self, days: int = 30) -> go.Figure:
        """
        Generate correlation chart showing which emotions occur together.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Plotly figure object
        """
        if not self.db:
            return self._create_empty_chart("Correlation analysis requires more data")
        
        emotions = self.db.get_emotions(self.user_id, days=days, limit=1000)
        
        if len(emotions) < 10:
            return self._create_empty_chart("Need more data for correlation analysis")
        
        df = pd.DataFrame(emotions)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        
        # Count emotions per day
        daily_emotions = df.groupby(['date', 'emotion']).size().unstack(fill_value=0)
        
        # Calculate correlation
        correlation = daily_emotions.corr()
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=correlation.values,
            x=correlation.columns,
            y=correlation.columns,
            colorscale='RdBu',
            zmid=0,
            hovertemplate='%{x} vs %{y}<br>Correlation: %{z:.2f}<extra></extra>',
            colorbar=dict(title="Correlation")
        ))
        
        fig.update_layout(
            title=f"Emotion Correlations - Last {days} Days",
            template='plotly_white',
            height=500,
            font=dict(family="Arial, sans-serif", size=12)
        )
        
        return fig
    
    def generate_progress_chart(self, emotion: str, days: int = 30) -> go.Figure:
        """
        Generate progress chart for a specific emotion over time.
        
        Args:
            emotion: Emotion to track
            days: Number of days to display
            
        Returns:
            Plotly figure object
        """
        if not self.db:
            return self._create_empty_chart("Progress tracking requires historical data")
        
        trends = self.db.get_emotion_trends(self.user_id, emotion, days=days)
        
        if not trends:
            return self._create_empty_chart(f"No data for {emotion}")
        
        dates, intensities = zip(*trends)
        
        # Create line chart with moving average
        fig = go.Figure()
        
        # Actual data
        fig.add_trace(go.Scatter(
            x=dates,
            y=intensities,
            mode='lines+markers',
            name='Daily Average',
            line=dict(color=self.emotion_colors.get(emotion, '#6b7280'), width=2),
            marker=dict(size=8)
        ))
        
        # Moving average (7-day)
        if len(intensities) >= 7:
            ma = pd.Series(intensities).rolling(window=7, min_periods=1).mean()
            fig.add_trace(go.Scatter(
                x=dates,
                y=ma,
                mode='lines',
                name='7-Day Trend',
                line=dict(color='rgba(0,0,0,0.3)', width=2, dash='dash')
            ))
        
        fig.update_layout(
            title=f"{emotion} Intensity Trend - Last {days} Days",
            xaxis_title="Date",
            yaxis_title="Average Intensity",
            template='plotly_white',
            height=400,
            font=dict(family="Arial, sans-serif", size=12),
            yaxis=dict(range=[0, 10.5])
        )
        
        return fig
    
    # ════════════════════════════════════════════════════════════
    # HELPER METHODS
    # ════════════════════════════════════════════════════════════
    
    def _create_empty_chart(self, message: str) -> go.Figure:
        """Create empty chart with message."""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            template='plotly_white',
            height=400,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig
    
    def _create_mock_timeline(self, days: int) -> go.Figure:
        """Create mock timeline for testing."""
        import random
        
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        emotions_list = ["ANXIOUS", "HAPPY", "SAD", "CALM"]
        
        fig = go.Figure()
        for emotion in emotions_list:
            intensities = [random.randint(3, 9) for _ in range(days)]
            fig.add_trace(go.Scatter(
                x=dates,
                y=intensities,
                mode='lines+markers',
                name=emotion,
                line=dict(color=self.emotion_colors.get(emotion, '#6b7280'))
            ))
        
        fig.update_layout(
            title="Emotional Journey (Mock Data)",
            xaxis_title="Date",
            yaxis_title="Intensity",
            template='plotly_white',
            height=500
        )
        return fig
    
    def _create_mock_pie(self, days: int) -> go.Figure:
        """Create mock pie chart for testing."""
        emotions = ["ANXIOUS", "HAPPY", "SAD", "CALM"]
        values = [25, 35, 20, 20]
        colors = [self.emotion_colors.get(e, '#6b7280') for e in emotions]
        
        fig = go.Figure(data=[go.Pie(
            labels=emotions,
            values=values,
            marker=dict(colors=colors)
        )])
        
        fig.update_layout(
            title="Emotion Distribution (Mock Data)",
            template='plotly_white',
            height=500
        )
        return fig
    
    def _create_mock_heatmap(self, days: int) -> go.Figure:
        """Create mock heatmap for testing."""
        import numpy as np
        
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        hours = list(range(24))
        data = np.random.randint(3, 9, size=(7, 24))
        
        fig = go.Figure(data=go.Heatmap(
            z=data,
            x=[f"{h}:00" for h in hours],
            y=days_order,
            colorscale='RdYlGn_r'
        ))
        
        fig.update_layout(
            title="Emotion Patterns (Mock Data)",
            template='plotly_white',
            height=400
        )
        return fig
    
    def _create_mock_summary(self) -> Dict:
        """Create mock summary for testing."""
        return {
            "total_emotions": 42,
            "most_common": "ANXIOUS",
            "avg_intensity": 6.5,
            "trend": "improving",
            "emotion_counts": {
                "ANXIOUS": 15,
                "HAPPY": 12,
                "SAD": 8,
                "CALM": 7
            }
        }


# ════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ════════════════════════════════════════════════════════════

def get_emotion_summary_text(summary: Dict) -> str:
    """
    Convert summary dictionary to readable text.
    
    Args:
        summary: Summary dictionary from generate_weekly_summary()
        
    Returns:
        Formatted summary text
    """
    trend_emoji = {
        "improving": "📈",
        "declining": "📉",
        "stable": "➡️",
        "neutral": "➖"
    }
    
    text = f"""
    **Weekly Summary**
    
    {trend_emoji.get(summary['trend'], '➖')} **Trend:** {summary['trend'].capitalize()}
    
    📊 **Total Emotions Logged:** {summary['total_emotions']}
    
    🎯 **Most Common:** {summary['most_common']}
    
    💯 **Average Intensity:** {summary['avg_intensity']}/10
    """
    
    return text.strip()