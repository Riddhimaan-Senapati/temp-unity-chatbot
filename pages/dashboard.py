import streamlit as st
import datetime
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import os
from dotenv import load_dotenv
import pandas as pd
from utils.data_pipeline.scrape_and_upload_to_s3 import (
    run_scrape_and_upload_pipeline,
    scrape_and_upload_link,
)
from utils.feedback import display_feedback_dashboard

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
tab1, tab2, tab3 = st.tabs(
    ["User Feedback Analytics", "Data Pipeline Management", "Slack Conversations"]
)

with tab1:
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

    def run_slack_scraper_and_refresh():
        """Run the Slack scraper and refresh the dashboard"""
        st.info("Scraping Slack channel conversations...")
        with st.spinner("Scraping conversations from Slack..."):
            from slack_scraper import main as slack_scraper_main

            slack_scraper_main()
        st.success("Slack scraping complete! Refreshing dashboard...")
        st.cache_data.clear()
        st.rerun()

    # Control buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh Slack Conversations", key="refresh_slack"):
            st.cache_data.clear()
            st.rerun()
    with col2:
        if st.button("📥 Scrape Slack Channel", key="scrape_slack"):
            run_slack_scraper_and_refresh()

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
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Conversations", slack_data["conversation_count"])
        with col2:
            st.metric("Channel ID", slack_data["channel_id"])
        with col3:
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
