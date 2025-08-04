import logging
import os
import boto3
import json
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import time

# Load env vars
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("SCRAPPER_SLACK_BOT_TOKEN")
if not BOT_TOKEN:
    logger.critical("SCRAPPER_SLACK_BOT_TOKEN must be set")
    exit(1)

# The App object holds a client instance authenticated with the BOT_TOKEN.
app = App(token=BOT_TOKEN)


def safe_call(client: WebClient, method: str, **kwargs):
    """Wrapper to catch and wait on rate limits."""
    try:
        func = getattr(client, method)
        return func(**kwargs)
    except SlackApiError as e:
        if e.response.status_code == 429:
            delay = int(e.response.headers.get("Retry-After", 60))
            logger.warning(
                f"Rate limited on API method '{method}'; sleeping for {delay + 1} seconds."
            )
            time.sleep(delay + 1)
            return safe_call(client, method, **kwargs)
        else:
            logger.error(f"Slack API error calling '{method}': {e.response['error']}")
            return None


# Function now implements a pagination loop to fetch all messages
def scrape_channel_conversations(
    client: WebClient,
    channel_id: str,
    limit_per_page: int = 200,
    oldest_timestamp: float = 0,
):
    """
    Fetches ALL messages since `oldest_timestamp` by handling pagination,
    and gets their replies, ignoring threads with more than 10 replies.

    Returns:
        tuple: (conversations, metrics) where metrics contains scraping statistics
    """
    logger.info(
        f"Scraping channel {channel_id} for all messages since timestamp {oldest_timestamp}..."
    )

    all_messages = []
    next_cursor = None
    metrics = {
        "total_conversations": 0,
        "conversations_with_10_or_less_replies": 0,
        "conversations_scraped": 0,
        "conversations_skipped": 0,
    }

    #  Loop to handle pagination
    # Keep fetching pages as long as Slack provides a 'next_cursor'.
    while True:
        logger.info(f"Fetching page of conversations... (cursor: {next_cursor})")
        res = safe_call(
            client,
            "conversations_history",
            channel=channel_id,
            limit=limit_per_page,
            oldest=str(oldest_timestamp),
            cursor=next_cursor,  # Pass the cursor for the next page
        )

        if not res or not res.get("ok"):
            logger.error(
                "Failed to fetch conversations history page. Aborting scrape for this channel."
            )
            break

        messages_on_page = res.get("messages", [])
        all_messages.extend(messages_on_page)

        # Check if there are more pages to fetch
        if res.get("has_more") and res.get("response_metadata", {}).get("next_cursor"):
            next_cursor = res["response_metadata"]["next_cursor"]
        else:
            # No more pages, exit the loop
            break

    metrics["total_conversations"] = len(all_messages)
    logger.info(
        f"Total parent messages fetched: {len(all_messages)}. Processing threads..."
    )
    conversations = []

    # Initialize S3 client for immediate writes
    s3_client = boto3.client("s3")
    bucket = os.getenv("S3_BUCKET_NAME")

    # The rest of the function processes the `all_messages` list as before.
    for i, msg in enumerate(all_messages):
        conv = {
            "timestamp": msg.get("ts"),
            "user": msg.get("user"),
            "text": msg.get("text", ""),
            "thread_messages": [],
        }

        reply_count = msg.get("reply_count", 0)

        # Count conversations with 10 or less replies
        if reply_count <= 10:
            metrics["conversations_with_10_or_less_replies"] += 1

        if msg.get("thread_ts"):
            if reply_count > 10:
                logger.warning(
                    f"Skipping thread for message {msg['ts']} because it has {reply_count} replies (more than 10)."
                )
                metrics["conversations_skipped"] += 1
                conversations.append(conv)
                continue

            if reply_count > 0:
                tr = safe_call(
                    client,
                    "conversations_replies",
                    channel=channel_id,
                    ts=msg["thread_ts"],
                )
                thread_msgs = tr.get("messages", []) if tr else []
                for tm in thread_msgs[1:]:
                    conv["thread_messages"].append(
                        {
                            "timestamp": tm.get("ts"),
                            "user": tm.get("user"),
                            "text": tm.get("text", ""),
                        }
                    )

        conversations.append(conv)
        metrics["conversations_scraped"] += 1

        # Write to S3 after every conversation
        if bucket:
            write_conversations_to_s3(s3_client, bucket, conversations, metrics)

    # The API returns messages from newest to oldest, so we reverse the final list
    # to get a chronological order from oldest to newest.
    return conversations[::-1], metrics


def convert_to_markdown(conversations: list) -> str:
    """Converts the conversation data to a markdown string."""
    md = f"# Slack Conversations\nScraped on {datetime.now():%Y-%m-%d %H:%M:%S}\n\n"
    for idx, conv in enumerate(conversations, 1):
        md += f"## Conversation {idx}\n"
        md += f"**User:** {conv['user']} • **TS:** {datetime.fromtimestamp(float(conv['timestamp']), tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}\n\n"
        md += f"{conv['text']}\n\n"
        if conv["thread_messages"]:
            md += "### Thread replies:\n"
            for j, r in enumerate(conv["thread_messages"], 1):
                md += f"- **Reply {j}** ({r['user']}, {datetime.fromtimestamp(float(r['timestamp']), tz=timezone.utc).strftime('%H:%M:%S')}): {r['text']}\n"
        md += "\n---\n\n"
    return md


def write_conversations_to_s3(
    s3_client, bucket: str, conversations: list, metrics: dict
):
    """Write conversations to S3 immediately after each one."""
    if not bucket or not conversations:
        return

    try:
        md_content = convert_to_markdown(conversations)
        key = "slack_conversations/slack_conversations.md"

        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=md_content,
            ContentType="text/markdown",
            Metadata={
                "ScrapedDatetime": datetime.now(timezone.utc).isoformat(),
                "ConversationCount": str(len(conversations)),
            },
        )

        # Save metrics
        metrics_key = "slack_conversations/scraper_metrics.json"
        metrics_data = {
            "last_run": datetime.now(timezone.utc).isoformat(),
            "success": True,
            "metrics": metrics,
            "total_conversations_written": len(conversations),
        }

        s3_client.put_object(
            Bucket=bucket,
            Key=metrics_key,
            Body=json.dumps(metrics_data, default=str),
            ContentType="application/json",
        )

    except Exception as e:
        logger.error(f"S3 upload failed: {e}", exc_info=True)


def upload_markdown_to_s3(md_content: str, count: int, bucket: str, key: str):
    """Uploads the markdown content to S3."""
    s3 = boto3.client("s3")
    try:
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=md_content,
            ContentType="text/markdown",
            Metadata={
                "ScrapedDatetime": datetime.now(timezone.utc).isoformat(),
                "ConversationCount": str(count),
            },
        )
        logger.info(f"Successfully uploaded to s3://{bucket}/{key}")
    except Exception as e:
        logger.error(f"S3 upload failed: {e}", exc_info=True)
        raise  # Re-raise to be caught by the main function


def run_slack_conversation_scraper(start_date_str=None):
    """
    Main function to scrape Slack conversations with detailed metrics.

    Args:
        start_date_str: Start date in YYYY-MM-DD format

    Returns:
        dict: Scraping results with metrics and status
    """
    channel_id = "C04VBHU8QQN"
    limit_per_page = 200

    result = {
        "success": False,
        "start_time": datetime.now(timezone.utc),
        "end_time": None,
        "metrics": {},
        "error": None,
    }

    try:
        if not start_date_str:
            # Default to last week's data
            start_datetime = datetime.now(timezone.utc) - timedelta(days=7)
            start_date_str = start_datetime.strftime("%Y-%m-%d")
            logger.info(
                f"No start date provided, defaulting to last week: {start_date_str}"
            )
        else:
            try:
                start_datetime = datetime.strptime(start_date_str, "%Y-%m-%d").replace(
                    tzinfo=timezone.utc
                )
            except ValueError:
                logger.error(
                    f"Invalid date format for '{start_date_str}'. Please use YYYY-MM-DD. Using last week instead."
                )
                start_datetime = datetime.now(timezone.utc) - timedelta(days=7)
                start_date_str = start_datetime.strftime("%Y-%m-%d")

        oldest_timestamp = start_datetime.timestamp()
        logger.info(
            f"Setting scrape start date to {start_date_str}, which is Unix timestamp {oldest_timestamp}"
        )

        # The 'limit' parameter is now named 'limit_per_page' for clarity
        conversations, metrics = scrape_channel_conversations(
            client=app.client,
            channel_id=channel_id,
            limit_per_page=limit_per_page,
            oldest_timestamp=oldest_timestamp,
        )

        result["metrics"] = metrics

        if not conversations:
            logger.warning(
                f"No conversations were found in channel {channel_id} since {start_date_str}."
            )
            result["success"] = True
            result["end_time"] = datetime.now(timezone.utc)
            return result

        md = convert_to_markdown(conversations)

        bucket = os.getenv("S3_BUCKET_NAME")
        key = "slack_conversations/slack_conversations.md"

        if bucket:
            upload_markdown_to_s3(md, len(conversations), bucket, key)
        else:
            logger.warning(
                "S3_BUCKET_NAME not set, skipping S3 upload. Markdown content will be printed below."
            )
            print("\n--- Converted Markdown ---\n")
            print(md)

        logger.info(
            f"Scraped a total of {len(conversations)} conversations successfully."
        )
        logger.info(f"Metrics: {metrics}")

        result["success"] = True
        result["end_time"] = datetime.now(timezone.utc)
        return result

    except Exception as e:
        logger.error(f"Error in slack scraper: {str(e)}", exc_info=True)
        result["error"] = str(e)
        result["end_time"] = datetime.now(timezone.utc)
        return result


def main(start_date_str=None):
    """Legacy main function for backward compatibility."""
    result = run_slack_conversation_scraper(start_date_str)
    if not result["success"] and result["error"]:
        logger.error(f"Scraping failed: {result['error']}")
    return result


if __name__ == "__main__":
    main()
