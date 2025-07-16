import streamlit as st
import datetime
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import os
from dotenv import load_dotenv
import pandas as pd
import json
from utils.data_pipeline.scrape_and_upload_to_s3 import (
    run_scrape_and_upload_pipeline,
    scrape_and_upload_link,
)
from utils.feedback import display_feedback_dashboard
from slack_scripts.slack_scraper import main as slack_scraper_main
from qa_pairs.slack_qa_generator import main as slack_qa_main

load_dotenv()

#  Configuration
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_FOLDER_PREFIX = os.getenv("S3_FOLDER_PREFIX")


#  S3 Data Retrieval Function
@st.cache_data(ttl=3600)  # Cache data for 1 hour
def get_scraped_data_from_s3(bucket_name, prefix):
    """
    Connects to S3, lists objects, and extracts source URL and scraped datetime from metadata.
    Returns a list of dictionaries, each representing a scraped item.
    """
    scraped_items_list = []
    try:
        s3 = boto3.client("s3")
        paginator = s3.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

        for page in pages:
            if "Contents" in page:
                for obj in page["Contents"]:
                    key = obj["Key"]
                    if key.endswith("/"):  # Skip S3 folder objects
                        continue
                    try:
                        head_object = s3.head_object(Bucket=bucket_name, Key=key)
                        metadata = head_object.get("Metadata", {})
                        source_url = metadata.get("sourceurl")
                        scraped_datetime_str = metadata.get("scrapeddatetime")

                        if source_url and scraped_datetime_str:
                            try:
                                scraped_datetime = datetime.datetime.fromisoformat(
                                    scraped_datetime_str
                                )
                                scraped_items_list.append(
                                    {
                                        "URL": source_url,
                                        "Last Scraped": scraped_datetime,
                                        "S3 Key": key,
                                    }
                                )
                            except ValueError:
                                st.warning(
                                    f"Could not parse datetime '{scraped_datetime_str}' for {source_url} (Key: {key})"
                                )

                    except ClientError as e:
                        if e.response["Error"]["Code"] == "404":
                            st.error(
                                f"S3 object not found: {key}"
                            )  # S3 object not found error
                        else:
                            st.error(
                                f"Error accessing S3 metadata for {key}: {e}"
                            )  # S3 metadata error
                    except Exception as e:
                        st.error(
                            f"Unexpected error processing S3 object {key}: {e}"
                        )  # Unknown S3 object processing error

    except NoCredentialsError:
        st.error("AWS credentials not found. Please configure your AWS credentials.")
        return None  # Indicate critical AWS credential error
    except ClientError as e:
        st.error(f"S3 client error: {e}")
        return None  # Indicate critical client error
    except Exception as e:
        st.error(f"An unexpected error occurred while fetching S3 data: {e}")
        return None  # Indicate critical unknown error
    return scraped_items_list


# Streamlit Dashboard Layout
st.set_page_config(layout="wide")
st.title("Unity Documentation Chatbot Dashboard")

# initialize logged_in session state variable
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Infobox to tell the user to log in on the main page
if not st.session_state.logged_in:
    st.info("Please Login on the main page")
    st.stop()

# Create tabs for different dashboard sections
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "User Feedback Analytics",
        "Data Pipeline Management",
        "Slack Conversations",
        "Q&A Pair Review",
        "Add Knowledge",
    ]
)

with tab1:
    st.header("📊 User Feedback Analytics")

    # Add refresh button for feedback
    if st.button("🔄 Refresh Feedback Data", key="refresh_feedback"):
        st.cache_data.clear()
        st.rerun()

    display_feedback_dashboard()

with tab2:
    st.header("📄 Data Pipeline Dashboard")

    #  Session State Initialization for DataFrame
    if "df_display_data" not in st.session_state:
        st.session_state.df_display_data = pd.DataFrame(
            columns=["URL", "Last Scraped", "S3 Key"]
        )

    def refresh_dashboard_data():
        """Clears S3 cache and reruns the app to fetch updated data."""
        st.cache_data.clear()  # Clear S3 data cache
        # Clear the DataFrame in session state to ensure it's reloaded
        st.session_state.df_display_data = pd.DataFrame(
            columns=["URL", "Last Scraped", "S3 Key"]
        )
        st.rerun()

    def run_scraper_and_refresh():
        """Executes the scraping pipeline and then refreshes the dashboard."""
        st.info("Initiating web scraping and S3 upload. This may take some time...")
        # Run the scraping pipeline from datapipeline.py
        with st.spinner(text="Scraping and uploading to S3..."):
            run_scrape_and_upload_pipeline()
        st.success("Scraping and upload complete! Refreshing dashboard...")
        refresh_dashboard_data()

    def run_single_url_scraper(target_url):
        """Executes scraping for a single URL and then refreshes the dashboard."""
        if not target_url:
            st.warning("Please enter a URL to scrape.")
            return

        st.info(f"Initiating scraping for: {target_url}")
        with st.spinner(text=f"Scraping {target_url}..."):
            scrape_and_upload_link(target_url)  # Call the single URL scrape function
        st.success(
            f"Scraping and upload for {target_url} complete! Refreshing dashboard..."
        )
        refresh_dashboard_data()

    # Top Controls: Refresh button
    if st.button(
        "🔄 Refresh Data from S3",
        key="refresh_button_top",
        help="Fetches the latest data from S3.",
    ):
        refresh_dashboard_data()

    st.markdown("---")
    st.subheader("📄 Scraped Links and Timestamps when they were scrapped")

    # Load or Reload Data
    # Load data if session state DataFrame is empty (first run or after clearing for refresh)
    if st.session_state.df_display_data.empty:
        st.write("Fetching scraped data from S3 bucket...")
        raw_data_list = get_scraped_data_from_s3(S3_BUCKET_NAME, S3_FOLDER_PREFIX)

        if raw_data_list is None:  # Critical error fetching data
            st.error(
                "Failed to load data from S3. Please check credentials and bucket configuration."
            )
            st.stop()  # halt execution
        elif not raw_data_list:
            st.info("No scraped data found in the specified S3 location.")
            st.session_state.df_display_data = pd.DataFrame(
                columns=["URL", "Last Scraped", "S3 Key"]
            )
        else:
            df = pd.DataFrame(raw_data_list)
            df["Last Scraped"] = pd.to_datetime(df["Last Scraped"])
            # Arrange the dataframe in descending order of time
            st.session_state.df_display_data = df.sort_values(
                by="Last Scraped", ascending=False
            )

    # Display the DataFrame
    if not st.session_state.df_display_data.empty:
        st.dataframe(
            st.session_state.df_display_data,
            column_config={
                "URL": st.column_config.LinkColumn(
                    "Source URL",
                    help="The original URL that was scraped.",
                ),
                "Last Scraped": st.column_config.DatetimeColumn(
                    "Last Scraped Date",
                    help="The date and time when this URL was last scraped.",
                    format="YYYY-MM-DD HH:mm:ss",
                ),
                "S3 Key": st.column_config.TextColumn(
                    "S3 Object Key",
                    help="The path to the object in the S3 bucket.",
                    width="medium",
                ),
            },
            use_container_width=True,
            hide_index=True,
        )
        st.success(
            f"Displaying {len(st.session_state.df_display_data)} entries. Click on column headers to sort."
        )
    else:
        if raw_data_list is not None:  # Incorrect metadata or no data
            st.info(
                "No data to display. Ensure files with 'sourceurl' and 'scrapeddatetime' metadata exist in S3."
            )

    st.markdown("---")

    # Section for individual URL scraping
    st.subheader("📥 Scrape a Specific URL")

    # URL text input
    single_url = st.text_input(
        "Enter URL to scrape:",
        placeholder="e.g., https://docs.unity.rc.umass.edu/documentation/some-page",
        key="single_url_text_input",
    )

    #  Button to run the scrapping pipeline for the given url
    if st.button(
        "📥 Scrape This URL",
        key="run_single_scraper_button",
        help="Scrapes the entered URL and uploads its content to S3.",
    ):
        run_single_url_scraper(single_url)

    st.markdown("---")

    # Button to run the scraping pipeline for all websites
    if st.button(
        "🚀 Scrape All Websites",
        key="run_scraper_button",
        help="Runs the scraping pipeline defined in datapipeline.py and uploads to S3.",
    ):
        run_scraper_and_refresh()

    st.caption("Dashboard displays data using S3 metadata")

with tab3:
    st.header("💬 Slack Conversations")

    @st.cache_data(ttl=3600)
    def get_slack_conversations_from_s3():
        """Get slack conversations markdown from S3"""
        try:
            s3 = boto3.client("s3")
            s3_key = "slack_conversations/slack_conversations.md"

            # Get object metadata
            head_response = s3.head_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
            metadata = head_response.get("Metadata", {})

            # Get object content
            response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
            content = response["Body"].read().decode("utf-8")

            return {
                "content": content,
                "scraped_datetime": metadata.get("scrapeddatetime", "Unknown"),
                "conversation_count": metadata.get("conversationcount", "Unknown"),
                "channel_id": metadata.get("channelid", "Unknown"),
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return None
            else:
                st.error(f"Error accessing Slack conversations: {e}")
                return None
        except Exception as e:
            st.error(f"Unexpected error: {e}")
            return None

    def run_slack_scraper_and_refresh(start_date=None):
        """Run the Slack scraper and refresh the dashboard"""
        st.info(
            f"Scraping Slack channel conversations from {start_date or 'beginning'}..."
        )
        with st.spinner("Scraping conversations from Slack..."):
            slack_scraper_main(start_date)
        st.success("Slack scraping complete! Refreshing dashboard...")
        st.cache_data.clear()
        st.rerun()

    # Control buttons and date picker
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        if st.button("🔄 Refresh Slack Conversations", key="refresh_slack"):
            st.cache_data.clear()
            st.rerun()
    with col2:
        start_date = st.date_input("Start Date", key="slack_start_date")
    with col3:
        st.write("")  # Add vertical space to align with date input
        st.write("")  # Add more vertical space if needed
        if st.button("📥 Scrape Slack Channel", key="scrape_slack"):
            run_slack_scraper_and_refresh(start_date.strftime("%Y-%m-%d"))

    def save_edited_markdown_to_s3(edited_content, original_metadata):
        """Save edited markdown content back to S3"""
        try:
            s3 = boto3.client("s3")
            s3_key = "slack_conversations/slack_conversations.md"

            # Update metadata with edit timestamp
            updated_metadata = original_metadata.copy()
            updated_metadata["LastEdited"] = datetime.datetime.now().isoformat()

            s3.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_key,
                Body=edited_content,
                ContentType="text/markdown",
                Metadata=updated_metadata,
            )
            return True
        except Exception as e:
            st.error(f"Error saving to S3: {e}")
            return False

    # Get and display Slack conversations
    slack_data = get_slack_conversations_from_s3()

    if slack_data:
        # Display metadata
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Conversations", slack_data["conversation_count"])
        with col2:
            scraped_time = slack_data["scraped_datetime"]
            if scraped_time != "Unknown":
                try:
                    dt = datetime.datetime.fromisoformat(scraped_time)
                    scraped_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    st.error(f"Error parsing scraped datetime: {e}")
                    pass
            st.metric("Last Scraped", scraped_time)

        st.markdown("---")

        # Editable text area for markdown content
        edited_content = st.text_area(
            "Edit Slack Conversations (Markdown):",
            value=slack_data["content"],
            height=400,
            key="slack_markdown_editor",
        )

        # Save button
        if st.button("💾 Save Changes to S3", key="save_slack_changes"):
            original_metadata = {
                "scrapeddatetime": slack_data["scraped_datetime"],
                "channelid": slack_data["channel_id"],
                "conversationcount": slack_data["conversation_count"],
            }

            if save_edited_markdown_to_s3(edited_content, original_metadata):
                st.success("Changes saved successfully to S3!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Failed to save changes.")

        st.markdown("---")
        st.subheader("Preview:")
        st.markdown(edited_content)

    else:
        st.info(
            "No Slack conversations found. Run the slack scraper to generate conversations data."
        )
        st.code("python slack_scraper.py", language="bash")

    def check_slack_conversations_exists():
        """Check if slack_conversations.md exists in S3"""
        try:
            s3 = boto3.client("s3")
            s3.head_object(
                Bucket=S3_BUCKET_NAME, Key="slack_conversations/slack_conversations.md"
            )
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            else:
                st.error(f"Error checking for slack_conversations.md: {e}")
                return False
        except Exception as e:
            st.error(f"Error checking for slack_conversations.md: {e}")
            return False


with tab4:
    st.header("📋 Q&A Pair Review")

    # Initialize session state for Q&A review
    if "current_qa_file" not in st.session_state:
        st.session_state.current_qa_file = None
    if "current_qa_index" not in st.session_state:
        st.session_state.current_qa_index = 0
    if "qa_pairs" not in st.session_state:
        st.session_state.qa_pairs = []
    if "approved_qa_pairs" not in st.session_state:
        st.session_state.approved_qa_pairs = []

    def get_qa_files():
        """Get all Q&A JSON files from S3 slack_conversations folder"""
        try:
            s3 = boto3.client("s3")
            response = s3.list_objects_v2(
                Bucket=S3_BUCKET_NAME, Prefix="slack_conversations/slack_qa_pairs_"
            )

            qa_files = []
            if "Contents" in response:
                for obj in response["Contents"]:
                    if obj["Key"].endswith(".json") and "slack_qa_pairs_" in obj["Key"]:
                        qa_files.append(obj["Key"])

            return sorted(qa_files, reverse=True)  # Most recent first
        except Exception as e:
            st.error(f"Error accessing S3 Q&A files: {e}")
            return []

    def load_qa_file(file_path):
        """Load Q&A pairs from S3 JSON file"""
        try:
            s3 = boto3.client("s3")
            response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=file_path)
            content = response["Body"].read().decode("utf-8")
            data = json.loads(content)
            return data if isinstance(data, list) else data.get("qa_pairs", [])
        except Exception as e:
            st.error(f"Error loading Q&A file from S3: {e}")
            return []

    def save_qa_file(file_path, qa_pairs):
        """Save Q&A pairs to S3 JSON file"""
        try:
            s3 = boto3.client("s3")
            content = json.dumps(qa_pairs, indent=2, ensure_ascii=False)

            s3.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=file_path,
                Body=content,
                ContentType="application/json",
            )
            return True
        except Exception as e:
            st.error(f"Error saving Q&A file to S3: {e}")
            return False

    def load_approved_qa_pairs():
        """Load approved Q&A pairs from S3"""
        approved_key = "slack_conversations/approved_qa_pairs.json"
        try:
            s3 = boto3.client("s3")
            response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=approved_key)
            content = response["Body"].read().decode("utf-8")
            data = json.loads(content)
            return data.get("qa_pairs", []) if isinstance(data, dict) else data
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return []  # File doesn't exist yet
            else:
                st.error(f"Error loading approved Q&A pairs from S3: {e}")
                return []
        except Exception as e:
            st.error(f"Error loading approved Q&A pairs: {e}")
            return []

    def save_approved_qa_pairs(approved_pairs):
        """Save approved Q&A pairs to S3"""
        approved_key = "slack_conversations/approved_qa_pairs.json"
        try:
            s3 = boto3.client("s3")

            # Create metadata structure
            data = {
                "generated_at": datetime.datetime.now().isoformat(),
                "total_pairs": len(approved_pairs),
                "qa_pairs": approved_pairs,
            }

            content = json.dumps(data, indent=2, ensure_ascii=False)

            # Add metadata to S3 object
            metadata = {
                "generated_at": datetime.datetime.now().isoformat(),
                "total_pairs": str(len(approved_pairs)),
                "content_type": "approved_qa_pairs",
            }

            s3.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=approved_key,
                Body=content,
                ContentType="application/json",
                Metadata=metadata,
            )
            return True
        except Exception as e:
            st.error(f"Error saving approved Q&A pairs to S3: {e}")
            return False

    def remove_current_qa_pair():
        """Remove current Q&A pair from the source file"""
        if (
            st.session_state.current_qa_file
            and 0 <= st.session_state.current_qa_index < len(st.session_state.qa_pairs)
        ):
            # Remove the current pair
            st.session_state.qa_pairs.pop(st.session_state.current_qa_index)

            # Save updated file
            if save_qa_file(
                st.session_state.current_qa_file, st.session_state.qa_pairs
            ):
                # Adjust index if necessary
                if st.session_state.current_qa_index >= len(st.session_state.qa_pairs):
                    st.session_state.current_qa_index = max(
                        0, len(st.session_state.qa_pairs) - 1
                    )
                return True
        return False

    def approve_qa_pair(qa_pair):
        """Add Q&A pair to approved list"""
        # Load current approved pairs
        approved_pairs = load_approved_qa_pairs()

        # Add timestamp to the Q&A pair
        qa_pair_with_metadata = qa_pair.copy()
        qa_pair_with_metadata["approved_at"] = datetime.datetime.now().isoformat()
        qa_pair_with_metadata["source_file"] = st.session_state.current_qa_file
        qa_pair_with_metadata["original_index"] = st.session_state.current_qa_index

        # Add to approved list
        approved_pairs.append(qa_pair_with_metadata)

        # Save approved pairs
        if save_approved_qa_pairs(approved_pairs):
            # Remove from source file
            return remove_current_qa_pair()
        return False

    def run_qa_generator_and_upload():
        """Run the Q&A generator using Slack conversations from S3"""
        # First check if slack_conversations.md exists in S3
        if not check_slack_conversations_exists():
            st.error(
                "❌ Could not find `slack_conversations/slack_conversations.md` in S3. Please upload the Slack conversations file first."
            )
            return

        st.info("Generating Q&A pairs from Slack conversations in S3...")
        with st.spinner("Processing conversations and uploading to S3..."):
            try:
                # Import and run the Q&A generator with S3 input
                import sys

                sys.path.append(os.path.join(os.getcwd(), "qa_pairs"))

                # Run Q&A generator with S3 input (this will save directly to S3)
                success = slack_qa_main()

                if success:
                    st.success("✅ Q&A pairs generated and uploaded to S3!")
                else:
                    st.warning(
                        "⚠️ Q&A generation completed but no pairs were generated or saved."
                    )

            except Exception as e:
                st.error(f"❌ Error running Q&A generator: {e}")
                import traceback

                st.error(f"Details: {traceback.format_exc()}")

        # Refresh the dashboard
        st.cache_data.clear()
        st.rerun()

    # File selection
    qa_files = get_qa_files()

    # Check if source file exists
    slack_file_exists = check_slack_conversations_exists()

    # Control buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh Q&A Files", key="refresh_qa"):
            st.cache_data.clear()
            st.rerun()
    with col2:
        button_disabled = not slack_file_exists
        button_text = (
            "🤖 Generate Q&A Pairs from S3"
            if slack_file_exists
            else "🚫 No Slack File in S3"
        )
        if st.button(button_text, key="generate_qa", disabled=button_disabled):
            run_qa_generator_and_upload()

    # Status indicator
    if slack_file_exists:
        st.success("✅ `slack_conversations/slack_conversations.md` found in S3")
    else:
        st.warning("⚠️ `slack_conversations/slack_conversations.md` not found in S3")

    if not qa_files:
        st.info(
            "No Q&A Pairs files found in S3 slack_conversations folder. Click 'Generate Q&A Pairs from S3' to create them."
        )
    else:
        # File selector
        selected_file = st.selectbox(
            "Select Q&A file to review:", qa_files, key="qa_file_selector"
        )

        # Load file if changed or first time
        if selected_file != st.session_state.current_qa_file:
            st.session_state.current_qa_file = selected_file
            st.session_state.qa_pairs = load_qa_file(selected_file)
            st.session_state.current_qa_index = 0

        if st.session_state.qa_pairs:
            # Check if this file has original conversations
            has_original_conversations = False
            if st.session_state.qa_pairs:
                has_original_conversations = any(
                    "original_conversation" in pair
                    for pair in st.session_state.qa_pairs
                )

            # Display file info
            if has_original_conversations:
                st.success(
                    "✅ This file includes original Slack conversations for review"
                )
            else:
                st.info(
                    "ℹ️ This file was generated before conversation tracking was implemented"
                )

            # Display progress
            total_pairs = len(st.session_state.qa_pairs)
            current_index = st.session_state.current_qa_index

            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.progress((current_index + 1) / total_pairs)
                st.caption(f"Reviewing pair {current_index + 1} of {total_pairs}")
            with col2:
                # Navigation buttons
                if st.button("⬅️ Previous", disabled=(current_index == 0)):
                    st.session_state.current_qa_index = max(0, current_index - 1)
                    st.rerun()
            with col3:
                if st.button("➡️ Next", disabled=(current_index >= total_pairs - 1)):
                    st.session_state.current_qa_index = min(
                        total_pairs - 1, current_index + 1
                    )
                    st.rerun()
            with col4:
                # Jump to specific index
                jump_to_index = st.number_input(
                    "Jump to:",
                    min_value=1,
                    max_value=total_pairs,
                    value=current_index + 1,
                    step=1,
                    key=f"jump_to_{current_index}",
                    help="Enter a pair number to jump directly to it",
                )
                if st.button("🎯 Go", key=f"jump_button_{current_index}"):
                    st.session_state.current_qa_index = jump_to_index - 1
                    st.rerun()

            st.markdown("---")

            # Display current Q&A pair
            if current_index < len(st.session_state.qa_pairs):
                current_pair = st.session_state.qa_pairs[current_index]

                st.subheader("📝 Current Q&A Pair")

                # Editable question
                edited_question = st.text_area(
                    "Question:",
                    value=current_pair.get("question", ""),
                    height=100,
                    key=f"question_edit_{current_index}",
                )

                # Editable answers
                st.write("**Answers:**")
                answers = current_pair.get("answers", [])
                edited_answers = []

                for i, answer in enumerate(answers):
                    edited_answer = st.text_area(
                        f"Answer {i + 1}:",
                        value=answer,
                        height=80,
                        key=f"answer_edit_{current_index}_{i}",
                    )
                    edited_answers.append(edited_answer)

                # Button to add new answer
                if st.button("➕ Add Answer", key=f"add_answer_{current_index}"):
                    edited_answers.append("")
                    # Update the Q&A pair with new empty answer
                    updated_pair = {
                        "question": edited_question,
                        "answers": edited_answers,
                    }
                    # Preserve original conversation if it exists
                    if "original_conversation" in current_pair:
                        updated_pair["original_conversation"] = current_pair[
                            "original_conversation"
                        ]
                    if "conversation_index" in current_pair:
                        updated_pair["conversation_index"] = current_pair[
                            "conversation_index"
                        ]
                    if "total_conversations" in current_pair:
                        updated_pair["total_conversations"] = current_pair[
                            "total_conversations"
                        ]
                    if "generated_at" in current_pair:
                        updated_pair["generated_at"] = current_pair["generated_at"]

                    st.session_state.qa_pairs[current_index] = updated_pair
                    save_qa_file(
                        st.session_state.current_qa_file, st.session_state.qa_pairs
                    )
                    st.rerun()

                # Original Conversation Expandable Section
                original_conversation = current_pair.get("original_conversation")
                if original_conversation:
                    with st.expander(
                        "📜 View Original Slack Conversation", expanded=False
                    ):
                        st.markdown("**Original Conversation Thread:**")

                        # Add metadata if available
                        conversation_metadata = []
                        if "conversation_index" in current_pair:
                            conversation_metadata.append(
                                f"Conversation #{current_pair['conversation_index']}"
                            )
                        if "total_conversations" in current_pair:
                            conversation_metadata.append(
                                f"of {current_pair['total_conversations']} total"
                            )
                        if "generated_at" in current_pair:
                            conversation_metadata.append(
                                f"Generated: {current_pair['generated_at'][:19].replace('T', ' ')}"
                            )

                        if conversation_metadata:
                            st.caption(" • ".join(conversation_metadata))

                        # Display the conversation in a code block for better formatting
                        st.text_area(
                            "Conversation Content:",
                            value=original_conversation,
                            height=300,
                            key=f"original_conversation_{current_index}",
                            disabled=True,
                            help="This is the original Slack conversation thread that was used to generate this Q&A pair",
                        )
                else:
                    st.info(
                        "ℹ️ Original conversation not available for this Q&A pair (generated before conversation tracking was implemented)"
                    )

                st.markdown("---")

                # Action buttons
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    if st.button(
                        "✅ Approve", key=f"approve_{current_index}", type="primary"
                    ):
                        # Update the current pair with edits
                        updated_pair = {
                            "question": edited_question,
                            "answers": [
                                ans for ans in edited_answers if ans.strip()
                            ],  # Remove empty answers
                        }

                        # Preserve original conversation and metadata
                        for key in [
                            "original_conversation",
                            "conversation_index",
                            "total_conversations",
                            "generated_at",
                        ]:
                            if key in current_pair:
                                updated_pair[key] = current_pair[key]

                        if updated_pair["question"].strip() and updated_pair["answers"]:
                            if approve_qa_pair(updated_pair):
                                st.success("Q&A pair approved and added to database!")
                                st.rerun()
                            else:
                                st.error("Failed to approve Q&A pair")
                        else:
                            st.warning("Question and at least one answer are required")

                with col2:
                    if st.button("❌ Reject", key=f"reject_{current_index}"):
                        if remove_current_qa_pair():
                            st.success("Q&A pair rejected and removed!")
                            st.rerun()
                        else:
                            st.error("Failed to reject Q&A pair")

                with col3:
                    if st.button("💾 Save Edits", key=f"save_{current_index}"):
                        # Update the current pair with edits
                        updated_pair = {
                            "question": edited_question,
                            "answers": [
                                ans for ans in edited_answers if ans.strip()
                            ],  # Remove empty answers
                        }

                        # Preserve original conversation and metadata
                        for key in [
                            "original_conversation",
                            "conversation_index",
                            "total_conversations",
                            "generated_at",
                        ]:
                            if key in current_pair:
                                updated_pair[key] = current_pair[key]

                        if updated_pair["question"].strip() and updated_pair["answers"]:
                            st.session_state.qa_pairs[current_index] = updated_pair
                            if save_qa_file(
                                st.session_state.current_qa_file,
                                st.session_state.qa_pairs,
                            ):
                                st.success("Changes saved!")
                            else:
                                st.error("Failed to save changes")
                        else:
                            st.warning("Question and at least one answer are required")

                with col4:
                    if st.button("⏭️ Skip", key=f"skip_{current_index}"):
                        if current_index < total_pairs - 1:
                            st.session_state.current_qa_index += 1
                            st.rerun()
                        else:
                            st.info("No more pairs to review")

                st.markdown("---")

                # Statistics
                approved_pairs = load_approved_qa_pairs()
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Remaining to Review", total_pairs)
                with col2:
                    st.metric("Approved Pairs", len(approved_pairs))
                with col3:
                    if total_pairs > 0:
                        completion_rate = (
                            (len(approved_pairs)) / (len(approved_pairs) + total_pairs)
                        ) * 100
                        st.metric("Completion Rate", f"{completion_rate:.1f}%")

            else:
                st.success("🎉 All Q&A pairs in this file have been reviewed!")

                # Show option to load another file
                remaining_files = [
                    f for f in qa_files if f != st.session_state.current_qa_file
                ]
                if remaining_files:
                    st.info("Select another file to continue reviewing.")
                else:
                    st.info("All Q&A files have been processed!")

        else:
            st.warning("No Q&A pairs found in the selected file.")

    st.markdown("---")

    # Display approved pairs management
    st.subheader("📊 Approved Q&A Pairs Management")
    approved_pairs = load_approved_qa_pairs()
    if approved_pairs:
        st.write(f"**Total Approved Pairs:** {len(approved_pairs)}")

        # Initialize session state for approved pairs navigation
        if "current_approved_index" not in st.session_state:
            st.session_state.current_approved_index = 0

        # Ensure index is within bounds
        if st.session_state.current_approved_index >= len(approved_pairs):
            st.session_state.current_approved_index = max(0, len(approved_pairs) - 1)

        # Control buttons and navigation
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 2])

        with col1:
            if st.button("🔄 Refresh", key="refresh_approved"):
                st.cache_data.clear()
                st.rerun()

        with col2:
            # Previous button
            if st.button(
                "⬅️ Previous",
                disabled=(st.session_state.current_approved_index == 0),
                key="prev_approved",
            ):
                st.session_state.current_approved_index = max(
                    0, st.session_state.current_approved_index - 1
                )
                st.rerun()

        with col3:
            # Next button
            if st.button(
                "➡️ Next",
                disabled=(
                    st.session_state.current_approved_index >= len(approved_pairs) - 1
                ),
                key="next_approved",
            ):
                st.session_state.current_approved_index = min(
                    len(approved_pairs) - 1, st.session_state.current_approved_index + 1
                )
                st.rerun()

        with col4:
            # Jump to specific index
            jump_to_index = st.number_input(
                "Jump to:",
                min_value=1,
                max_value=len(approved_pairs),
                value=st.session_state.current_approved_index + 1,
                step=1,
                key="jump_to_approved",
                help="Enter a pair number to jump directly to it",
            )

        with col5:
            if st.button("🎯 Go", key="jump_button_approved"):
                st.session_state.current_approved_index = jump_to_index - 1
                st.rerun()

        # Search functionality
        search_approved = st.text_input(
            "🔍 Search approved pairs:",
            placeholder="Search by question or answer...",
            key="search_approved_pairs",
        )

        # Filter approved pairs based on search
        filtered_pairs = approved_pairs
        if search_approved:
            search_lower = search_approved.lower()
            filtered_pairs = [
                pair
                for pair in approved_pairs
                if (
                    search_lower in pair.get("question", "").lower()
                    or search_lower in str(pair.get("answers", [])).lower()
                    or search_lower in pair.get("answer", "").lower()
                )
            ]

        st.markdown("---")

        # Display current pair or search results
        if search_approved:
            # Show search results
            if filtered_pairs:
                st.write(f"**Search Results: {len(filtered_pairs)} pairs found**")

                for i, pair in enumerate(filtered_pairs):
                    # Find original index in the full list
                    original_index = approved_pairs.index(pair)
                    approved_at = pair.get("approved_at", "Unknown")
                    source_file = pair.get("source_file", "Unknown")

                    # Format approval date
                    try:
                        dt = datetime.datetime.fromisoformat(approved_at)
                        approved_at_formatted = dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        approved_at_formatted = approved_at

                    # Create container for each search result
                    with st.container():
                        st.markdown(
                            f"**#{original_index + 1} - {pair.get('question', 'No question')[:80]}...** *(Approved: {approved_at_formatted})*"
                        )

                        col1, col2 = st.columns([4, 1])

                        with col1:
                            st.write("**Question:**")
                            st.write(pair.get("question", "No question available"))

                            # Handle both single answer and multiple answers format
                            if "answers" in pair and isinstance(pair["answers"], list):
                                st.write("**Answers:**")
                                for j, answer in enumerate(pair["answers"]):
                                    st.write(f"{j + 1}. {answer}")
                            elif "answer" in pair:
                                st.write("**Answer:**")
                                st.write(pair.get("answer", "No answer available"))
                            else:
                                st.write("**Answer:** No answer available")

                        with col2:
                            st.write("**Metadata:**")
                            st.write(f"Index: #{original_index + 1}")
                            st.write(f"Approved: {approved_at_formatted}")
                            if source_file != "Unknown":
                                st.write(f"Source: {source_file.split('/')[-1]}")

                            # Delete button for approved pairs (single click)
                            if st.button(
                                "🗑️ Delete",
                                key=f"delete_approved_search_{original_index}",
                                help="Delete this approved Q&A pair",
                            ):
                                # Remove the pair from approved list
                                updated_approved = [
                                    p
                                    for j, p in enumerate(approved_pairs)
                                    if j != original_index
                                ]

                                # Save updated approved pairs
                                if save_approved_qa_pairs(updated_approved):
                                    st.success(
                                        "✅ Approved Q&A pair deleted successfully!"
                                    )
                                    st.cache_data.clear()
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to delete approved Q&A pair.")

                        # Add separator between pairs (except for the last one)
                        if i < len(filtered_pairs) - 1:
                            st.markdown("---")
            else:
                st.info("No approved pairs match your search criteria.")
        else:
            # Show single pair navigation
            if approved_pairs:
                current_index = st.session_state.current_approved_index
                pair = approved_pairs[current_index]
                approved_at = pair.get("approved_at", "Unknown")
                source_file = pair.get("source_file", "Unknown")

                # Progress indicator
                st.progress((current_index + 1) / len(approved_pairs))
                st.caption(f"Viewing pair {current_index + 1} of {len(approved_pairs)}")

                # Format approval date
                try:
                    dt = datetime.datetime.fromisoformat(approved_at)
                    approved_at_formatted = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    approved_at_formatted = approved_at

                # Create container for current pair
                with st.container():
                    st.markdown(
                        f"**#{current_index + 1} - {pair.get('question', 'No question')[:80]}...** *(Approved: {approved_at_formatted})*"
                    )

                    col1, col2 = st.columns([4, 1])

                    with col1:
                        st.write("**Question:**")
                        st.write(pair.get("question", "No question available"))

                        # Handle both single answer and multiple answers format
                        if "answers" in pair and isinstance(pair["answers"], list):
                            st.write("**Answers:**")
                            for j, answer in enumerate(pair["answers"]):
                                st.write(f"{j + 1}. {answer}")
                        elif "answer" in pair:
                            st.write("**Answer:**")
                            st.write(pair.get("answer", "No answer available"))
                        else:
                            st.write("**Answer:** No answer available")

                    with col2:
                        st.write("**Metadata:**")
                        st.write(f"Index: #{current_index + 1}")
                        st.write(f"Approved: {approved_at_formatted}")
                        if source_file != "Unknown":
                            st.write(f"Source: {source_file.split('/')[-1]}")

                        # Delete button for approved pairs (single click)
                        if st.button(
                            "🗑️ Delete",
                            key=f"delete_approved_{current_index}",
                            help="Delete this approved Q&A pair",
                        ):
                            # Remove the pair from approved list
                            updated_approved = [
                                p
                                for j, p in enumerate(approved_pairs)
                                if j != current_index
                            ]

                            # Save updated approved pairs
                            if save_approved_qa_pairs(updated_approved):
                                st.success("✅ Approved Q&A pair deleted successfully!")
                                # Adjust index if necessary
                                if st.session_state.current_approved_index >= len(
                                    updated_approved
                                ):
                                    st.session_state.current_approved_index = max(
                                        0, len(updated_approved) - 1
                                    )
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error("❌ Failed to delete approved Q&A pair.")
            else:
                st.info("No approved pairs to display.")
    else:
        st.info(
            "No approved Q&A pairs yet. Approve some pairs from the review section above to see them here."
        )

with tab5:
    st.header("📚 Add Knowledge")

    # Initialize session state for knowledge input
    if "knowledge_entries" not in st.session_state:
        st.session_state.knowledge_entries = []

    def load_knowledge_from_s3():
        """Load knowledge entries from S3 JSON file"""
        try:
            s3 = boto3.client("s3")
            s3_key = "manual_knowledge/knowledge_input.json"

            response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
            content = response["Body"].read().decode("utf-8")
            data = json.loads(content)

            # Return the entries or empty list if structure is different
            if isinstance(data, dict):
                return data.get("entries", [])
            elif isinstance(data, list):
                return data
            else:
                return []

        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return []  # File doesn't exist yet
            else:
                st.error(f"Error loading knowledge from S3: {e}")
                return []
        except Exception as e:
            st.error(f"Error loading knowledge: {e}")
            return []

    def save_knowledge_to_s3(entries):
        """Save knowledge entries to S3 JSON file"""
        try:
            s3 = boto3.client("s3")
            s3_key = "manual_knowledge/knowledge_input.json"

            # Create structured data with metadata
            data = {
                "metadata": {
                    "created_at": datetime.datetime.now().isoformat(),
                    "total_entries": len(entries),
                    "last_updated": datetime.datetime.now().isoformat(),
                },
                "entries": entries,
            }

            content = json.dumps(data, indent=2, ensure_ascii=False)

            # Add S3 metadata
            metadata = {
                "content_type": "manual_knowledge",
                "total_entries": str(len(entries)),
                "last_updated": datetime.datetime.now().isoformat(),
            }

            s3.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_key,
                Body=content,
                ContentType="application/json",
                Metadata=metadata,
            )
            return True
        except Exception as e:
            st.error(f"Error saving knowledge to S3: {e}")
            return False

    def add_knowledge_entry(entry_type, title, content, question=None, answer=None):
        """Add a new knowledge entry"""
        new_entry = {
            "type": entry_type,
            "title": title,
            "created_at": datetime.datetime.now().isoformat(),
        }

        if entry_type == "qa_pair":
            new_entry["question"] = question
            new_entry["answer"] = answer
        else:  # knowledge_input
            new_entry["content"] = content

        return new_entry

    # Load existing knowledge entries on first load
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_cached_knowledge_entries():
        return load_knowledge_from_s3()

    # Control buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh Knowledge Entries", key="refresh_knowledge"):
            st.cache_data.clear()
            st.rerun()
    with col2:
        st.metric("Total Entries", len(get_cached_knowledge_entries()))

    st.markdown("---")

    # Knowledge input form
    st.subheader("✍️ Add New Knowledge")

    # Type selection
    entry_type = st.radio(
        "Select knowledge type:",
        ["Q&A Pair", "Knowledge Input"],
        key="knowledge_type",
        help="Choose whether to add a question-answer pair or general knowledge content",
    )

    with st.form("knowledge_form", clear_on_submit=True):
        # Common fields
        title = st.text_input(
            "Title/Summary:",
            placeholder="Brief title or summary of this knowledge entry",
            help="A short descriptive title for this knowledge entry",
        )

        if entry_type == "Q&A Pair":
            question = st.text_area(
                "Question:",
                placeholder="Enter the question about Unity...",
                height=80,
                help="The question that users might ask",
            )
            answer = st.text_area(
                "Answer:",
                placeholder="Enter the answer or explanation...",
                height=120,
                help="The detailed answer or explanation",
            )
            content = None
        else:  # Knowledge Input
            content = st.text_area(
                "Knowledge Content:",
                placeholder="Enter general knowledge, documentation, or information about Unity...",
                height=150,
                help="General knowledge content, documentation, or information",
            )
            question = None
            answer = None

        # Submit button
        submitted = st.form_submit_button("💾 Save Knowledge Entry", type="primary")

        if submitted:
            # Validation
            if not title.strip():
                st.error("Title is required!")
            elif entry_type == "Q&A Pair" and (
                not question.strip() or not answer.strip()
            ):
                st.error("Both question and answer are required for Q&A pairs!")
            elif entry_type == "Knowledge Input" and not content.strip():
                st.error("Knowledge content is required!")
            else:
                # Load current entries
                current_entries = load_knowledge_from_s3()

                # Create new entry
                new_entry = add_knowledge_entry(
                    entry_type.lower().replace(" ", "_"),
                    title.strip(),
                    content.strip() if content else None,
                    question.strip() if question else None,
                    answer.strip() if answer else None,
                )

                # Add to list
                current_entries.append(new_entry)

                # Save to S3
                if save_knowledge_to_s3(current_entries):
                    st.success(f"✅ {entry_type} saved successfully!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("❌ Failed to save knowledge entry.")

    st.markdown("---")

    # Display existing knowledge entries
    st.subheader("📖 Existing Knowledge Entries")

    knowledge_entries = get_cached_knowledge_entries()

    if not knowledge_entries:
        st.info("No knowledge entries found. Add your first entry above!")
    else:
        # Filter and search options
        col1, col2 = st.columns([2, 1])
        with col1:
            search_term = st.text_input(
                "🔍 Search knowledge base:",
                placeholder="Search by title, question, or content...",
                key="knowledge_search",
            )
        with col2:
            filter_type = st.selectbox(
                "Filter by type:",
                ["All", "Q&A Pair", "Knowledge Input"],
                key="knowledge_filter",
            )

        # Filter entries based on search and type
        filtered_entries = knowledge_entries

        if search_term:
            search_lower = search_term.lower()
            filtered_entries = [
                entry
                for entry in filtered_entries
                if (
                    search_lower in entry.get("title", "").lower()
                    or search_lower in entry.get("question", "").lower()
                    or search_lower in entry.get("answer", "").lower()
                    or search_lower in entry.get("content", "").lower()
                )
            ]

        if filter_type != "All":
            filter_type_key = filter_type.lower().replace(" ", "_")
            filtered_entries = [
                entry
                for entry in filtered_entries
                if entry.get("type") == filter_type_key
            ]

        # Sort by creation date (newest first)
        filtered_entries.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        st.write(f"Showing {len(filtered_entries)} of {len(knowledge_entries)} entries")

        # Display entries in a container format
        for i, entry in enumerate(filtered_entries):
            entry_type_display = entry.get("type", "unknown").replace("_", " ").title()
            created_at = entry.get("created_at", "Unknown")

            # Format creation date
            try:
                dt = datetime.datetime.fromisoformat(created_at)
                created_at_formatted = dt.strftime("%Y-%m-%d %H:%M")
            except:
                created_at_formatted = created_at

            # Create container for each knowledge entry
            with st.container():
                st.markdown(
                    f"**#{i + 1} - {entry.get('title', 'Untitled')}** *({entry_type_display}) - {created_at_formatted}*"
                )

                col1, col2 = st.columns([3, 1])

                with col1:
                    if entry.get("type") == "qa_pair":
                        st.write("**Question:**")
                        st.write(entry.get("question", ""))
                        st.write("**Answer:**")
                        st.write(entry.get("answer", ""))
                    else:  # knowledge_input
                        st.write("**Content:**")
                        st.write(entry.get("content", ""))

                with col2:
                    st.write("**Metadata:**")
                    st.write(f"Index: #{i + 1}")
                    st.write(f"Type: {entry_type_display}")
                    st.write(f"Created: {created_at_formatted}")

                    # Delete button
                    if st.button(
                        "🗑️ Delete",
                        key=f"delete_knowledge_{i}",
                        help="Delete this knowledge entry",
                    ):
                        # Remove entry from list
                        updated_entries = [
                            e for j, e in enumerate(knowledge_entries) if j != i
                        ]

                        # Save updated list
                        if save_knowledge_to_s3(updated_entries):
                            st.success("✅ Entry deleted successfully!")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete entry.")

                # Add separator between entries (except for the last one)
                if i < len(filtered_entries) - 1:
                    st.markdown("---")

        # Statistics summary
        if knowledge_entries:
            st.markdown("---")
            col1, col2, col3 = st.columns(3)

            qa_count = len([e for e in knowledge_entries if e.get("type") == "qa_pair"])
            knowledge_count = len(
                [e for e in knowledge_entries if e.get("type") == "knowledge_input"]
            )

            with col1:
                st.metric("Total Entries", len(knowledge_entries))
            with col2:
                st.metric("Q&A Pairs", qa_count)
            with col3:
                st.metric("Knowledge Inputs", knowledge_count)
