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
from utils.qa_pair_tab import display_qa_pair_review_tab
from utils.streamlit_components import confirm_action, trigger_confirmation
from slack_scripts.slack_scraper import main as slack_scraper_main

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
        if single_url.strip():
            trigger_confirmation("scrape_single_url")
        else:
            st.warning("Please enter a URL to scrape.")

    # Handle confirmation for single URL scraping
    if confirm_action(
        "scrape_single_url",
        f"scrape the URL: {single_url}",
        action_description=f"This will scrape the content from {single_url} and upload it to S3.",
        warning_message="This action will consume API resources and may take some time to complete.",
        danger_level="info",
    ):
        run_single_url_scraper(single_url)

    st.markdown("---")

    # Button to run the scraping pipeline for all websites
    if st.button(
        "🚀 Scrape All Websites",
        key="run_scraper_button",
        help="Runs the scraping pipeline defined in datapipeline.py and uploads to S3.",
    ):
        trigger_confirmation("scrape_all_websites")

    # Handle confirmation for scraping all websites
    if confirm_action(
        "scrape_all_websites",
        "scrape all websites",
        action_description="This will run the complete scraping pipeline for all configured websites and upload the content to S3.",
        warning_message="⚠️ This is a resource-intensive operation that may take a significant amount of time and consume API resources. Please ensure you want to proceed.",
        danger_level="warning",
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
            trigger_confirmation("scrape_slack_channel")

    # Handle confirmation for Slack channel scraping
    if confirm_action(
        "scrape_slack_channel",
        f"scrape the Slack channel from {start_date.strftime('%Y-%m-%d')}",
        action_description=f"This will scrape all conversations from the Slack channel starting from {start_date.strftime('%Y-%m-%d')} and upload them to S3.",
        warning_message="⚠️ This operation will access your Slack workspace and may take time depending on the amount of conversation data. Please ensure you want to proceed.",
        danger_level="warning",
    ):
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
    display_qa_pair_review_tab()


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
            except Exception as e:
                created_at_formatted = created_at
                st.error(f"Error in formatting creation date: {e}")

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
