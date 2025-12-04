"""
Emotion Dashboard UI
Add this to your Streamlit app to display emotional graphs and analytics
"""

import streamlit as st
from datetime import datetime, timedelta
import sys
import os

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.emotion_graph import EmotionGraphGenerator, get_emotion_summary_text
from src.core.analytics import EmotionAnalytics, quick_insights
from src.core.emotion_db import EmotionDB


def render_emotion_dashboard(user_id: str):
    """
    Main dashboard rendering function.
    Call this from your streamlit_app.py
    
    Args:
        user_id: Current user's ID (email)
    """
    
    st.title("📊 My Emotional Journey")
    st.caption("Visualize and understand your emotional patterns")
    
    # ════════════════════════════════════════════════════════════
    # SIDEBAR FILTERS
    # ════════════════════════════════════════════════════════════
    
    with st.sidebar:
        # ✅ BACK BUTTON AT TOP OF SIDEBAR
        if st.button("← Back to Chat", key="back_to_chat", use_container_width=True, type="primary"):
            st.session_state.show_dashboard = False
            st.rerun()
        
        st.divider()
        
        st.markdown("### 📅 Time Range")
        
        time_range = st.selectbox(
            "Select period",
            ["Last 7 days", "Last 30 days", "Last 90 days", "All time"],
            index=1
        )
        
        # Convert to days
        days_map = {
            "Last 7 days": 7,
            "Last 30 days": 30,
            "Last 90 days": 90,
            "All time": 365
        }
        days = days_map[time_range]
        
        st.divider()
        
        st.markdown("### 🎨 Display Options")
        show_timeline = st.checkbox("Timeline Chart", value=True)
        show_distribution = st.checkbox("Emotion Distribution", value=True)
        show_heatmap = st.checkbox("Pattern Heatmap", value=True)
        show_analytics = st.checkbox("Advanced Analytics", value=True)
    
    # ════════════════════════════════════════════════════════════
    # INITIALIZE COMPONENTS
    # ════════════════════════════════════════════════════════════
    
    graph_gen = EmotionGraphGenerator(user_id)
    db = EmotionDB()
    
    # Get emotion data
    emotions_data = db.get_emotions(user_id, days=days, limit=1000)
    
    if not emotions_data:
        st.info("👋 Start chatting to begin tracking your emotional journey!")
        st.markdown("""
        **How it works:**
        1. Chat with SoulSync in any therapy room
        2. Your emotions are automatically detected and logged
        3. Return here to see beautiful visualizations and insights
        
        💡 The more you chat, the better insights you'll receive!
        """)
        st.stop()
    
    # ════════════════════════════════════════════════════════════
    # QUICK SUMMARY
    # ════════════════════════════════════════════════════════════
    
    st.markdown("### 📈 Quick Summary")
    
    summary = graph_gen.generate_weekly_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Emotions",
            summary['total_emotions'],
            delta=None
        )
    
    with col2:
        st.metric(
            "Most Common",
            summary['most_common'],
            delta=None
        )
    
    with col3:
        st.metric(
            "Avg Intensity",
            f"{summary['avg_intensity']}/10",
            delta=None
        )
    
    with col4:
        trend_icons = {
            "improving": "📈",
            "declining": "📉",
            "stable": "➡️"
        }
        st.metric(
            "Trend",
            summary['trend'].capitalize(),
            delta=trend_icons.get(summary['trend'], "➡️")
        )
    
    st.divider()
    
    # ════════════════════════════════════════════════════════════
    # TIMELINE CHART
    # ════════════════════════════════════════════════════════════
    
    if show_timeline:
        st.markdown("### 📅 Emotional Timeline")
        st.caption("See how your emotions change over time")
        
        timeline_fig = graph_gen.generate_timeline_chart(days=days)
        st.plotly_chart(timeline_fig, use_container_width=True)
        
        st.divider()
    
    # ════════════════════════════════════════════════════════════
    # DISTRIBUTION PIE CHART
    # ════════════════════════════════════════════════════════════
    
    if show_distribution:
        st.markdown("### 🥧 Emotion Distribution")
        st.caption("Which emotions do you experience most?")
        
        pie_fig = graph_gen.generate_distribution_pie(days=days)
        st.plotly_chart(pie_fig, use_container_width=True)
        
        st.divider()
    
    # ════════════════════════════════════════════════════════════
    # HEATMAP
    # ════════════════════════════════════════════════════════════
    
    if show_heatmap:
        st.markdown("### 🗓️ Pattern Heatmap")
        st.caption("Identify when emotions are most intense")
        
        heatmap_fig = graph_gen.generate_intensity_heatmap(days=days)
        st.plotly_chart(heatmap_fig, use_container_width=True)
        
        st.divider()
    
    # ════════════════════════════════════════════════════════════
    # ADVANCED ANALYTICS
    # ════════════════════════════════════════════════════════════
    
    if show_analytics and len(emotions_data) >= 10:
        st.markdown("### 🔍 Advanced Analytics")
        
        analytics = EmotionAnalytics(emotions_data)
        
        # Tabs for different analytics
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Patterns", "🎯 Triggers", "💪 Resilience", "✨ Recommendations"])
        
        with tab1:
            st.markdown("#### Identified Patterns")
            
            patterns_data = analytics.identify_patterns()
            
            if patterns_data['patterns']:
                for pattern in patterns_data['patterns']:
                    severity_colors = {
                        "high": "🔴",
                        "medium": "🟡",
                        "low": "🟢",
                        "positive": "✨"
                    }
                    icon = severity_colors.get(pattern['severity'], "ℹ️")
                    
                    st.markdown(f"{icon} **{pattern['type'].replace('_', ' ').title()}**")
                    st.write(pattern['description'])
                    st.write("")
            else:
                st.info("Not enough data to identify patterns yet. Keep tracking!")
            
            if patterns_data['insights']:
                st.markdown("#### 💡 Insights")
                for insight in patterns_data['insights']:
                    st.info(insight)
        
        with tab2:
            st.markdown("#### Potential Triggers")
            
            triggers = analytics.detect_triggers()
            
            if triggers:
                for trigger in triggers:
                    severity_icon = "🔴" if trigger['severity'] == "high" else "🟡"
                    
                    st.markdown(f"{severity_icon} **{trigger['category'].title()}**")
                    st.write(f"Frequency: {trigger['frequency']} times | Avg Intensity: {trigger['avg_intensity']}/10")
                    st.write("")
            else:
                st.info("No specific triggers identified yet. Continue tracking to find patterns.")
        
        with tab3:
            st.markdown("#### Emotional Resilience")
            
            resilience = analytics.calculate_resilience_score()
            
            if resilience['score']:
                st.metric("Resilience Score", f"{resilience['score']}/100")
                st.write(resilience['interpretation'])
                
                if resilience.get('avg_recovery_time'):
                    st.write(f"**Average Recovery Time:** {resilience['avg_recovery_time']} emotional check-ins")
            else:
                st.info(resilience['interpretation'])
        
        with tab4:
            st.markdown("#### Personalized Recommendations")
            
            recommendations = analytics.generate_recommendations()
            
            for rec in recommendations:
                st.markdown(f"• {rec}")
        
        st.divider()
    
    # ════════════════════════════════════════════════════════════
    # EXPORT OPTIONS
    # ════════════════════════════════════════════════════════════
    
    st.markdown("### 📥 Export & Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Generate Text Report", use_container_width=True):
            analytics = EmotionAnalytics(emotions_data)
            report = analytics.export_summary_report()
            
            st.download_button(
                label="Download Report",
                data=report,
                file_name=f"emotional_wellness_report_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
            with st.expander("📄 View Report"):
                st.text(report)
    
    with col2:
        if st.button("📊 Export Data (JSON)", use_container_width=True):
            import json
            
            export_data = {
                "user_id": user_id,
                "export_date": datetime.now().isoformat(),
                "time_range_days": days,
                "emotions": emotions_data,
                "summary": summary
            }
            
            st.download_button(
                label="Download JSON",
                data=json.dumps(export_data, indent=2),
                file_name=f"emotions_export_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    # ════════════════════════════════════════════════════════════
    # FOOTER
    # ════════════════════════════════════════════════════════════
    
    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Total emotions logged: {len(emotions_data)}")


# ════════════════════════════════════════════════════════════
# ALTERNATIVE: MINIMAL DASHBOARD (For sidebar)
# ════════════════════════════════════════════════════════════

def render_mini_dashboard(user_id: str):
    """
    Minimal dashboard for sidebar display.
    
    Args:
        user_id: Current user's ID
    """
    st.markdown("### 📊 Quick Insights")
    
    db = EmotionDB()
    emotions_data = db.get_emotions(user_id, days=7, limit=100)
    
    if not emotions_data:
        st.caption("Start chatting to see insights!")
        return
    
    # Quick summary
    insight_text = quick_insights(emotions_data)
    st.caption(insight_text)
    
    # Mini pie chart
    from src.core.emotion_graph import EmotionGraphGenerator
    graph_gen = EmotionGraphGenerator(user_id)
    
    mini_fig = graph_gen.generate_distribution_pie(days=7)
    mini_fig.update_layout(height=250, showlegend=False)
    st.plotly_chart(mini_fig, use_container_width=True)
    
    if st.button("📊 View Full Dashboard", use_container_width=True):
        st.session_state.show_dashboard = True
        st.rerun()


# ════════════════════════════════════════════════════════════
# TESTING / DEMO MODE
# ════════════════════════════════════════════════════════════

def demo_dashboard():
    """
    Demo dashboard with mock data for testing.
    """
    st.title("📊 Emotional Journey Dashboard (Demo)")
    st.info("This is a demo with mock data. Connect to real emotion_db for actual data.")
    
    graph_gen = EmotionGraphGenerator("demo_user")
    
    # Timeline
    st.markdown("### 📅 Timeline")
    timeline = graph_gen.generate_timeline_chart(days=30)
    st.plotly_chart(timeline, use_container_width=True)
    
    # Pie chart
    st.markdown("### 🥧 Distribution")
    pie = graph_gen.generate_distribution_pie(days=30)
    st.plotly_chart(pie, use_container_width=True)
    
    # Heatmap
    st.markdown("### 🗓️ Heatmap")
    heatmap = graph_gen.generate_intensity_heatmap(days=30)
    st.plotly_chart(heatmap, use_container_width=True)
    
    # Summary
    st.markdown("### 📈 Summary")
    summary = graph_gen.generate_weekly_summary()
    st.json(summary)


if __name__ == "__main__":
    # For testing
    demo_dashboard()