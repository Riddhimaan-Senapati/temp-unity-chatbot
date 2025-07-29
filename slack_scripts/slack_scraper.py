import logging
import os
import boto3
from datetime import datetime, timezone
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
    """
    logger.info(
        f"Scraping channel {channel_id} for all messages since timestamp {oldest_timestamp}..."
    )

    all_messages = []
    next_cursor = None

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

    logger.info(
        f"Total parent messages fetched: {len(all_messages)}. Processing threads..."
    )
    conversations = []

    # The rest of the function processes the `all_messages` list as before.
    for msg in all_messages:
        conv = {
            "timestamp": msg.get("ts"),
            "user": msg.get("user"),
            "text": msg.get("text", ""),
            "thread_messages": [],
        }

        reply_count = msg.get("reply_count", 0)

        if msg.get("thread_ts"):
            if reply_count > 10:
                logger.warning(
                    f"Skipping thread for message {msg['ts']} because it has {reply_count} replies (more than 10)."
                )
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

    # The API returns messages from newest to oldest, so we reverse the final list
    # to get a chronological order from oldest to newest.
    return conversations[::-1]


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


def main(start_date_str=None):
    channel_id = "C04VBHU8QQN"
    # This limit is now per API call, not the total limit. 200 is a good number.
    limit_per_page = 200

    if not start_date_str:
        start_date_str = "2025-05-03"  # Format: YYYY-MM-DD
    oldest_timestamp = 0.0

    try:
        start_datetime = datetime.strptime(start_date_str, "%Y-%m-%d").replace(
            tzinfo=timezone.utc
        )
        oldest_timestamp = start_datetime.timestamp()
        logger.info(
            f"Setting scrape start date to {start_date_str}, which is Unix timestamp {oldest_timestamp}"
        )
    except ValueError:
        logger.error(
            f"Invalid date format for '{start_date_str}'. Please use YYYY-MM-DD. Scraping all messages."
        )

    # The 'limit' parameter is now named 'limit_per_page' for clarity
    conversations = scrape_channel_conversations(
        client=app.client,
        channel_id=channel_id,
        limit_per_page=limit_per_page,
        oldest_timestamp=oldest_timestamp,
    )

    if not conversations:
        logger.warning(
            f"No conversations were found in channel {channel_id} since {start_date_str}."
        )
        return

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

    logger.info(f"Scraped a total of {len(conversations)} conversations successfully.")
    # Printing details for every single conversation might be too verbose if there are many.
    # print(f"First 10 conversations:")
    # for idx, conv in enumerate(conversations[:10], 1):
    #     print(f"  Conversation {idx}: User {conv['user']}, {len(conv['thread_messages'])} thread replies found.")


if __name__ == "__main__":
    main()
