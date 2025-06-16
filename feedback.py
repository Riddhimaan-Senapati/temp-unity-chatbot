import os
import json
import streamlit as st
from datetime import datetime
import pandas as pd


def save_feedback(feedback_data):
    """Save user feedback to a JSON file"""
    feedback_folder = "feedback"
    feedback_file = os.path.join(feedback_folder, "user_feedback.json")
    
    # Create feedback folder if it doesn't exist
    os.makedirs(feedback_folder, exist_ok=True)
    
    # Load existing feedback or create new list
    if os.path.exists(feedback_file):
        with open(feedback_file, 'r', encoding='utf-8') as f:
            feedback_list = json.load(f)
    else:
        feedback_list = []
    
    # Add timestamp and ID to feedback
    feedback_data['timestamp'] = datetime.now().isoformat()
    feedback_data['feedback_id'] = len(feedback_list) + 1
    
    # Append new feedback
    feedback_list.append(feedback_data)
    
    # Save updated feedback
    with open(feedback_file, 'w', encoding='utf-8') as f:
        json.dump(feedback_list, f, indent=2, ensure_ascii=False)


def display_feedback_form(question, response, sources, unique_key):
    """Display feedback form for a specific response"""
    st.markdown("---")
    
    # Create expandable feedback section
    with st.expander("📝 Rate This Response"):
        # Create columns for better layout
        col1, col2 = st.columns([3, 1])
        
        with col1:            # Rating system
            rating = st.select_slider(
                "How would you rate this response?",
                options=[1, 2, 3, 4, 5],
                value=3,
                format_func=lambda x: f"{x} {'⭐' * x}",
                key=f"rating_{unique_key}"
            )
            
            # Additional comments
            comments = st.text_area(
                "Additional comments:",
                placeholder="Please provide specific feedback about the response...",
                key=f"comments_{unique_key}"
            )
        
        with col2:
            st.write("**Quick Actions:**")
              # Quick feedback buttons
            if st.button("👍 Helpful", key=f"helpful_{unique_key}"):
                quick_feedback = {
                    "question": question,
                    "response": response,
                    "sources": [doc.page_content if hasattr(doc, 'page_content') else str(doc) for doc in sources] if sources else [],
                    "rating": 5,
                    "feedback_type": "positive",
                    "comments": "User marked as helpful"
                }
                save_feedback(quick_feedback)
                st.success("Thank you! 👍")
            
            if st.button("👎 Not Helpful", key=f"not_helpful_{unique_key}"):
                quick_feedback = {
                    "question": question,
                    "response": response,
                    "sources": [doc.page_content if hasattr(doc, 'page_content') else str(doc) for doc in sources] if sources else [],
                    "rating": 2,
                    "feedback_type": "negative",
                    "comments": "User marked as not helpful"
                }
                save_feedback(quick_feedback)
                st.warning("Thank you for the feedback!")
          # Submit detailed feedback
        if st.button("Submit Detailed Feedback", key=f"submit_{unique_key}"):
            feedback_data = {
                "question": question,
                "response": response,
                "sources": [doc.page_content if hasattr(doc, 'page_content') else str(doc) for doc in sources] if sources else [],
                "rating": rating,
                "feedback_type": "detailed",
                "comments": comments
            }
            
            save_feedback(feedback_data)
            st.success("Thank you for your detailed feedback! 🙏")


def load_feedback_data():
    """Load feedback data from JSON file and return as pandas DataFrame"""
    feedback_folder = "feedback"
    feedback_file = os.path.join(feedback_folder, "user_feedback.json")
    
    if os.path.exists(feedback_file):
        with open(feedback_file, 'r', encoding='utf-8') as f:
            feedback_list = json.load(f)
        
        if feedback_list:
            df = pd.DataFrame(feedback_list)
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
    return pd.DataFrame()


def display_feedback_dashboard():
    """Display comprehensive feedback analytics for dashboard page"""
    st.header("📊 User Feedback Analytics")
    
    df = load_feedback_data()
    
    if df.empty:
        st.info("No feedback data available yet.")
        return
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Feedback", len(df))
    
    with col2:
        avg_rating = df['rating'].mean()
        st.metric("Average Rating", f"{avg_rating:.1f} ⭐")
    
    with col3:
        latest_feedback = df['timestamp'].max().strftime('%Y-%m-%d')
        st.metric("Latest Feedback", latest_feedback)
    
    with col4:
        positive_feedback = len(df[df['rating'] >= 4])
        positive_rate = (positive_feedback / len(df)) * 100
        st.metric("Positive Rate", f"{positive_rate:.1f}%")
    
    # Distribution chart

    st.subheader("Rating Distribution")
    rating_counts = df['rating'].value_counts().sort_index()
    st.bar_chart(rating_counts)

    # Recent feedback table
    st.subheader("Recent Detailed Feedback")
    # Filter only detailed feedback types
    detailed_df = df[df['feedback_type'] == 'detailed']
    if not detailed_df.empty:
        recent_detailed_df = detailed_df.nlargest(10, 'timestamp')[['timestamp', 'rating', 'question', 'response', 'feedback_type', 'comments']].copy()
        recent_detailed_df['timestamp'] = recent_detailed_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
        # Truncate question and response to first 50 characters
        recent_detailed_df['question'] = recent_detailed_df['question'].astype(str)
        recent_detailed_df['response'] = recent_detailed_df['response'].astype(str)
        # Reorder columns for better display
        recent_detailed_df = recent_detailed_df[['timestamp', 'rating', 'question', 'response', 'comments']]
        st.dataframe(recent_detailed_df, use_container_width=True)
    else:
        st.info("No detailed feedback available yet.")
    
    # Export functionality
    if st.button("📥 Export Feedback Data"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name=f"feedback_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
