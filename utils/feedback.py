import json
import boto3
import streamlit as st
from datetime import datetime
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


# Load feedback details from S3 Bucket
def save_feedback(feedback_data):
    # Add timestamp and ID to feedback
    feedback_data["timestamp"] = datetime.now().isoformat()

    try:
        # Create S3 client
        s3_client = boto3.client("s3")

        # Get existing feedback list from S3 or create new one
        try:
            response = s3_client.get_object(
                Bucket=S3_BUCKET_NAME, Key="feedback/all_feedback.json"
            )
            feedback_list = json.loads(response["Body"].read().decode("utf-8"))
        except Exception as e:
            print(f"Error loading feedback from S3: {e}")
            feedback_list = []

        # Append new feedback
        feedback_list.append(feedback_data)

        # Update the consolidated feedback file in S3
        consolidated_json = json.dumps(feedback_list, indent=2, ensure_ascii=False)
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key="feedback/all_feedback.json",
            Body=consolidated_json,
            ContentType="application/json",
            Metadata={
                "total_feedback": str(len(feedback_list)),
                "last_updated": datetime.now().isoformat(),
            },
        )
    except Exception as e:
        print(f"Error saving to S3: {e}")


# Display feedback form for user responses
def display_feedback_form(question, response, unique_key):
    st.markdown("---")

    # Create expandable feedback section
    with st.expander("📝 Rate This Response"):
        # Create columns for better layout
        col1, col2 = st.columns([3, 1])

        with col1:  # Rating system
            rating = st.select_slider(
                "How would you rate this response?",
                options=[1, 2, 3, 4, 5],
                value=3,
                format_func=lambda x: f"{x} {'⭐' * x}",
                key=f"rating_{unique_key}",
            )

            # Additional comments
            comments = st.text_area(
                "Additional comments:",
                placeholder="Please provide specific feedback about the response...",
                key=f"comments_{unique_key}",
            )

        with col2:
            st.write("**Quick Actions:**")
            # Quick feedback buttons
            if st.button("👍 Helpful", key=f"helpful_{unique_key}"):
                quick_feedback = {
                    "question": question,
                    "response": response,
                    "rating": 5,
                    "feedback_type": "positive",
                    "comments": "User marked as helpful",
                }
                save_feedback(quick_feedback)
                st.success("Thank you! 👍")

            if st.button("👎 Not Helpful", key=f"not_helpful_{unique_key}"):
                quick_feedback = {
                    "question": question,
                    "response": response,
                    "rating": 1,
                    "feedback_type": "negative",
                    "comments": "User marked as not helpful",
                }
                save_feedback(quick_feedback)
                st.warning("Thank you for the feedback!")
        # Submit detailed feedback
        if st.button("Submit Detailed Feedback", key=f"submit_{unique_key}"):
            feedback_data = {
                "question": question,
                "response": response,
                "rating": rating,
                "feedback_type": "detailed",
                "comments": comments,
            }

            save_feedback(feedback_data)
            st.success("Thank you for your detailed feedback! 🙏")


# Display feedback form for sources
def display_feedback_form_for_sources(question, response, doc, unique_key):
    """Display a simplified feedback form specifically for sources"""

    # Add a separator and header for the feedback section
    st.markdown("---")
    st.markdown("**📝 Rate This Source:**")

    # Rating system for source quality
    source_rating = st.select_slider(
        "How helpful was this source for answering your question?",
        options=[1, 2, 3, 4, 5],
        value=3,
        format_func=lambda x: f"{x} {'⭐' * x}",
        key=f"source_rating_{unique_key}",
    )

    # Comments for source feedback
    source_comments = st.text_area(
        "Comments about this source:",
        placeholder="Was this source relevant? Did it provide accurate information?",
        key=f"source_comments_{unique_key}",
        height=80,
    )
    # Submit source feedback
    if st.button("Submit Source Feedback", key=f"source_submit_{unique_key}"):
        source_feedback_data = {
            "question": question,
            "response": response,
            "source_content": doc.page_content
            if hasattr(doc, "page_content")
            else str(doc),
            "rating": source_rating,
            "feedback_type": "source",
            "comments": source_comments,
        }

        save_feedback(source_feedback_data)
        st.success("Thank you for rating this source! 📚")


# Load feedback data from S3 as DataFrame
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_feedback_data():
    try:
        # Load from S3
        s3_client = boto3.client("s3")
        response = s3_client.get_object(
            Bucket=S3_BUCKET_NAME, Key="feedback/all_feedback.json"
        )
        feedback_list = json.loads(response["Body"].read().decode("utf-8"))

        if feedback_list:
            df = pd.DataFrame(feedback_list)
            # Convert timestamp to datetime
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            return df
    except Exception as e:
        print(f"Error loading feedback from S3: {e}")

    return pd.DataFrame()


# Display the feedback dashboard with analytics and recent feedback
def display_feedback_dashboard():
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
        avg_rating = df["rating"].mean()
        st.metric("Average Rating", f"{avg_rating:.1f} ⭐")

    with col3:
        latest_feedback = df["timestamp"].max().strftime("%Y-%m-%d")
        st.metric("Latest Feedback", latest_feedback)

    with col4:
        positive_feedback = len(df[df["rating"] >= 4])
        positive_rate = (positive_feedback / len(df)) * 100
        st.metric("Positive Rate", f"{positive_rate:.1f}%")

    # Distribution chart
    st.subheader("Rating Distribution")
    rating_counts = df["rating"].value_counts().sort_index()
    st.bar_chart(rating_counts)

    # Recent feedback table
    st.subheader("Recent Detailed Response Feedback")
    # Filter only detailed feedback types
    detailed_df = df[df["feedback_type"] == "detailed"]
    if not detailed_df.empty:
        recent_detailed_df = detailed_df.nlargest(10, "timestamp")[
            ["timestamp", "rating", "question", "response", "feedback_type", "comments"]
        ].copy()
        recent_detailed_df["timestamp"] = recent_detailed_df["timestamp"].dt.strftime(
            "%Y-%m-%d %H:%M"
        )
        recent_detailed_df["question"] = recent_detailed_df["question"].astype(str)
        recent_detailed_df["response"] = recent_detailed_df["response"].astype(str)
        # Reorder columns for better display
        recent_detailed_df = recent_detailed_df[
            ["timestamp", "rating", "question", "response", "comments"]
        ]
        st.dataframe(recent_detailed_df, use_container_width=True)
    else:
        st.info("No detailed feedback available yet.")

    # Recent feedback for sources
    st.subheader("Recent Source Feedback")
    # Filter only source feedback types
    source_df = df[df["feedback_type"] == "source"]
    if not source_df.empty:
        recent_source_df = source_df.nlargest(10, "timestamp")[
            ["timestamp", "rating", "question", "source_content", "comments"]
        ].copy()
        recent_source_df["timestamp"] = recent_source_df["timestamp"].dt.strftime(
            "%Y-%m-%d %H:%M"
        )
        recent_source_df["question"] = recent_source_df["question"].astype(str)
        recent_source_df["source_content"] = recent_source_df["source_content"].astype(
            str
        )
        st.dataframe(recent_source_df, use_container_width=True)
    else:
        st.info("No source feedback available yet.")

    # Export functionality
    if st.button("📥 Export Feedback Data"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name=f"feedback_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )
